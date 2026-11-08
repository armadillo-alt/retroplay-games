/*
 * Retroplay Games: a minimal libretro frontend for the web.
 * Drives one emulator core a frame at a time and hands the page the picture (RGBA),
 * the sound (16-bit stereo) and takes the pad state as a bitmask.
 * Licensed GPLv2+, like the Beetle Supafaust core it links with.
 */
#include <stdint.h>
#include <stdlib.h>
#include <string.h>
#include <emscripten.h>
#include "libretro.h"

static uint32_t picture[512 * 512];
static int width, height;
static int16_t sound[2 * 48000];
static int sound_frames;
static uint16_t pad;
static uint8_t *game;
static struct retro_system_av_info av;

static const char *setting(const char *key)
{
    /* One thread (a web page has no real threads), 32-bit colour, 48 kHz sound for the browser */
    if (!strcmp(key, "supafaust_renderer")) return "st";
    if (!strcmp(key, "supafaust_pixel_format")) return "xrgb8888";
    if (!strcmp(key, "supafaust_audio_rate")) return "48000";
    if (!strcmp(key, "supafaust_thread_affinity_emu")) return "0x0";
    if (!strcmp(key, "supafaust_thread_affinity_ppu")) return "0x0";
    if (!strcmp(key, "supafaust_correct_aspect")) return "disabled";
    return NULL;
}

static bool environment(unsigned cmd, void *data)
{
    switch (cmd) {
    case RETRO_ENVIRONMENT_GET_VARIABLE: {
        struct retro_variable *v = data;
        v->value = setting(v->key);
        return v->value != NULL;
    }
    case RETRO_ENVIRONMENT_SET_PIXEL_FORMAT:
        return *(enum retro_pixel_format *)data == RETRO_PIXEL_FORMAT_XRGB8888;
    case RETRO_ENVIRONMENT_GET_INPUT_BITMASKS:
    case RETRO_ENVIRONMENT_SET_VARIABLES:
    case RETRO_ENVIRONMENT_SET_INPUT_DESCRIPTORS:
    case RETRO_ENVIRONMENT_SET_SERIALIZATION_QUIRKS:
        return true;
    default:
        return false;
    }
}

static void video(const void *data, unsigned w, unsigned h, size_t pitch)
{
    if (!data) return; /* the same picture as last time */
    if (w > 512) w = 512;
    if (h > 512) h = 512;
    for (unsigned y = 0; y < h; y++) {
        const uint32_t *src = (const uint32_t *)((const uint8_t *)data + y * pitch);
        uint32_t *dst = picture + y * w;
        for (unsigned x = 0; x < w; x++) {
            uint32_t p = src[x];
            /* XRGB in a little-endian word becomes RGBA bytes for the canvas */
            dst[x] = 0xFF000000u | ((p & 0xFF) << 16) | (p & 0xFF00) | ((p >> 16) & 0xFF);
        }
    }
    width = w;
    height = h;
}

static size_t sound_batch(const int16_t *data, size_t frames)
{
    size_t room = 48000 - sound_frames;
    if (frames > room) frames = room;
    memcpy(sound + 2 * sound_frames, data, frames * 4);
    sound_frames += frames;
    return frames;
}

static void sound_one(int16_t l, int16_t r)
{
    int16_t s[2] = { l, r };
    sound_batch(s, 1);
}

static void poll(void) {}

static int16_t state(unsigned port, unsigned device, unsigned index, unsigned id)
{
    if (port != 0 || device != RETRO_DEVICE_JOYPAD) return 0;
    if (id == RETRO_DEVICE_ID_JOYPAD_MASK) return pad;
    return (pad >> id) & 1;
}

EMSCRIPTEN_KEEPALIVE int rp_init(void)
{
    retro_set_environment(environment);
    retro_set_video_refresh(video);
    retro_set_audio_sample(sound_one);
    retro_set_audio_sample_batch(sound_batch);
    retro_set_input_poll(poll);
    retro_set_input_state(state);
    retro_init();
    return 1;
}

/* Takes ownership of [data] (from malloc). 1 when the game loaded. */
EMSCRIPTEN_KEEPALIVE int rp_load(uint8_t *data, int size)
{
    if (game) {
        retro_unload_game();
        free(game);
    }
    game = data;
    struct retro_game_info info = { "game.sfc", game, (size_t)size, NULL };
    if (!retro_load_game(&info)) {
        free(game);
        game = NULL;
        return 0;
    }
    retro_get_system_av_info(&av);
    return 1;
}

EMSCRIPTEN_KEEPALIVE void rp_run(void) { sound_frames = 0; retro_run(); }
EMSCRIPTEN_KEEPALIVE void rp_reset(void) { retro_reset(); }
EMSCRIPTEN_KEEPALIVE void rp_pad(int mask) { pad = (uint16_t)mask; }
EMSCRIPTEN_KEEPALIVE uint32_t *rp_picture(void) { return picture; }
EMSCRIPTEN_KEEPALIVE int rp_width(void) { return width; }
EMSCRIPTEN_KEEPALIVE int rp_height(void) { return height; }
EMSCRIPTEN_KEEPALIVE int16_t *rp_sound(void) { return sound; }
EMSCRIPTEN_KEEPALIVE int rp_sound_frames(void) { return sound_frames; }
EMSCRIPTEN_KEEPALIVE double rp_fps(void) { return av.timing.fps; }
EMSCRIPTEN_KEEPALIVE double rp_sample_rate(void) { return av.timing.sample_rate; }
EMSCRIPTEN_KEEPALIVE void *rp_save_data(void) { return retro_get_memory_data(RETRO_MEMORY_SAVE_RAM); }
EMSCRIPTEN_KEEPALIVE int rp_save_size(void) { return (int)retro_get_memory_size(RETRO_MEMORY_SAVE_RAM); }
