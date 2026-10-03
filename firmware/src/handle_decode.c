#include "handle_decode.h"
#include <stddef.h>

/* Non-wrapping physical cams. Adjacent detents differ by exactly one bit.
 * All-open is reserved, so an unplugged harness cannot command power. */
static const uint8_t combined_codes[] = {14,10,11,9,8,0,1,3,2,6,7,5,4,12,13};
static const uint8_t power_codes[] = {1,3,2,6,4,5};
static const uint8_t brake_codes[] = {0,1,3,2,6,7,5,4,12,13};

unsigned handle_position_count(enum handle_role role)
{
    switch (role) {
    case HANDLE_COMBINED: return 15;
    case HANDLE_POWER: return 6;
    case HANDLE_BRAKE: return 10;
    default: return 0;
    }
}

static unsigned distance(unsigned a, unsigned b)
{
    unsigned d = a > b ? a - b : b - a;
    return d > HANDLE_ANGLE_COUNTS / 2 ? HANDLE_ANGLE_COUNTS - d : d;
}

bool handle_calibration_valid(const struct handle_calibration *cal, enum handle_role role)
{
    unsigned count = handle_position_count(role);
    if (!cal || !count || cal->count != count || cal->hysteresis >= HANDLE_ANGLE_COUNTS / 2) return false;
    for (unsigned i = 0; i < count; i++) {
        if (cal->centers[i] >= HANDLE_ANGLE_COUNTS) return false;
        for (unsigned j = 0; j < i; j++) {
            if (distance(cal->centers[i], cal->centers[j]) <= 2u * cal->hysteresis) return false;
        }
    }
    return true;
}

int handle_gray_position(enum handle_role role, unsigned levels)
{
    const uint8_t *codes;
    switch (role) {
    case HANDLE_COMBINED: codes = combined_codes; break;
    case HANDLE_POWER: codes = power_codes; break;
    case HANDLE_BRAKE: codes = brake_codes; break;
    default: return -1;
    }
    for (unsigned i = 0; i < handle_position_count(role); i++) {
        if (codes[i] == levels) return (int)i;
    }
    return -1;
}

int handle_angle_position(const struct handle_calibration *cal, unsigned raw, int previous)
{
    if (!cal || !cal->count || cal->count > HANDLE_MAX_POSITIONS || raw >= HANDLE_ANGLE_COUNTS) return -1;
    unsigned nearest = 0;
    unsigned best = HANDLE_ANGLE_COUNTS;
    for (unsigned i = 0; i < cal->count; i++) {
        if (cal->centers[i] >= HANDLE_ANGLE_COUNTS) return -1;
        unsigned d = distance(raw, cal->centers[i]);
        if (d < best) { best = d; nearest = i; }
    }
    if (previous >= 0 && previous < cal->count &&
        distance(raw, cal->centers[previous]) <= best + 2u * cal->hysteresis) return previous;
    return (int)nearest;
}

void handle_filter_init(struct handle_filter *f)
{
    *f = (struct handle_filter){.position = -1, .candidate = -1};
}

void handle_filter_update(struct handle_filter *f, int position, uint32_t now, uint32_t debounce_ms)
{
    if (position < 0) { f->candidate = -1; return; }
    if (position != f->candidate) {
        f->candidate = position;
        f->candidate_since = now;
    }
    if (f->valid && position == f->position) f->last_good = now;
    if ((uint32_t)(now - f->candidate_since) >= debounce_ms) {
        f->position = position;
        f->last_good = now;
        f->valid = true;
    }
}

bool handle_filter_fresh(const struct handle_filter *f, uint32_t now)
{
    return f->valid && (uint32_t)(now - f->last_good) < HANDLE_STALE_MS;
}

struct handle_state handle_resolve(bool dual, int first, int brake, bool valid, bool *armed)
{
    struct handle_state s = {0};
    if (!valid || first < 0 || first >= (dual ? 6 : 15) || (dual && (brake < 0 || brake >= 10))) {
        *armed = false;
        return (struct handle_state){.brake = 9, .combined = 0, .fault = true};
    }
    s.power = dual ? first : (first > 9 ? first - 9 : 0);
    s.brake = dual ? brake : (first < 9 ? 9 - first : 0);
    if (!s.power && !s.brake) *armed = true;
    if (!*armed || s.brake) s.power = 0;
    s.combined = s.brake ? 9 - s.brake : 9 + s.power;
    s.armed = *armed;
    return s;
}

uint8_t handle_axis_value(unsigned position, unsigned maximum)
{
    if (!maximum) return 0;
    if (position > maximum) position = maximum;
    return (uint8_t)((position * 255u + maximum / 2u) / maximum);
}

uint8_t handle_mux_mask(unsigned channel)
{
    return channel < 2 ? (uint8_t)(1u << channel) : 0;
}
