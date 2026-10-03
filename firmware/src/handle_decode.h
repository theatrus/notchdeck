/* Sensor-independent handle decoding. Electrical Gray bits: open=1, closed=0. */
#ifndef NOTCHDECK_HANDLE_DECODE_H_
#define NOTCHDECK_HANDLE_DECODE_H_
#include <stdbool.h>
#include <stdint.h>

#define HANDLE_MAX_POSITIONS 15
#define HANDLE_ANGLE_COUNTS 4096
#define HANDLE_STALE_MS 100
#define HANDLE_DEBOUNCE_MS 16

enum handle_role { HANDLE_COMBINED, HANDLE_POWER, HANDLE_BRAKE };
enum handle_source { HANDLE_MAGNETIC, HANDLE_GRAY };

/* Centers follow physical notch order, including decreasing angles or a 0 seam.
 * Fill from measurements. count=0 deliberately means uncalibrated. */
struct handle_calibration {
    uint16_t centers[HANDLE_MAX_POSITIONS];
    uint16_t hysteresis;
    uint8_t count;
};
struct handle_filter {
    int position;
    int candidate;
    uint32_t candidate_since;
    uint32_t last_good;
    bool valid;
};
struct handle_state {
    uint8_t power;       /* 0=off, 1..5 */
    uint8_t brake;       /* 0=release, 1..8, 9=emergency */
    uint8_t combined;    /* legacy notch enum: EB=0, N=9, P5=14 */
    bool fault;
    bool armed;
};

unsigned handle_position_count(enum handle_role role);
bool handle_calibration_valid(const struct handle_calibration *cal, enum handle_role role);
int handle_gray_position(enum handle_role role, unsigned levels);
int handle_angle_position(const struct handle_calibration *cal, unsigned raw, int previous);
void handle_filter_init(struct handle_filter *filter);
void handle_filter_update(struct handle_filter *filter, int position, uint32_t now, uint32_t debounce_ms);
bool handle_filter_fresh(const struct handle_filter *filter, uint32_t now);
struct handle_state handle_resolve(bool dual, int first, int brake, bool valid, bool *armed);
uint8_t handle_axis_value(unsigned position, unsigned maximum);
uint8_t handle_mux_mask(unsigned channel);
#endif
