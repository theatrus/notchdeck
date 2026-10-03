/*
 * NotchDeck One — power/brake lever: absolute angle -> discrete notch byte.
 * Notch byte values are canonical per docs/02-emulation-protocol-spec.md §4
 * (Zuiki ZKNS-001 native encoding): EB=0x00 ... N=0x80 ... P5=0xFF.
 */
#ifndef NOTCHDECK_LEVER_H_
#define NOTCHDECK_LEVER_H_

#include <stdint.h>
#include <stdbool.h>
#include "handle_decode.h"

/* Notch indices, low (full brake/EB) -> high (full power). */
enum notchdeck_notch {
	NOTCH_EB = 0,                                   /* emergency */
	NOTCH_B8, NOTCH_B7, NOTCH_B6, NOTCH_B5,
	NOTCH_B4, NOTCH_B3, NOTCH_B2, NOTCH_B1,
	NOTCH_N,                                        /* neutral */
	NOTCH_P1, NOTCH_P2, NOTCH_P3, NOTCH_P4, NOTCH_P5,
	NOTCH_COUNT                                     /* = 15 */
};

/* Initialise the lever sensor (I2C to AS5600). Returns 0 on success. */
int lever_init(void);

/* Sample once per report; getters below return the same cached sample. */
void lever_poll(void);
const struct handle_state *lever_get_state(void);
bool lever_uses_split_axes(void);
int lever_set_calibration(enum handle_role role, const struct handle_calibration *cal);

/* Read the cached combined notch index. */
enum notchdeck_notch lever_get_notch(void);

/* Convenience: the canonical HID Y-axis byte for the current notch. */
uint8_t lever_get_notch_byte(void);

/* Map a notch index to its canonical HID byte. */
uint8_t notchdeck_notch_byte(enum notchdeck_notch n);

#endif /* NOTCHDECK_LEVER_H_ */
