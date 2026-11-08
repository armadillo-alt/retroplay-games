#!/bin/sh
# Builds the page's emulator from source: Beetle Supafaust + Retroplay's web frontend.
# Needs git and the Emscripten SDK (emsdk) on the PATH.
set -e
here=$(cd "$(dirname "$0")" && pwd)
test -d supafaust || git clone --depth 1 https://github.com/libretro/supafaust.git
(cd supafaust && git apply "$here/supafaust-renderer.patch" 2>/dev/null || true)
export EMCC_CFLAGS="-fwasm-exceptions"
(cd supafaust && emmake make platform=emscripten -j"$(nproc)")
cp supafaust/mednafen_supafaust_libretro_emscripten.bc supafaust_core.a
cp supafaust/libretro.h "$here/"
emcc -O3 -c "$here/frontend.c" -o frontend.o
emcc -O3 -c "$here/webstubs.c" -o webstubs.o
em++ -O3 -fwasm-exceptions frontend.o webstubs.o supafaust_core.a -o supafaust.js \
  -s MODULARIZE=1 -s EXPORT_NAME=Supafaust -s ALLOW_MEMORY_GROWTH=1 -s INITIAL_MEMORY=67108864 -s ENVIRONMENT=web \
  -s EXPORTED_FUNCTIONS='["_malloc","_free","_rp_init","_rp_load","_rp_run","_rp_reset","_rp_pad","_rp_picture","_rp_width","_rp_height","_rp_sound","_rp_sound_frames","_rp_fps","_rp_sample_rate","_rp_save_data","_rp_save_size"]' \
  -s EXPORTED_RUNTIME_METHODS='["HEAPU8","HEAP16","HEAPU32"]'
python3 "$here/make_test_rom.py" test-cart.sfc
echo "Built supafaust.js, supafaust.wasm and test-cart.sfc"
