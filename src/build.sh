#!/bin/sh
# Builds the page's two emulators from source: FCEUmm (NES) and Beetle Supafaust (SNES),
# each linked with Retroplay's web frontend. Needs git and the Emscripten SDK (emsdk) on the PATH.
set -e
here=$(cd "$(dirname "$0")" && pwd)
export EMCC_CFLAGS="-fwasm-exceptions"
EXPORTS='["_malloc","_free","_rp_init","_rp_load","_rp_run","_rp_reset","_rp_pad","_rp_picture","_rp_width","_rp_height","_rp_sound","_rp_sound_frames","_rp_fps","_rp_sample_rate","_rp_save_data","_rp_save_size"]'
link_opts() {
  echo -s MODULARIZE=1 -s EXPORT_NAME=$1 -s ALLOW_MEMORY_GROWTH=1 -s INITIAL_MEMORY=67108864 -s ENVIRONMENT=web,node \
    -s "EXPORTED_FUNCTIONS=$EXPORTS" '-s EXPORTED_RUNTIME_METHODS=["HEAPU8","HEAP16","HEAPU32"]'
}

# SNES: Beetle Supafaust, with the single-thread renderer honoured
test -d supafaust || git clone --depth 1 https://github.com/libretro/supafaust.git
(cd supafaust && git apply "$here/supafaust-renderer.patch" 2>/dev/null || true)
(cd supafaust && emmake make platform=emscripten -j"$(nproc)")
cp supafaust/mednafen_supafaust_libretro_emscripten.bc supafaust_core.a
emcc -O3 -DGAME_EXT='"sfc"' -I"$here" -c "$here/frontend.c" -o fe_snes.o
emcc -O3 -c "$here/webstubs.c" -o webstubs.o
eval em++ -O3 -fwasm-exceptions fe_snes.o webstubs.o supafaust_core.a -o supafaust.js $(link_opts Supafaust)

# NES: FCEUmm, plus the libretro-common files its static build leaves to the frontend
test -d fceumm || git clone --depth 1 https://github.com/libretro/libretro-fceumm.git fceumm
(cd fceumm && emmake make -f Makefile.libretro platform=emscripten -j"$(nproc)")
cp fceumm/fceumm_libretro_emscripten.bc fceumm_core.a
lc=fceumm/src/drivers/libretro/libretro-common
mkdir -p lc
for f in compat/compat_posix_string.c compat/compat_snprintf.c compat/compat_strcasestr.c compat/compat_strl.c \
         compat/fopen_utf8.c encodings/encoding_utf.c file/file_path.c file/file_path_io.c streams/file_stream.c \
         streams/file_stream_transforms.c string/stdstring.c time/rtime.c vfs/vfs_implementation.c; do
  emcc -O3 -fwasm-exceptions -I$lc/include -c $lc/$f -o lc/$(basename $f .c).o
done
emcc -O3 -fwasm-exceptions -DGAME_EXT='"nes"' -I"$here" -c "$here/frontend.c" -o fe_nes.o
eval emcc -O3 -fwasm-exceptions fe_nes.o lc/*.o fceumm_core.a -o fceumm.js $(link_opts Fceumm)

python3 "$here/make_test_rom.py" test-cart.sfc
python3 "$here/make_nes_test_rom.py" test-cart.nes
echo "Built fceumm.js/.wasm, supafaust.js/.wasm, test-cart.nes and test-cart.sfc"
