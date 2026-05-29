/*
 * NotchDeck One — packed report structs and field helpers.
 * Layout matches docs/02-emulation-protocol-spec.md §2 (input) and §5 (output).
 * These are the report PAYLOADS (no report-ID prefix); transports prepend the
 * report ID where their wire format requires it.
 */
#ifndef NOTCHDECK_REPORT_H_
#define NOTCHDECK_REPORT_H_

#include <stdint.h>

/* --- Hat (D-pad) encoded values --- */
#define NOTCHDECK_HAT_N        0
#define NOTCHDECK_HAT_NE       1
#define NOTCHDECK_HAT_E        2
#define NOTCHDECK_HAT_SE       3
#define NOTCHDECK_HAT_S        4
#define NOTCHDECK_HAT_SW       5
#define NOTCHDECK_HAT_W        6
#define NOTCHDECK_HAT_NW       7
#define NOTCHDECK_HAT_CENTER   0x0F   /* null state */

#define NOTCHDECK_AXIS_CENTER  0x80   /* neutral for reserved X/Z/Rz axes */

/* Input report payload: 7 bytes. buttons is little-endian (byte0 = buttons 1-8). */
struct __attribute__((packed)) notchdeck_in_report {
	uint16_t buttons;   /* bit0 = button 1 ... bit15 = button 16 */
	uint8_t  hat;       /* low nibble = direction (see NOTCHDECK_HAT_*), high nibble pad */
	uint8_t  x;         /* reserved, NOTCHDECK_AXIS_CENTER */
	uint8_t  y;         /* POWER/BRAKE LEVER notch byte (see lever.h) */
	uint8_t  z;         /* reserved (reverser), NOTCHDECK_AXIS_CENTER */
	uint8_t  rz;        /* reserved (aux dial),  NOTCHDECK_AXIS_CENTER */
};

/* Output report payload: 7 bytes (LEDs / lamps / instrument). */
struct __attribute__((packed)) notchdeck_out_report {
	uint8_t indicators; /* bit0 ATS · bit1 door-open · bit2 EB/buzzer · bit3 overspeed */
	uint8_t status_r;   /* RGB status LED override (R) — active while any of RGB != 0 */
	uint8_t status_g;
	uint8_t status_b;
	uint8_t brightness; /* global LED brightness 0..255 */
	uint8_t speed;      /* host-pushed train speed, 0..255 -> meter/bargraph */
	uint8_t flags;      /* bit0 notch-bar follow-host · bit1 sleep-LEDs · bit2 demo */
};

#define NOTCHDECK_IN_REPORT_SIZE   sizeof(struct notchdeck_in_report)   /* 7 */
#define NOTCHDECK_OUT_REPORT_SIZE  sizeof(struct notchdeck_out_report)  /* 7 */

/* Output-report flag bits */
#define NOTCHDECK_OUT_FLAG_BAR_HOST   (1u << 0)
#define NOTCHDECK_OUT_FLAG_SLEEP_LEDS (1u << 1)
#define NOTCHDECK_OUT_FLAG_DEMO       (1u << 2)

#endif /* NOTCHDECK_REPORT_H_ */
