#!/usr/bin/env python3
"""Patch an upstream Bruce checkout for the M5Stack Cap CC1101 on Cardputer ADV."""
from pathlib import Path
import sys

root = Path(sys.argv[1])
interface = root / "boards/m5stack-cardputer/interface.cpp"
board_ini = root / "boards/m5stack-cardputer/m5stack-cardputer.ini"
rf_utils = root / "src/modules/rf/rf_utils.cpp"

# 1) Board-level defaults. This makes the custom build match the M5Stack Cap.
s = board_ini.read_text()
repls = {
    "-DCC1101_GDO0_PIN=GROVE_SDA": "-DCC1101_GDO0_PIN=15",
    "-DCC1101_SS_PIN=SPI_SS_PIN": "-DCC1101_SS_PIN=5",
}
for old, new in repls.items():
    if old not in s:
        raise SystemExit(f"Missing expected board config text: {old}")
    s = s.replace(old, new, 1)
marker = "\t-DCORE_DEBUG_LEVEL=0\n"
if marker not in s:
    raise SystemExit("Could not find board debug flag marker")
s = s.replace(marker, marker + "\t-DCARDPUTER_ADV_M5STACK_CAP_CC1101=1\n", 1)
board_ini.write_text(s)

# 2) Cardputer ADV runtime code currently overwrites the CC1101 pin config.
s = interface.read_text()
old = """    bruceConfigPins.CC1101_bus.sck = (gpio_num_t)40;\n    bruceConfigPins.CC1101_bus.miso = (gpio_num_t)39;\n    bruceConfigPins.CC1101_bus.mosi = (gpio_num_t)14;\n    bruceConfigPins.CC1101_bus.cs = (gpio_num_t)13;\n    bruceConfigPins.CC1101_bus.io0 = (gpio_num_t)5;\n"""
new = """    bruceConfigPins.CC1101_bus.sck = (gpio_num_t)40;\n    bruceConfigPins.CC1101_bus.miso = (gpio_num_t)39;\n    bruceConfigPins.CC1101_bus.mosi = (gpio_num_t)14;\n    bruceConfigPins.CC1101_bus.cs = (gpio_num_t)5;\n    bruceConfigPins.CC1101_bus.io0 = (gpio_num_t)15;\n    bruceConfigPins.CC1101_bus.io2 = GPIO_NUM_NC;\n\n    // GPIO13 is the M5Stack Cap CC1101 RF_SW0 control line.\n    pinMode(13, OUTPUT);\n    digitalWrite(13, LOW);\n"""
if old not in s:
    raise SystemExit("Missing expected Cardputer ADV CC1101 runtime block")
s = s.replace(old, new, 1)
interface.write_text(s)

# 3) The Cap uses CC1101 GDO2 as RF_SW1. Add frequency-dependent RF switch control
#    immediately after Bruce programs the CC1101 frequency. GDO2=0x2F is HW-low;
#    setting INV=1 (0x40) makes the same hardware function high.
s = rf_utils.read_text()
needle = "        ELECHOUSE_cc1101.setMHZ(frequency);\n"
insert = """        ELECHOUSE_cc1101.setMHZ(frequency);\n\n#if defined(CARDPUTER_ADV_M5STACK_CAP_CC1101)\n        // M5Stack Cap CC1101 RF switch: RF_SW0 is GPIO13 and RF_SW1 is CC1101 GDO2.\n        // 315 MHz: 0/0, 433 MHz: 0/1, 868/915 MHz: 1/1.\n        bool capSw0 = false;\n        bool capSw1 = false;\n        if (frequency <= 350.0f) {\n            capSw0 = false;\n            capSw1 = false;\n        } else if (frequency < 468.0f) {\n            capSw0 = false;\n            capSw1 = true;\n        } else if (frequency >= 779.0f && frequency <= 928.0f) {\n            capSw0 = true;\n            capSw1 = true;\n        }\n        pinMode(13, OUTPUT);\n        digitalWrite(13, capSw0 ? HIGH : LOW);\n        ELECHOUSE_cc1101.SpiWriteReg(CC1101_IOCFG2,\n                                      (byte)(0x2F | (capSw1 ? 0x40 : 0x00)));\n#endif\n"""
if needle not in s:
    raise SystemExit("Could not find setMHZ call in rf_utils.cpp")
s = s.replace(needle, insert, 1)
rf_utils.write_text(s)

print("Bruce patched for M5Stack Cap CC1101 on Cardputer ADV")
