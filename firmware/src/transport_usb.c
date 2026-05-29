/*
 * NotchDeck One — USB HID transport (Zephyr legacy usb_hid class).
 * SKELETON. Sends the input report with the report-ID prefix; receives output
 * reports via the set_report callback and forwards them to the report engine.
 *
 * Note (spec §2): with report IDs in use, the on-wire buffer is
 *   [REPORT_ID][7-byte payload]. Over USB that's fine; the host parses by ID.
 */
#include "transport.h"
#include "hid_descriptor.h"

#include <zephyr/kernel.h>
#include <zephyr/usb/usb_device.h>
#include <zephyr/usb/class/usb_hid.h>
#include <zephyr/logging/log.h>
#include <string.h>

LOG_MODULE_REGISTER(transport_usb, LOG_LEVEL_INF);

static const struct device *hid_dev;
static notchdeck_output_cb output_cb;
static atomic_t ep_ready;
static atomic_t configured;

static void in_ready_cb(const struct device *dev)
{
	ARG_UNUSED(dev);
	atomic_set(&ep_ready, 1);
}

/* Host -> device output report (LEDs). Buffer includes the report ID. */
static int set_report_cb(const struct device *dev, struct usb_setup_packet *setup,
			 int32_t *len, uint8_t **data)
{
	ARG_UNUSED(dev);
	ARG_UNUSED(setup);

	uint8_t *buf = *data;

	if (*len >= 1 + (int)NOTCHDECK_OUT_REPORT_SIZE &&
	    buf[0] == NOTCHDECK_REPORT_ID_OUTPUT && output_cb) {
		struct notchdeck_out_report out;

		memcpy(&out, &buf[1], NOTCHDECK_OUT_REPORT_SIZE);
		output_cb(&out);
	}
	return 0;
}

static const struct hid_ops ops = {
	.int_in_ready = in_ready_cb,
	.set_report = set_report_cb,
};

static void status_cb(enum usb_dc_status_code status, const uint8_t *param)
{
	ARG_UNUSED(param);
	atomic_set(&configured, status == USB_DC_CONFIGURED);
}

int transport_usb_init(notchdeck_output_cb cb)
{
	output_cb = cb;

	hid_dev = device_get_binding("HID_0");
	if (!hid_dev) {
		LOG_ERR("HID_0 device not found");
		return -ENODEV;
	}

	usb_hid_register_device(hid_dev, notchdeck_hid_report_desc,
				sizeof(notchdeck_hid_report_desc), &ops);
	usb_hid_init(hid_dev);

	int err = usb_enable(status_cb);

	if (err) {
		LOG_ERR("usb_enable failed (%d)", err);
		return err;
	}
	LOG_INF("USB HID up");
	return 0;
}

bool transport_usb_ready(void)
{
	return atomic_get(&configured) && atomic_get(&ep_ready);
}

int transport_usb_send(const struct notchdeck_in_report *rep)
{
	uint8_t buf[1 + NOTCHDECK_IN_REPORT_SIZE];

	buf[0] = NOTCHDECK_REPORT_ID_INPUT;
	memcpy(&buf[1], rep, NOTCHDECK_IN_REPORT_SIZE);

	atomic_set(&ep_ready, 0);
	return hid_int_ep_write(hid_dev, buf, sizeof(buf), NULL);
}
