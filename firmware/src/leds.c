/*
 * NotchDeck One — LED / lamp subsystem.
 * SKELETON. Drives a WS2812-style strip (notch bar + status pixel) via the Zephyr
 * led_strip API over SPI, plus discrete warning lamps via GPIO. Host output
 * reports override the local lever-follow/status behavior until a timeout.
 *
 * TODO(hw): size the strip to the physical bar; map warning-lamp GPIOs;
 *           implement the host-override timeout fallback to local defaults.
 */
#include "leds.h"

#include <zephyr/kernel.h>
#include <zephyr/drivers/led_strip.h>
#include <zephyr/logging/log.h>

LOG_MODULE_REGISTER(leds, LOG_LEVEL_INF);

#define STRIP_NODE  DT_ALIAS(led_strip)

#if DT_NODE_EXISTS(STRIP_NODE)
#define STRIP_NUM_PIXELS DT_PROP(STRIP_NODE, chain_length)
static const struct device *const strip = DEVICE_DT_GET(STRIP_NODE);
static struct led_rgb pixels[STRIP_NUM_PIXELS];
#define HAVE_STRIP 1
#else
#define STRIP_NUM_PIXELS 0
#define HAVE_STRIP 0
#endif

static uint8_t g_brightness = 64;          /* default dim; host can raise */
static bool    host_owns_bar;              /* output-report flag bit0 */

int leds_init(void)
{
#if HAVE_STRIP
	if (!device_is_ready(strip)) {
		LOG_ERR("LED strip not ready");
		return -ENODEV;
	}
	memset(pixels, 0, sizeof(pixels));
	led_strip_update_rgb(strip, pixels, STRIP_NUM_PIXELS);
	LOG_INF("LED strip ready (%u px)", (unsigned)STRIP_NUM_PIXELS);
#else
	LOG_WRN("no led_strip alias — LEDs disabled");
#endif
	return 0;
}

static inline uint8_t scale(uint8_t v)
{
	return (uint8_t)(((uint16_t)v * g_brightness) / 255u);
}

void leds_show_notch(enum notchdeck_notch n)
{
#if HAVE_STRIP
	if (host_owns_bar || STRIP_NUM_PIXELS < 2) {
		return;
	}
	/* Pixel 0 reserved for status; pixels 1.. = the notch bar. Brake side
	 * amber->red toward EB, neutral a single green pip, power side green. */
	memset(&pixels[1], 0, sizeof(pixels[0]) * (STRIP_NUM_PIXELS - 1));

	int bar_px = STRIP_NUM_PIXELS - 1;
	int idx = 1 + ((int)n * (bar_px - 1)) / (NOTCH_COUNT - 1);

	if (n < NOTCH_N) {              /* braking */
		pixels[idx].r = scale(255);
		pixels[idx].g = scale(n <= NOTCH_B6 ? 0 : 96);  /* redder toward EB */
	} else if (n == NOTCH_N) {      /* neutral */
		pixels[idx].g = scale(160);
	} else {                        /* powering */
		pixels[idx].g = scale(255);
	}
	led_strip_update_rgb(strip, pixels, STRIP_NUM_PIXELS);
#else
	ARG_UNUSED(n);
#endif
}

void leds_set_link_state(enum notchdeck_link_state st)
{
#if HAVE_STRIP
	if (STRIP_NUM_PIXELS < 1) {
		return;
	}
	struct led_rgb *s = &pixels[0];
	*s = (struct led_rgb){0};
	switch (st) {
	case LINK_USB:           s->g = scale(120); s->b = scale(120); break; /* cyan */
	case LINK_BLE_ADV:       s->b = scale(200);                    break; /* blue */
	case LINK_BLE_CONNECTED: s->g = scale(200);                    break; /* green */
	case LINK_PAIRING:       s->r = s->g = s->b = scale(200);      break; /* white */
	case LINK_BATT_LOW:      s->r = scale(220); s->g = scale(90);  break; /* amber */
	}
	led_strip_update_rgb(strip, pixels, STRIP_NUM_PIXELS);
#else
	ARG_UNUSED(st);
#endif
}

void leds_apply_output(const struct notchdeck_out_report *out)
{
	g_brightness = out->brightness ? out->brightness : g_brightness;
	host_owns_bar = (out->flags & NOTCHDECK_OUT_FLAG_BAR_HOST) != 0;

	if (out->flags & NOTCHDECK_OUT_FLAG_SLEEP_LEDS) {
		g_brightness = 0;
	}

	/* TODO: drive warning lamps from out->indicators (GPIO), render out->speed
	 * onto the bar/meter, and apply the status_r/g/b override. Reset host_owns_bar
	 * after an inactivity timeout so local lever-follow resumes. */
	LOG_DBG("output: ind=0x%02x speed=%u bright=%u flags=0x%02x",
		out->indicators, out->speed, out->brightness, out->flags);
}
