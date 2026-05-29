# NotchDeck One firmware — Makefile (wraps nRF Connect SDK / west)
#
# Targets:
#   make build         west build for $(BOARD)
#   make flash         build + flash over SWD (J-Link / CMSIS-DAP)
#   make uf2           build + show the drag-and-drop .uf2 artifact
#   make release       build + copy versioned .uf2/.hex into dist/
#   make menuconfig    open Kconfig UI for the current build
#   make clean         remove build/ and dist/
#   make help          this text
#
# Requires the nRF Connect SDK toolchain on PATH (west + Zephyr SDK).
# Override the target: `make build BOARD=<your_board>`.

WEST      ?= west
HOSTCC    ?= cc
BOARD     ?= nrf52840dk/nrf52840
BUILD     ?= build
APP       := notchdeck-one

# Version from the Zephyr VERSION file (also drives app_version.h).
VER := $(shell awk -F'= ' '/^VERSION_MAJOR/{a=$$2} /^VERSION_MINOR/{b=$$2} /^PATCHLEVEL/{c=$$2} END{printf "%s.%s.%s",a,b,c}' VERSION)

.PHONY: help build flash uf2 release menuconfig clean test

help:
	@echo "NotchDeck One firmware (v$(VER)) — board: $(BOARD)"
	@echo ""
	@echo "  make test        host unit test (no Zephyr toolchain needed)"
	@echo "  make build       west build"
	@echo "  make flash       build + flash via SWD"
	@echo "  make uf2         build + locate the .uf2 (drag-and-drop update)"
	@echo "  make release     build + versioned artifacts in dist/"
	@echo "  make menuconfig  Kconfig UI"
	@echo "  make clean       remove build/ and dist/"

# Host-side protocol sanity test — compiles with a plain C compiler, no Zephyr.
test:
	@mkdir -p $(BUILD)
	$(HOSTCC) -std=c11 -Wall -Wextra -Isrc test/host_report_test.c -o $(BUILD)/host_report_test
	@$(BUILD)/host_report_test

build:
	$(WEST) build -b $(BOARD) -d $(BUILD) .

flash: build
	$(WEST) flash -d $(BUILD)

uf2: build
	@echo "UF2 (double-tap RESET, then drag onto the NOTCHDECK drive):"
	@ls -la $(BUILD)/zephyr/zephyr.uf2

release: build
	@mkdir -p dist
	@cp $(BUILD)/zephyr/zephyr.uf2 dist/$(APP)-v$(VER).uf2
	@cp $(BUILD)/zephyr/zephyr.hex dist/$(APP)-v$(VER).hex
	@echo "release artifacts:"; ls -la dist/

menuconfig:
	$(WEST) build -d $(BUILD) -t menuconfig

clean:
	rm -rf $(BUILD) dist
