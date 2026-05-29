/*
 * NotchDeck One — shared HID report descriptor.
 *
 * This is the single source of truth fed to BOTH transports: the USB HID class
 * (transport_usb.c) and the BLE HID-over-GATT Report Map (transport_ble.c).
 * It is a verbatim implementation of docs/02-emulation-protocol-spec.md §1.
 *
 *   Report ID 1 (Input)   : 16 buttons + hat + 4 axes (X, Y=lever, Z, Rz)  -> 7 bytes
 *   Report ID 2 (Output)  : 8 LED-page bits + 6 vendor bytes (RGB/bright/speed/flags)
 *   Report ID 3 (Feature) : 7 vendor bytes (config/instrument)
 *
 * The power/brake lever lives on the Y axis (data byte 4 of the input payload),
 * matching the Zuiki/SDL "lever = left-stick-Y" convention.
 */
#ifndef NOTCHDECK_HID_DESCRIPTOR_H_
#define NOTCHDECK_HID_DESCRIPTOR_H_

#include <stdint.h>

#define NOTCHDECK_REPORT_ID_INPUT    0x01
#define NOTCHDECK_REPORT_ID_OUTPUT   0x02
#define NOTCHDECK_REPORT_ID_FEATURE  0x03

static const uint8_t notchdeck_hid_report_desc[] = {
	0x05, 0x01,        /* Usage Page (Generic Desktop)        */
	0x09, 0x04,        /* Usage (Joystick)                    */
	0xA1, 0x01,        /* Collection (Application)            */

	/* ---------- INPUT REPORT (ID 1) ---------- */
	0x85, NOTCHDECK_REPORT_ID_INPUT,

	/* 16 buttons */
	0x05, 0x09,        /*   Usage Page (Button)               */
	0x19, 0x01,        /*   Usage Minimum (Button 1)          */
	0x29, 0x10,        /*   Usage Maximum (Button 16)         */
	0x15, 0x00,        /*   Logical Minimum (0)               */
	0x25, 0x01,        /*   Logical Maximum (1)               */
	0x75, 0x01,        /*   Report Size (1)                   */
	0x95, 0x10,        /*   Report Count (16)                 */
	0x81, 0x02,        /*   Input (Data,Var,Abs)        2 B   */

	/* Hat switch (4-bit) + 4-bit padding */
	0x05, 0x01,        /*   Usage Page (Generic Desktop)      */
	0x09, 0x39,        /*   Usage (Hat switch)                */
	0x15, 0x00,        /*   Logical Minimum (0)               */
	0x25, 0x07,        /*   Logical Maximum (7)               */
	0x35, 0x00,        /*   Physical Minimum (0)              */
	0x46, 0x3B, 0x01,  /*   Physical Maximum (315)            */
	0x65, 0x14,        /*   Unit (Eng Rot: Degrees)           */
	0x75, 0x04,        /*   Report Size (4)                   */
	0x95, 0x01,        /*   Report Count (1)                  */
	0x81, 0x42,        /*   Input (Data,Var,Abs,Null)   0.5 B */
	0x65, 0x00,        /*   Unit (None)                       */
	0x75, 0x04,        /*   Report Size (4)                   */
	0x95, 0x01,        /*   Report Count (1)                  */
	0x81, 0x03,        /*   Input (Const,Var,Abs) pad   0.5 B */

	/* 4 axes: X, Y(=lever), Z, Rz  each 0..255 */
	0x05, 0x01,        /*   Usage Page (Generic Desktop)      */
	0x09, 0x30,        /*   Usage (X)                         */
	0x09, 0x31,        /*   Usage (Y)   <-- POWER/BRAKE LEVER  */
	0x09, 0x32,        /*   Usage (Z)   <-- reserved/reverser */
	0x09, 0x35,        /*   Usage (Rz)  <-- reserved/aux dial */
	0x15, 0x00,        /*   Logical Minimum (0)               */
	0x26, 0xFF, 0x00,  /*   Logical Maximum (255)             */
	0x75, 0x08,        /*   Report Size (8)                   */
	0x95, 0x04,        /*   Report Count (4)                  */
	0x81, 0x02,        /*   Input (Data,Var,Abs)        4 B   */

	/* ---------- OUTPUT REPORT (ID 2): LEDs / lamps ---------- */
	0x85, NOTCHDECK_REPORT_ID_OUTPUT,
	0x05, 0x08,        /*   Usage Page (LEDs)                 */
	0x19, 0x01,        /*   Usage Minimum (1)                 */
	0x29, 0x08,        /*   Usage Maximum (8)                 */
	0x75, 0x01,        /*   Report Size (1)                   */
	0x95, 0x08,        /*   Report Count (8)                  */
	0x91, 0x02,        /*   Output (Data,Var,Abs)       1 B   */
	0x06, 0x00, 0xFF,  /*   Usage Page (Vendor-Defined 0xFF00)*/
	0x09, 0x01,        /*   Usage (vendor)                    */
	0x15, 0x00,        /*   Logical Minimum (0)               */
	0x26, 0xFF, 0x00,  /*   Logical Maximum (255)             */
	0x75, 0x08,        /*   Report Size (8)                   */
	0x95, 0x06,        /*   Report Count (6)                  */
	0x91, 0x02,        /*   Output (Data,Var,Abs)       6 B   */

	/* ---------- FEATURE REPORT (ID 3): config / instrument ---------- */
	0x85, NOTCHDECK_REPORT_ID_FEATURE,
	0x06, 0x00, 0xFF,  /*   Usage Page (Vendor-Defined)       */
	0x09, 0x02,        /*   Usage (vendor)                    */
	0x75, 0x08,        /*   Report Size (8)                   */
	0x95, 0x07,        /*   Report Count (7)                  */
	0xB1, 0x02,        /*   Feature (Data,Var,Abs)      7 B   */

	0xC0               /* End Collection                      */
};

#endif /* NOTCHDECK_HID_DESCRIPTOR_H_ */
