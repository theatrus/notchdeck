cmake_minimum_required(VERSION 3.20.0)

find_package(Zephyr REQUIRED HINTS $ENV{ZEPHYR_BASE})
project(notchdeck_one)

target_sources(app PRIVATE
	src/main.c
	src/report_engine.c
	src/lever.c
	src/leds.c
	src/transport_usb.c
	src/transport_ble.c
	src/dfu.c
)
