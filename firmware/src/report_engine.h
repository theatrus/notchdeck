/*
 * NotchDeck One — report engine: gather inputs into the HID input report, and
 * apply host output reports to the LED subsystem. Transport-agnostic.
 */
#ifndef NOTCHDECK_REPORT_ENGINE_H_
#define NOTCHDECK_REPORT_ENGINE_H_

#include "report.h"

/* Initialise inputs (lever + buttons). Returns 0 on success. */
int report_engine_init(void);

/* Populate *rep with the current lever notch, buttons and hat. */
void report_engine_build(struct notchdeck_in_report *rep);

/* Apply a host-sent output report (LEDs/lamps/instrument). */
void report_engine_apply_output(const struct notchdeck_out_report *out);

#endif /* NOTCHDECK_REPORT_ENGINE_H_ */
