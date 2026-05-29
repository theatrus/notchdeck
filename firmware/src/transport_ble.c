/*
 * NotchDeck One — BLE HID-over-GATT (HOGP) transport.
 * SKELETON, modelled on the nRF Connect SDK peripheral_hids_* samples. Uses the
 * SAME report map as USB (hid_descriptor.h). One input report (ID 1, 7 B) and one
 * output report (ID 2, 7 B); boot protocol disabled (this is a joystick, not a
 * boot keyboard/mouse). Appearance = Gamepad (0x03C4).
 *
 * Reminder (spec §2): HOGP reports are referenced by report ID, so the report-ID
 * prefix is handled by the HIDS layer — the payload we send is the 7-byte body.
 */
#include "transport.h"
#include "hid_descriptor.h"

#include <zephyr/kernel.h>
#include <zephyr/bluetooth/bluetooth.h>
#include <zephyr/bluetooth/conn.h>
#include <zephyr/bluetooth/gatt.h>
#include <zephyr/bluetooth/services/bas.h>
#include <bluetooth/services/hids.h>
#include <zephyr/settings/settings.h>
#include <zephyr/logging/log.h>
#include <string.h>

LOG_MODULE_REGISTER(transport_ble, LOG_LEVEL_INF);

#define INPUT_REP_IDX   0
#define OUTPUT_REP_IDX  0

BT_HIDS_DEF(hids_obj,
	    NOTCHDECK_OUT_REPORT_SIZE,   /* output report max len */
	    NOTCHDECK_IN_REPORT_SIZE);   /* input report max len  */

static notchdeck_output_cb output_cb;
static struct bt_conn *cur_conn;

static const struct bt_data ad[] = {
	BT_DATA_BYTES(BT_DATA_FLAGS, (BT_LE_AD_GENERAL | BT_LE_AD_NO_BREDR)),
	BT_DATA_BYTES(BT_DATA_UUID16_ALL, BT_UUID_16_ENCODE(BT_UUID_HIDS_VAL),
		      BT_UUID_16_ENCODE(BT_UUID_BAS_VAL)),
	BT_DATA_BYTES(BT_DATA_GAP_APPEARANCE, 0xC4, 0x03),   /* 0x03C4 Gamepad */
};

static void output_report_handler(struct bt_hids_rep *rep, struct bt_conn *conn,
				  bool write)
{
	ARG_UNUSED(conn);
	if (write && rep->size >= NOTCHDECK_OUT_REPORT_SIZE && output_cb) {
		struct notchdeck_out_report out;

		memcpy(&out, rep->data, NOTCHDECK_OUT_REPORT_SIZE);
		output_cb(&out);
	}
}

static int hids_init(void)
{
	struct bt_hids_init_param init = {0};

	init.rep_map.data = notchdeck_hid_report_desc;
	init.rep_map.size = sizeof(notchdeck_hid_report_desc);

	init.info.bcd_hid = 0x0111;
	init.info.b_country_code = 0;
	init.info.flags = BT_HIDS_REMOTE_WAKE | BT_HIDS_NORMALLY_CONNECTABLE;

	struct bt_hids_inp_rep *in = &init.inp_rep_group_init.reports[INPUT_REP_IDX];

	in->size = NOTCHDECK_IN_REPORT_SIZE;
	in->id = NOTCHDECK_REPORT_ID_INPUT;
	init.inp_rep_group_init.cnt = 1;

	struct bt_hids_outp_feat_rep *out =
		&init.outp_rep_group_init.reports[OUTPUT_REP_IDX];

	out->size = NOTCHDECK_OUT_REPORT_SIZE;
	out->id = NOTCHDECK_REPORT_ID_OUTPUT;
	out->handler = output_report_handler;
	init.outp_rep_group_init.cnt = 1;

	init.is_mouse = false;
	init.is_kb = false;

	return bt_hids_init(&hids_obj, &init);
}

static void connected(struct bt_conn *conn, uint8_t err)
{
	if (err) {
		LOG_WRN("connect failed (0x%02x)", err);
		return;
	}
	cur_conn = bt_conn_ref(conn);
	bt_hids_connected(&hids_obj, conn);
	LOG_INF("BLE connected");
}

static void disconnected(struct bt_conn *conn, uint8_t reason)
{
	bt_hids_disconnected(&hids_obj, conn);
	if (cur_conn) {
		bt_conn_unref(cur_conn);
		cur_conn = NULL;
	}
	LOG_INF("BLE disconnected (0x%02x)", reason);
	transport_ble_start_adv();
}

BT_CONN_CB_DEFINE(conn_callbacks) = {
	.connected = connected,
	.disconnected = disconnected,
};

int transport_ble_init(notchdeck_output_cb cb)
{
	output_cb = cb;

	int err = bt_enable(NULL);

	if (err) {
		LOG_ERR("bt_enable failed (%d)", err);
		return err;
	}
	if (IS_ENABLED(CONFIG_SETTINGS)) {
		settings_load();
	}
	err = hids_init();
	if (err) {
		LOG_ERR("hids_init failed (%d)", err);
		return err;
	}
	LOG_INF("BLE HOGP up");
	return transport_ble_start_adv();
}

int transport_ble_start_adv(void)
{
	int err = bt_le_adv_start(BT_LE_ADV_CONN_FAST_2, ad, ARRAY_SIZE(ad), NULL, 0);

	if (err && err != -EALREADY) {
		LOG_ERR("adv start failed (%d)", err);
	}
	return err;
}

bool transport_ble_connected(void)
{
	return cur_conn != NULL;
}

int transport_ble_send(const struct notchdeck_in_report *rep)
{
	if (!cur_conn) {
		return -ENOTCONN;
	}
	return bt_hids_inp_rep_send(&hids_obj, cur_conn, INPUT_REP_IDX,
				    (const uint8_t *)rep, NOTCHDECK_IN_REPORT_SIZE, NULL);
}
