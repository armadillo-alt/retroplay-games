# Retroplay Games

The game screen for Retroplay's "Games on TV": NES and SNES emulators that run in a web page, so
a TV or Cast device can play while a phone running Retroplay acts as the controller.

Live page: https://armadillo-alt.github.io/retroplay-games/

Right now the page is a **player and speed test**: load the NES or SNES test cartridge (or a game
file you copied from a cartridge you own) and press **Speed test** to see how many times faster
than a real console the device runs. 100% is just enough; 150% or more is comfortable. An NES
needs far less than an SNES, about a third as much.

## What's here
- `index.html` — the page: picks the emulator by the file's header or extension, draws the picture, plays the sound, reads the keys; on phones and tablets it shows touch controls (a D-pad you slide your thumb around, SELECT, START, B and A, plus X, Y, L and R for SNES) and a FULL SCREEN key
- `receiver.html` — the Cast receiver for Games on TV: Retroplay on the phone sends the game in 36 KB pieces (Cast messages are capped at 64 KB), any saved progress, then the pad as a bitmask on every change; battery saves go back to the phone, since Cast receivers may not keep data. Namespace `urn:x-cast:studio.setout.retroplay.games`; `receiver.html?test` runs it in a normal browser with `rpReceive(message)` for testing
- `fceumm.js`, `fceumm.wasm` — FCEUmm, the NES emulator (wide support for multi-game cartridge boards)
- `supafaust.js`, `supafaust.wasm` — Beetle Supafaust, the SNES emulator
- `src/frontend.c` — a small libretro frontend, built once per emulator: runs a frame, hands over the picture (RGBA), the sound (16-bit stereo, 48 kHz) and takes the pad as a bitmask; gives cores the game from memory
- `src/libretro.h` — the libretro API header
- `src/webstubs.c` — stand-ins for thread calls a web page lacks (Supafaust runs on one thread here)
- `src/supafaust-renderer.patch` — one line in Supafaust's libretro wrapper so the single-thread renderer setting is honoured
- `src/make_test_rom.py`, `src/make_nes_test_rom.py` — build the SNES and NES test cartridges, written for Retroplay
- `src/build.sh` — rebuilds both emulators from source with Emscripten

No games are included. Load only game files you made yourself or copied from cartridges you own.

## Licences
- FCEUmm, the NES emulator, is licensed GPLv2: https://github.com/libretro/libretro-fceumm
- Beetle Supafaust, the SNES emulator, is by the Mednafen team and licensed GPLv2 or later: https://github.com/libretro/supafaust
- Everything else here is © SetOut.Studio and licensed GPLv2 or later, so the whole page can be shared and sold under the GPL.
