"""Builds Retroplay's test cartridge: a 32 KB LoROM that switches on all layers, changes the
backdrop colour every frame (so motion shows it runs) and keeps the CPU busy in between.
Written from scratch for testing; free to use."""
import struct, sys

rom = bytearray(0x8000)
code = bytes([
    0x78,             # SEI
    0x18, 0xFB,       # CLC ; XCE  -> native mode
    0xE2, 0x20,       # SEP #$20   -> 8-bit A
    0xA9, 0x8F, 0x8D, 0x00, 0x21,   # LDA #$8F ; STA $2100  (screen off)
    0xA9, 0x01, 0x8D, 0x05, 0x21,   # LDA #$01 ; STA $2105  (BG mode 1)
    0xA9, 0x1F, 0x8D, 0x2C, 0x21,   # LDA #$1F ; STA $212C  (all layers and sprites on)
    0xA9, 0x0F, 0x8D, 0x00, 0x21,   # LDA #$0F ; STA $2100  (screen on, full brightness)
    0xA9, 0x81, 0x8D, 0x00, 0x42,   # LDA #$81 ; STA $4200  (NMI on, auto-joypad on)
    0x58,             # CLI
    # busy loop: count in X and Y
    0xE8,             # loop: INX
    0xC8,             #       INY
    0x80, 0xFC,       #       BRA loop
])
nmi = bytes([
    0xE6, 0x00,       # INC $00
    0x9C, 0x21, 0x21, # STZ $2121  (colour 0)
    0xA5, 0x00,       # LDA $00
    0x8D, 0x22, 0x21, # STA $2122
    0x4A,             # LSR A
    0x8D, 0x22, 0x21, # STA $2122
    0x40,             # RTI
])
rti = bytes([0x40])
rom[0:len(code)] = code
NMI_AT = 0x0100
RTI_AT = 0x0200
rom[NMI_AT:NMI_AT + len(nmi)] = nmi
rom[RTI_AT] = 0x40
# Header at $7FC0
title = b"RETROPLAY TEST CART  "
rom[0x7FC0:0x7FC0 + 21] = title
rom[0x7FD5] = 0x20   # LoROM, slow
rom[0x7FD6] = 0x00   # ROM only
rom[0x7FD7] = 0x05   # 32 KB
rom[0x7FD8] = 0x00   # no SRAM
rom[0x7FD9] = 0x01   # North America (NTSC)
rom[0x7FDA] = 0x00
rom[0x7FDB] = 0x00
def vec(at, addr):
    rom[at:at + 2] = struct.pack('<H', 0x8000 + addr)
# Native vectors $FFE4..: COP BRK ABORT NMI unused IRQ
for off in (0x7FE4, 0x7FE6, 0x7FE8, 0x7FEE):
    vec(off, RTI_AT)
vec(0x7FEA, NMI_AT)
# Emulation vectors: COP, ABORT, NMI, RESET, IRQ/BRK
for off in (0x7FF4, 0x7FF8, 0x7FFA, 0x7FFE):
    vec(off, RTI_AT)
vec(0x7FFC, 0)
# Checksum (with complement and checksum fields counted as FFFF + 0000)
rom[0x7FDC:0x7FE0] = b"\xff\xff\x00\x00"
s = sum(rom) & 0xFFFF
rom[0x7FDC:0x7FDE] = struct.pack('<H', s ^ 0xFFFF)
rom[0x7FDE:0x7FE0] = struct.pack('<H', s)
open(sys.argv[1], "wb").write(rom)
