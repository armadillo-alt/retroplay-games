# Retroplay Games

The game screen for Retroplay's "Games on TV": an SNES emulator that runs in a web page, so a TV
or Cast device can play while a phone running Retroplay acts as the controller.

Right now this is the **speed test**: open the page on a device, load the test cartridge (or a game
file of your own), and press **Speed test** to see how many times faster than a real console the
device runs. 100% is just enough; 150% or more is comfortable.

## What's here
- `index.html`, `supafaust.js`, `supafaust.wasm` — the page and the emulator, served by GitHub Pages
- `src/frontend.c` — a small libretro frontend: runs a frame, hands over the picture (RGBA), the sound (16-bit stereo at 48 kHz) and takes the pad as a bitmask
- `src/webstubs.c` — stand-ins for thread calls a web page lacks (the emulator runs on one thread here)
- `src/supafaust-renderer.patch` — one line in Supafaust's libretro wrapper so the single-thread renderer setting is honoured
- `src/make_test_rom.py` — builds the test cartridge, written for Retroplay
- `src/build.sh` — rebuilds the emulator from source with Emscripten

No games are included. Load only game files you made yourself or copied from cartridges you own.

## Licences
- Beetle Supafaust, the emulator, is by the Mednafen team and licensed GPLv2 or later: https://github.com/libretro/supafaust
- Everything else here is © SetOut.Studio and licensed GPLv2 or later, so the whole page can be shared and sold under the GPL.
