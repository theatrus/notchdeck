/*
 * NotchDeck One — lever sensing & notch quantization.
 *
 * SKELETON. Reads a 12-bit absolute angle from an AS5600 over I2C (no external
 * driver dependency — direct register reads), then quantizes the active arc into
 * the 15 mascon notches with per-boundary hysteresis to kill chatter at detents.
 *
 * TODO(hw): set LEVER_ANGLE_MIN/MAX to the real mechanical end-stops after
 *           assembling the detented shaft + diametric magnet, and confirm the
 *           rotation direction (flip LEVER_REVERSED if EB/P5 come out swapped).
 */
#include "lever.h"

#include <zephyr/kernel.h>
#include <zephyr/device.h>
#include <zephyr/drivers/i2c.h>
#include <zephyr/logging/log.h>

LOG_MODULE_REGISTER(lever, LOG_LEVEL_INF);

/* AS5600: 7-bit address 0x36; RAW ANGLE in regs 0x0C (hi, 4 bits) / 0x0D (lo). */
#define AS5600_ADDR        0x36
#define AS5600_REG_RAWANGLE 0x0C

/* I2C bus the AS5600 hangs off — see board overlay (&i2c0 / as5600 node). */
#define LEVER_I2C_NODE     DT_NODELABEL(i2c0)
static const struct device *const i2c_dev = DEVICE_DT_GET(LEVER_I2C_NODE);

/* Active mechanical arc of the lever, in raw 12-bit AS5600 counts (0..4095). */
#define LEVER_ANGLE_MIN    200    /* TODO: measure — EB end stop */
#define LEVER_ANGLE_MAX    3900   /* TODO: measure — P5 end stop */
#define LEVER_REVERSED     0      /* set 1 if direction is inverted */

/* Hysteresis: fraction of one sector the lever must cross to switch notches. */
#define HYST_NUM           1
#define HYST_DEN           3

/* Canonical per-notch HID Y byte (spec §4). Index order matches enum. */
static const uint8_t notch_byte[NOTCH_COUNT] = {
	[NOTCH_EB] = 0x00,
	[NOTCH_B8] = 0x05, [NOTCH_B7] = 0x13, [NOTCH_B6] = 0x20, [NOTCH_B5] = 0x2E,
	[NOTCH_B4] = 0x3C, [NOTCH_B3] = 0x49, [NOTCH_B2] = 0x57, [NOTCH_B1] = 0x65,
	[NOTCH_N]  = 0x80,
	[NOTCH_P1] = 0x9F, [NOTCH_P2] = 0xB7, [NOTCH_P3] = 0xCE, [NOTCH_P4] = 0xE6,
	[NOTCH_P5] = 0xFF,
};

static enum notchdeck_notch current_notch = NOTCH_N;

uint8_t notchdeck_notch_byte(enum notchdeck_notch n)
{
	if (n < 0 || n >= NOTCH_COUNT) {
		return notch_byte[NOTCH_N];
	}
	return notch_byte[n];
}

int lever_init(void)
{
	if (!device_is_ready(i2c_dev)) {
		LOG_ERR("I2C bus not ready");
		return -ENODEV;
	}
	LOG_INF("lever ready (AS5600 @ 0x%02x)", AS5600_ADDR);
	return 0;
}

/* Read raw 12-bit angle; returns -1 on bus error. */
static int read_raw_angle(void)
{
	uint8_t buf[2];
	int err = i2c_burst_read(i2c_dev, AS5600_ADDR, AS5600_REG_RAWANGLE, buf, sizeof(buf));

	if (err) {
		return -1;
	}
	return ((int)(buf[0] & 0x0F) << 8) | buf[1];   /* 0..4095 */
}

/* Clamp + (optional) reverse + scale the raw angle into 0..(NOTCH_COUNT-1) sectors. */
static enum notchdeck_notch raw_to_notch_nominal(int raw, int *sector_lo, int *sector_hi)
{
	int span = LEVER_ANGLE_MAX - LEVER_ANGLE_MIN;

	if (span <= 0) {
		return NOTCH_N;
	}
	if (raw < LEVER_ANGLE_MIN) {
		raw = LEVER_ANGLE_MIN;
	}
	if (raw > LEVER_ANGLE_MAX) {
		raw = LEVER_ANGLE_MAX;
	}

	int pos = raw - LEVER_ANGLE_MIN;
#if LEVER_REVERSED
	pos = span - pos;
#endif

	int sector_w = span / NOTCH_COUNT;
	int idx = (sector_w > 0) ? (pos / sector_w) : NOTCH_N;

	if (idx >= NOTCH_COUNT) {
		idx = NOTCH_COUNT - 1;
	}
	if (sector_lo && sector_hi) {
		*sector_lo = LEVER_ANGLE_MIN + idx * sector_w;
		*sector_hi = *sector_lo + sector_w;
	}
	return (enum notchdeck_notch)idx;
}

enum notchdeck_notch lever_get_notch(void)
{
	int raw = read_raw_angle();

	if (raw < 0) {
		return current_notch;   /* hold last good on bus error */
	}

	int lo, hi;
	enum notchdeck_notch nominal = raw_to_notch_nominal(raw, &lo, &hi);

	if (nominal == current_notch) {
		return current_notch;
	}

	/* Require the lever to move past a hysteresis margin into the new sector
	 * before we accept the change — prevents flicker at detent boundaries. */
	int sector_w = hi - lo;
	int margin = (sector_w * HYST_NUM) / HYST_DEN;

	if (nominal > current_notch) {
		if (raw >= lo + margin) {
			current_notch = nominal;
		}
	} else { /* nominal < current_notch */
		if (raw <= hi - margin) {
			current_notch = nominal;
		}
	}
	return current_notch;
}

uint8_t lever_get_notch_byte(void)
{
	return notchdeck_notch_byte(lever_get_notch());
}
