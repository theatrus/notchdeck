/*
 * NotchDeck One — application entry / transport arbitration.
 * SKELETON. Picks USB when VBUS is present, otherwise BLE HOGP (spec policy:
 * "USB takes priority when connected"). Then runs the report loop at ~125 Hz.
 *
 * TODO: handle live VBUS plug/unplug to switch transports at runtime (this
 *       skeleton chooses once at boot); add battery (BAS) updates.
 */
#include "report.h"
#include "report_engine.h"
#include "transport.h"
#include "leds.h"
#include "lever.h"
#include "dfu.h"

#include <zephyr/kernel.h>
#include <zephyr/logging/log.h>
#include <hal/nrf_power.h>

LOG_MODULE_REGISTER(main, LOG_LEVEL_INF);

#define REPORT_PERIOD_MS  8   /* ~125 Hz */

enum { MODE_USB, MODE_BLE } mode;

static void on_output_report(const struct notchdeck_out_report *out)
{
	report_engine_apply_output(out);
}

static bool vbus_present(void)
{
	return nrf_power_usbregstatus_vbusdet_get(NRF_POWER);
}

int main(void)
{
	LOG_INF("NotchDeck One starting");

	leds_init();
	report_engine_init();

	/* Hold Select + Start (HID buttons 7 & 8) at power-on to drop into the
	 * USB UF2 update drive — the no-physical-reset path to firmware update. */
	{
		struct notchdeck_in_report boot;

		report_engine_build(&boot);
		if ((boot.buttons & (BIT(6) | BIT(7))) == (BIT(6) | BIT(7))) {
			notchdeck_enter_dfu();   /* does not return */
		}
	}

	if (vbus_present()) {
		mode = MODE_USB;
		transport_usb_init(on_output_report);
		leds_set_link_state(LINK_USB);
		LOG_INF("transport: USB");
	} else {
		mode = MODE_BLE;
		transport_ble_init(on_output_report);
		leds_set_link_state(LINK_BLE_ADV);
		LOG_INF("transport: BLE");
	}

	struct notchdeck_in_report rep;
	enum notchdeck_notch last_notch = NOTCH_COUNT;   /* force first paint */

	while (1) {
		report_engine_build(&rep);

		if (mode == MODE_USB) {
			if (transport_usb_ready()) {
				transport_usb_send(&rep);
			}
		} else {
			if (transport_ble_connected()) {
				transport_ble_send(&rep);
				leds_set_link_state(LINK_BLE_CONNECTED);
			}
		}

		enum notchdeck_notch n = lever_get_notch();

		if (n != last_notch) {
			leds_show_notch(n);
			last_notch = n;
		}

		k_msleep(REPORT_PERIOD_MS);
	}
	return 0;
}
