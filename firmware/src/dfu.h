/*
 * NotchDeck One — enter the USB UF2 bootloader (firmware update mode).
 * See docs/05-firmware-update.md.
 */
#ifndef NOTCHDECK_DFU_H_
#define NOTCHDECK_DFU_H_

/* Reboot into the UF2 bootloader's mass-storage update mode. Does not return. */
void notchdeck_enter_dfu(void);

#endif /* NOTCHDECK_DFU_H_ */
