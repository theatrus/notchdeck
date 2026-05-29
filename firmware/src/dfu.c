/*
 * NotchDeck One — DFU entry.
 *
 * The UF2 bootloader (Adafruit nRF52 bootloader) enters mass-storage update mode
 * either on a physical double-tap of RESET (handled entirely by the bootloader),
 * or when the application writes a magic value to the retained GPREGRET register
 * and resets. This file implements the programmatic path so a button combo or a
 * host command can drop the device into the update drive.
 *
 * GPREGRET magic (Adafruit nRF52 bootloader):
 *   0x4e = serial DFU · 0xA8 = BLE OTA · 0x57 = UF2 mass-storage.
 *
 * NOTE: nrf_power_gpregret_set() signature is the modern nrfx (NCS) 3-arg form
 * (p_reg, reg_num, value). Older nrfx uses (p_reg, value).
 */
#include "dfu.h"

#include <zephyr/kernel.h>
#include <zephyr/sys/reboot.h>
#include <zephyr/logging/log.h>
#include <hal/nrf_power.h>

LOG_MODULE_REGISTER(dfu, LOG_LEVEL_INF);

#define NOTCHDECK_DFU_MAGIC_UF2  0x57

void notchdeck_enter_dfu(void)
{
	LOG_INF("entering UF2 bootloader");
	nrf_power_gpregret_set(NRF_POWER, 0, NOTCHDECK_DFU_MAGIC_UF2);
	k_msleep(50);                 /* let the log flush */
	sys_reboot(SYS_REBOOT_COLD);  /* does not return */
}
