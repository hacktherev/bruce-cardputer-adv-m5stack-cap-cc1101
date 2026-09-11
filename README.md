# Bruce — Cardputer ADV + M5Stack Cap CC1101

Custom build of Bruce for the M5Stack Cardputer ADV with the M5Stack Cap CC1101.

Hardware pin mapping for the M5Stack Cap CC1101:

- SPI SCK: GPIO 40
- SPI MISO: GPIO 39
- SPI MOSI: GPIO 14
- CC1101 CS: GPIO 5
- CC1101 GDO0: GPIO 15
- RF switch control: GPIO 13 (RF_SW0)

This repository builds Bruce from the upstream `BruceDevices/firmware` source and applies the Cardputer ADV + M5Stack Cap CC1101 pin/configuration changes automatically.

## Build

GitHub Actions builds the firmware automatically. The resulting firmware artifact is attached to successful workflow runs.
