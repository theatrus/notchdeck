#include "handle_decode.h"
#include <assert.h>
#include <stdio.h>

static void check_gray(void)
{
    for (int role = HANDLE_COMBINED; role <= HANDLE_BRAKE; role++) {
        unsigned count = handle_position_count(role);
        unsigned codes[HANDLE_MAX_POSITIONS] = {0};
        unsigned found = 0;
        for (unsigned code = 0; code < 32; code++) {
            int pos = handle_gray_position(role, code);
            if (pos >= 0) { assert((unsigned)pos < count); codes[pos] = code; found++; }
        }
        assert(found == count);
        assert(handle_gray_position(role, role == HANDLE_POWER ? 7 : 15) == -1);
        for (unsigned i = 1; i < count; i++) {
            unsigned changed = codes[i] ^ codes[i-1];
            assert(changed && !(changed & (changed - 1)));
        }
    }
    /* Known electrical fixtures: open=1, grounded contact=0. */
    assert(handle_gray_position(HANDLE_POWER, 1) == 0);
    assert(handle_gray_position(HANDLE_POWER, 5) == 5);
    assert(handle_gray_position(HANDLE_BRAKE, 0) == 0);
    assert(handle_gray_position(HANDLE_BRAKE, 13) == 9);
    assert(handle_gray_position(HANDLE_COMBINED, 6) == 9);
    assert(handle_gray_position(HANDLE_COMBINED, 14) == 0);
    assert(handle_gray_position(99, 0) == -1);
}

static void check_angles(void)
{
    struct handle_calibration c = {.centers={4000,104,304,504,704,904}, .hysteresis=10, .count=6};
    assert(handle_calibration_valid(&c, HANDLE_POWER));
    assert(!handle_calibration_valid(&c, HANDLE_BRAKE));
    assert(handle_angle_position(&c, 4095, -1) == 0);
    assert(handle_angle_position(&c, 5, -1) == 1);
    assert(handle_angle_position(&c, 210, 1) == 1); /* below midpoint + hysteresis */
    assert(handle_angle_position(&c, 215, 1) == 2);
    assert(handle_angle_position(&c, 198, 2) == 2);
    assert(handle_angle_position(&c, 193, 2) == 1);
    for (unsigned i = 0; i < 6; i++) assert(handle_angle_position(&c, c.centers[i], -1) == (int)i);
    /* Reversed shaft direction remains a valid measured calibration. */
    for (unsigned i = 0; i < 3; i++) {
        unsigned t = c.centers[i]; c.centers[i] = c.centers[5-i]; c.centers[5-i] = t;
    }
    assert(handle_calibration_valid(&c, HANDLE_POWER));
    assert(handle_angle_position(&c, 4000, -1) == 5);
    assert(handle_angle_position(&c, 4096, -1) == -1);
    c.centers[1] = c.centers[0]; assert(!handle_calibration_valid(&c, HANDLE_POWER));
    c.count = 0; assert(handle_angle_position(&c, 0, -1) == -1);
    assert(!handle_calibration_valid(&c, HANDLE_POWER));
}

static void check_filters(void)
{
    struct handle_filter f;
    handle_filter_init(&f);
    assert(!handle_filter_fresh(&f, 0));
    handle_filter_update(&f, 0, 0, 16);
    handle_filter_update(&f, 0, 15, 16); assert(!f.valid);
    handle_filter_update(&f, 0, 16, 16); assert(f.valid && f.position == 0);
    handle_filter_update(&f, 1, 20, 16);
    handle_filter_update(&f, 0, 24, 16);
    handle_filter_update(&f, 1, 28, 16);
    handle_filter_update(&f, 1, 43, 16); assert(f.position == 0);
    handle_filter_update(&f, 1, 44, 16); assert(f.position == 1);
    handle_filter_update(&f, -1, 45, 16); /* unplug, keep last value only briefly */
    assert(handle_filter_fresh(&f, 143));
    assert(!handle_filter_fresh(&f, 144));
    /* Invalid samples break the debounce window. */
    handle_filter_update(&f, 2, 150, 16);
    handle_filter_update(&f, -1, 155, 16);
    handle_filter_update(&f, 2, 166, 16); assert(f.position == 1);
    handle_filter_update(&f, 2, 182, 16); assert(f.position == 2);
    /* Stable timer behavior across uptime wrap. */
    handle_filter_init(&f);
    handle_filter_update(&f, 3, UINT32_MAX-7, 16);
    handle_filter_update(&f, 3, 8, 16); assert(f.position == 3);
    assert(handle_filter_fresh(&f, 107)); assert(!handle_filter_fresh(&f, 108));
    handle_filter_update(&f, 4, 109, 0); assert(f.position == 4);
}

static void check_outputs(void)
{
    bool armed = false;
    struct handle_state s = handle_resolve(true, 5, 0, true, &armed);
    assert(!s.fault && !s.armed && !s.power); /* cannot start at power */
    s = handle_resolve(true, 0, 0, true, &armed); assert(s.armed);
    for (int p = 0; p <= 5; p++) for (int b = 0; b <= 9; b++) {
        s = handle_resolve(true, p, b, true, &armed);
        assert(s.power == (b ? 0 : p)); assert(s.brake == b);
        assert(s.combined == (b ? 9-b : 9+p));
    }
    s = handle_resolve(true, 5, 0, false, &armed);
    assert(s.fault && !s.power && s.brake == 9 && !armed);
    s = handle_resolve(true, 5, 0, true, &armed); assert(!s.power && !armed);
    handle_resolve(true, 0, 0, true, &armed);
    s = handle_resolve(true, 5, 0, true, &armed); assert(s.power == 5);
    s = handle_resolve(true, 6, 0, true, &armed); assert(s.fault && !armed);
    s = handle_resolve(true, 0, 10, true, &armed); assert(s.fault);
    handle_resolve(false, 9, 0, true, &armed);
    for (int n = 0; n < 15; n++) {
        s = handle_resolve(false, n, 0, true, &armed); assert(s.combined == n);
    }
    assert(handle_axis_value(0, 5) == 0 && handle_axis_value(5, 5) == 255);
    assert(handle_axis_value(9, 9) == 255 && handle_axis_value(1, 5) == 51);
    assert(handle_mux_mask(0) == 1 && handle_mux_mask(1) == 2 && handle_mux_mask(2) == 0);
}

int main(void)
{
    check_gray(); check_angles(); check_filters(); check_outputs();
    puts("PASS: Gray cams, magnetic calibration/wrap/hysteresis, debounce/staleness, brake priority and re-arm");
}
