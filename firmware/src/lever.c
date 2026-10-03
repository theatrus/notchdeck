/* Independent sensor backends, shared notch processing; Rev C/D MCU pinout in overlay. */
#include "lever.h"
#include "handle_calibration.h"
#include <errno.h>
#include <zephyr/kernel.h>
#include <zephyr/device.h>
#include <zephyr/drivers/i2c.h>
#include <zephyr/drivers/gpio.h>
#include <zephyr/logging/log.h>
LOG_MODULE_REGISTER(lever, LOG_LEVEL_INF);

#define AS5600_ADDR 0x36
#define AS5600_STATUS 0x0B
#define HANDLE_MUX_ADDR 0x70
static const struct device *const i2c_dev = DEVICE_DT_GET(DT_NODELABEL(i2c0));
static struct handle_filter first_filter, brake_filter;
static struct handle_calibration first_cal, brake_cal;
static struct handle_state state = {.brake = 9, .combined = NOTCH_EB, .fault = true};
static bool armed;
static bool initialized;
static bool use_dual = IS_ENABLED(CONFIG_NOTCHDECK_DUAL_HANDLES);
static bool first_gray;
static bool brake_gray = IS_ENABLED(CONFIG_NOTCHDECK_BRAKE_GRAY);

#if defined(CONFIG_NOTCHDECK_REV_C)
#define INPUT_SPEC(name) GPIO_DT_SPEC_GET(DT_NODELABEL(name), gpios)
static const struct gpio_dt_spec brake_bits[] = {
    INPUT_SPEC(brake_s0), INPUT_SPEC(brake_s1), INPUT_SPEC(brake_s2), INPUT_SPEC(brake_s3)
};
static const struct gpio_dt_spec power_bits[] = {
    INPUT_SPEC(power_s0), INPUT_SPEC(power_s1), INPUT_SPEC(power_s2)
};
static int setup_bits(const struct gpio_dt_spec *bits, size_t count)
{
    for (size_t i = 0; i < count; i++) {
        if (!gpio_is_ready_dt(&bits[i])) return -ENODEV;
        int err = gpio_pin_configure_dt(&bits[i], GPIO_INPUT);
        if (err) return err;
    }
    return 0;
}
static int read_gray(bool power)
{
    const struct gpio_dt_spec *bits = power ? power_bits : brake_bits;
    size_t count = power ? ARRAY_SIZE(power_bits) : ARRAY_SIZE(brake_bits);
    unsigned levels = 0;
    for (size_t i = 0; i < count; i++) {
        /* Read actual voltage levels. Do not invert contact closure. */
        int level = gpio_pin_get_raw(bits[i].port, bits[i].pin);
        if (level < 0) return -1;
        levels |= (unsigned)level << i;
    }
    return handle_gray_position(power ? HANDLE_POWER : (use_dual ? HANDLE_BRAKE : HANDLE_COMBINED), levels);
}
#else
static int read_gray(bool power) { ARG_UNUSED(power); return -1; }
#endif

static int read_angle(unsigned channel)
{
    if (!device_is_ready(i2c_dev)) return -1;
    if (IS_ENABLED(CONFIG_NOTCHDECK_REV_C)) {
        uint8_t mask = handle_mux_mask(channel);
        if (!mask || i2c_write(i2c_dev, &mask, 1, HANDLE_MUX_ADDR)) return -1;
    }
    /* STATUS, RAW_ANGLE_H, RAW_ANGLE_L. Reject no magnet, weak or strong field. */
    uint8_t bytes[3];
    int err = i2c_burst_read(i2c_dev, AS5600_ADDR, AS5600_STATUS, bytes, sizeof(bytes));
    if (IS_ENABLED(CONFIG_NOTCHDECK_REV_C)) {
        uint8_t off = 0;
        int deselect = i2c_write(i2c_dev, &off, 1, HANDLE_MUX_ADDR);
        if (deselect) return -1;
    }
    if (err || (bytes[0] & 0x38) != 0x20) return -1;
    return ((bytes[1] & 0x0F) << 8) | bytes[2];
}

int lever_set_calibration(enum handle_role role, const struct handle_calibration *cal)
{
    if (!handle_calibration_valid(cal, role)) return -EINVAL;
    if ((!use_dual && role == HANDLE_COMBINED) || (use_dual && role == HANDLE_POWER)) {
        first_cal = *cal;
        handle_filter_init(&first_filter);
    } else if (use_dual && role == HANDLE_BRAKE) {
        brake_cal = *cal;
        handle_filter_init(&brake_filter);
    } else return -EINVAL;
    armed = false;
    state = (struct handle_state){.brake = 9, .combined = NOTCH_EB, .fault = true};
    return 0;
}

int lever_init(void)
{
    first_gray = use_dual ? IS_ENABLED(CONFIG_NOTCHDECK_POWER_GRAY) : IS_ENABLED(CONFIG_NOTCHDECK_COMBINED_GRAY);
    first_cal = use_dual ? power_calibration : combined_calibration;
    brake_cal = brake_calibration;
    handle_filter_init(&first_filter);
    handle_filter_init(&brake_filter);
    armed = false;
    state = (struct handle_state){.brake = 9, .combined = NOTCH_EB, .fault = true};
    initialized = false;
#if defined(CONFIG_NOTCHDECK_REV_C)
    int err;
    if ((use_dual && brake_gray) || (!use_dual && first_gray)) {
        err = setup_bits(brake_bits, ARRAY_SIZE(brake_bits));
        if (err) return err;
    }
    if (use_dual && first_gray) {
        err = setup_bits(power_bits, ARRAY_SIZE(power_bits));
        if (err) return err;
    }
#endif
    bool magnetic = !first_gray || (use_dual && !brake_gray);
    if (magnetic && !device_is_ready(i2c_dev)) return -ENODEV;
    if (magnetic && IS_ENABLED(CONFIG_NOTCHDECK_REV_C)) {
        uint8_t off = 0;
        int err = i2c_write(i2c_dev, &off, 1, HANDLE_MUX_ADDR);
        if (err) return err;
    }
    initialized = true;
    LOG_INF("handles: %s; first=%s brake=%s", use_dual ? "dual" : "combined",
            first_gray ? "Gray" : "magnetic", use_dual ? (brake_gray ? "Gray" : "magnetic") : "unused");
    if ((!first_gray && !handle_calibration_valid(&first_cal, use_dual ? HANDLE_POWER : HANDLE_COMBINED)) ||
        (use_dual && !brake_gray && !handle_calibration_valid(&brake_cal, HANDLE_BRAKE))) {
        LOG_WRN("magnetic detent calibration required before enabling handle output");
    }
    return 0;
}

static void poll_one(struct handle_filter *filter, bool gray, enum handle_role role,
                     unsigned channel, const struct handle_calibration *cal, uint32_t now)
{
    int position = -1;
    if (gray) position = read_gray(role == HANDLE_POWER);
    else if (handle_calibration_valid(cal, role)) {
        int raw = read_angle(channel);
        if (raw >= 0) position = handle_angle_position(cal, (unsigned)raw, filter->valid ? filter->position : -1);
    }
    handle_filter_update(filter, position, now, gray ? HANDLE_DEBOUNCE_MS : 0);
}

void lever_poll(void)
{
    uint32_t now = k_uptime_get_32();
    if (initialized) {
        poll_one(&first_filter, first_gray, use_dual ? HANDLE_POWER : HANDLE_COMBINED, 0, &first_cal, now);
        if (use_dual) poll_one(&brake_filter, brake_gray, HANDLE_BRAKE, 1, &brake_cal, now);
    }
    bool valid = initialized && handle_filter_fresh(&first_filter, now) &&
                 (!use_dual || handle_filter_fresh(&brake_filter, now));
    state = handle_resolve(use_dual, first_filter.position, brake_filter.position, valid, &armed);
}

const struct handle_state *lever_get_state(void) { return &state; }
bool lever_uses_split_axes(void) { return use_dual && IS_ENABLED(CONFIG_NOTCHDECK_SPLIT_AXES); }
enum notchdeck_notch lever_get_notch(void) { return (enum notchdeck_notch)state.combined; }
uint8_t notchdeck_notch_byte(enum notchdeck_notch n)
{
    static const uint8_t bytes[NOTCH_COUNT] = {0x00,0x05,0x13,0x20,0x2E,0x3C,0x49,0x57,0x65,0x80,0x9F,0xB7,0xCE,0xE6,0xFF};
    return bytes[n >= 0 && n < NOTCH_COUNT ? n : NOTCH_N];
}
uint8_t lever_get_notch_byte(void) { return notchdeck_notch_byte(lever_get_notch()); }
