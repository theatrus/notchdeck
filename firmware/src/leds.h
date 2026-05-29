/*
 * NotchDeck One — LED / lamp subsystem (notch bar + status RGB + warning lamps).
 * Local default lighting (lever-follow + connection/battery status) unless a host
 * output report takes over. See docs/02-emulation-protocol-spec.md §7.
 */
#ifndef NOTCHDECK_LEDS_H_
#define NOTCHDECK_LEDS_H_

#include "report.h"
#include "lever.h"

enum notchdeck_link_state {
	LINK_USB,           /* USB attached / enumerated  */
	LINK_BLE_ADV,       /* BLE advertising            */
	LINK_BLE_CONNECTED, /* BLE connected              */
	LINK_PAIRING,       /* BLE pairing                */
	LINK_BATT_LOW,      /* low battery warning        */
};

int  leds_init(void);

/* Local default: paint the notch bar from the current lever position. */
void leds_show_notch(enum notchdeck_notch n);

/* Local default: status RGB reflects link/power state. */
void leds_set_link_state(enum notchdeck_link_state st);

/* Host override: apply a received output report. Takes priority until timeout. */
void leds_apply_output(const struct notchdeck_out_report *out);

#endif /* NOTCHDECK_LEDS_H_ */
