/*
 * NotchDeck One — report engine.
 * SKELETON. Buttons are scanned from a "buttons" gpio-keys node (see overlay).
 * Mapping of physical buttons -> HID button index follows spec §3.
 */
#include "report_engine.h"
#include "lever.h"
#include "leds.h"

#include <zephyr/kernel.h>
#include <zephyr/drivers/gpio.h>
#include <zephyr/logging/log.h>

LOG_MODULE_REGISTER(report_engine, LOG_LEVEL_INF);

/* Buttons: a "buttons" gpio-keys node; each child = one HID button, in DT order
 * (first child -> HID button 1, etc.). See the board overlay. */
#define BUTTONS_NODE DT_NODELABEL(buttons)

#if DT_NODE_EXISTS(BUTTONS_NODE)
#define BTN_SPEC(node_id) GPIO_DT_SPEC_GET(node_id, gpios),
static const struct gpio_dt_spec buttons[] = {
	DT_FOREACH_CHILD_STATUS_OKAY(BUTTONS_NODE, BTN_SPEC)
};
#define NUM_BUTTONS ARRAY_SIZE(buttons)
#else
static const struct gpio_dt_spec buttons[] = {};
#define NUM_BUTTONS 0
#endif

int report_engine_init(void)
{
	int err = lever_init();

	if (err) {
		LOG_WRN("lever_init failed (%d) — lever will read neutral", err);
	}

	for (size_t i = 0; i < NUM_BUTTONS; i++) {
		if (!gpio_is_ready_dt(&buttons[i])) {
			LOG_ERR("button %u gpio not ready", (unsigned)i);
			continue;
		}
		gpio_pin_configure_dt(&buttons[i], GPIO_INPUT);
	}
	LOG_INF("report engine ready (%u buttons)", (unsigned)NUM_BUTTONS);
	return 0;
}

void report_engine_build(struct notchdeck_in_report *rep)
{
	rep->buttons = 0;
	for (size_t i = 0; i < NUM_BUTTONS && i < 16; i++) {
		if (gpio_pin_get_dt(&buttons[i]) > 0) {
			rep->buttons |= (uint16_t)(1u << i);
		}
	}

	/* TODO(hw): scan the 4/5-way nav switch into rep->hat. */
	rep->hat = NOTCHDECK_HAT_CENTER;

	rep->x  = NOTCHDECK_AXIS_CENTER;
	rep->y  = lever_get_notch_byte();   /* the load-bearing input */
	rep->z  = NOTCHDECK_AXIS_CENTER;    /* TODO(hw): reverser */
	rep->rz = NOTCHDECK_AXIS_CENTER;
}

void report_engine_apply_output(const struct notchdeck_out_report *out)
{
	leds_apply_output(out);
}
