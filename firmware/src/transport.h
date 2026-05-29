/*
 * NotchDeck One — transport interface shared by USB HID and BLE HOGP.
 * Both transports consume the same HID report descriptor (hid_descriptor.h)
 * and the same report payloads (report.h). main.c arbitrates which is active.
 */
#ifndef NOTCHDECK_TRANSPORT_H_
#define NOTCHDECK_TRANSPORT_H_

#include "report.h"
#include <stdbool.h>

/* Called when a host writes an Output report (LEDs/lamps). */
typedef void (*notchdeck_output_cb)(const struct notchdeck_out_report *out);

/* USB */
int  transport_usb_init(notchdeck_output_cb cb);
bool transport_usb_ready(void);                                  /* enumerated + IN ep ready */
int  transport_usb_send(const struct notchdeck_in_report *rep);

/* BLE (HID over GATT) */
int  transport_ble_init(notchdeck_output_cb cb);
int  transport_ble_start_adv(void);
bool transport_ble_connected(void);
int  transport_ble_send(const struct notchdeck_in_report *rep);

#endif /* NOTCHDECK_TRANSPORT_H_ */
