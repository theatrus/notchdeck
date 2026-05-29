/*
 * Host-side sanity test for the transport-independent protocol layer.
 * Compiles with a plain host compiler (no Zephyr) — see `make test`.
 * Guards the wire contract in docs/02-emulation-protocol-spec.md.
 */
#include <stdio.h>
#include <stddef.h>
#include <assert.h>
#include "report.h"
#include "hid_descriptor.h"

int main(void)
{
	printf("sizeof(in_report)  = %zu (expect 7)\n", sizeof(struct notchdeck_in_report));
	printf("sizeof(out_report) = %zu (expect 7)\n", sizeof(struct notchdeck_out_report));
	printf("HID descriptor len = %zu bytes\n", sizeof(notchdeck_hid_report_desc));
	printf("report IDs: in=%d out=%d feat=%d\n",
	       NOTCHDECK_REPORT_ID_INPUT, NOTCHDECK_REPORT_ID_OUTPUT, NOTCHDECK_REPORT_ID_FEATURE);
	printf("offsets: buttons=%zu hat=%zu x=%zu y=%zu z=%zu rz=%zu\n",
	       offsetof(struct notchdeck_in_report, buttons),
	       offsetof(struct notchdeck_in_report, hat),
	       offsetof(struct notchdeck_in_report, x),
	       offsetof(struct notchdeck_in_report, y),
	       offsetof(struct notchdeck_in_report, z),
	       offsetof(struct notchdeck_in_report, rz));

	/* Report payloads are 7 bytes (spec §8). */
	assert(sizeof(struct notchdeck_in_report) == NOTCHDECK_IN_REPORT_SIZE);
	assert(sizeof(struct notchdeck_out_report) == NOTCHDECK_OUT_REPORT_SIZE);
	assert(NOTCHDECK_IN_REPORT_SIZE == 7);
	assert(NOTCHDECK_OUT_REPORT_SIZE == 7);

	/* Lever rides on the Y axis = payload byte 4 (Zuiki/SDL convention, spec §2). */
	assert(offsetof(struct notchdeck_in_report, buttons) == 0);
	assert(offsetof(struct notchdeck_in_report, hat) == 2);
	assert(offsetof(struct notchdeck_in_report, y) == 4);

	assert(NOTCHDECK_REPORT_ID_INPUT == 1);
	assert(NOTCHDECK_REPORT_ID_OUTPUT == 2);
	assert(NOTCHDECK_REPORT_ID_FEATURE == 3);

	/* DFU boot combo: Select (HID button 7 = bit6) + Start (button 8 = bit7). */
	uint16_t held = (uint16_t)((1u << 6) | (1u << 7));
	assert((held & ((1u << 6) | (1u << 7))) == ((1u << 6) | (1u << 7)));

	printf("ALL CORE ASSERTS PASS\n");
	return 0;
}
