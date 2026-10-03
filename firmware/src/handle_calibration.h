/* Replace with measured detent centers, or load via lever_set_calibration().
 * Deliberately empty: fabricated numbers must not command power on first boot.
 * Centers are AS5600 RAW_ANGLE counts (0..4095), listed in notch order:
 * combined EB,B8..B1,N,P1..P5; power Off,P1..P5; brake Release,B1..B8,EB.
 * Choose hysteresis well below half the closest center spacing. */
#ifndef NOTCHDECK_HANDLE_CALIBRATION_H_
#define NOTCHDECK_HANDLE_CALIBRATION_H_
#include "handle_decode.h"
static const struct handle_calibration combined_calibration = {0};
static const struct handle_calibration power_calibration = {0};
static const struct handle_calibration brake_calibration = {0};
#endif
