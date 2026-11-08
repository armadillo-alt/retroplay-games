"""Builds Retroplay's NES test cartridge: a 24 KB NROM cart (16 KB program, 8 KB tiles) that
switches on the background and sprites, fills the screen with a checked tile, changes the
backdrop colour every frame (so motion shows it runs) and keeps the CPU busy in between.
Written from scratch for testing; free to use."""
import sys

prg = bytearray(0x4000)   # mapped at $C000 (and mirrored at $8000)


def put(addr, data):
    prg[addr - 0xC000:addr - 0xC000 + len(data)] = bytes(data)


put(0xC000, [
    0x78,                    # SEI
    0xD8,                    # CLD
    0xA2, 0xFF, 0x9A,        # LDX #$FF ; TXS
    0xA9, 0x00,              # LDA #0
    0x8D, 0x00, 0x20,        # STA $2000  (NMI off)
    0x8D, 0x01, 0x20,        # STA $2001  (screen off)
    0x2C, 0x02, 0x20,        # vblank1: BIT $2002
    0x10, 0xFB,              # BPL vblank1
    0x2C, 0x02, 0x20,        # vblank2: BIT $2002
    0x10, 0xFB,              # BPL vblank2
    0xA9, 0x80,              # LDA #$80
    0x8D, 0x00, 0x20,        # STA $2000  (NMI on)
    0xA9, 0x1E,              # LDA #$1E
    0x8D, 0x01, 0x20,        # STA $2001  (background and sprites on)
    0xE8,                    # loop: INX
    0xC8,                    # INY
    0x4C, 0x21, 0xC0,        # JMP loop
])
put(0xC030, [
    0x48,                    # PHA
    0xE6, 0x00,              # INC $00
    0xAD, 0x02, 0x20,        # LDA $2002  (reset the address latch)
    0xA9, 0x3F, 0x8D, 0x06, 0x20,   # LDA #$3F ; STA $2006
    0xA9, 0x00, 0x8D, 0x06, 0x20,   # LDA #$00 ; STA $2006
    0xA5, 0x00,              # LDA $00
    0x4A, 0x4A,              # LSR ; LSR
    0x29, 0x3F,              # AND #$3F
    0x8D, 0x07, 0x20,        # STA $2007  (backdrop colour)
    0xA9, 0x00,              # LDA #0
    0x8D, 0x05, 0x20,        # STA $2005
    0x8D, 0x05, 0x20,        # STA $2005  (scroll 0, 0)
    0xA9, 0x80,              # LDA #$80
    0x8D, 0x00, 0x20,        # STA $2000  (nametable 0, NMI on)
    0x68,                    # PLA
    0x40,                    # RTI
])
put(0xC060, [0x40])          # IRQ: RTI
put(0xFFFA, [0x30, 0xC0, 0x00, 0xC0, 0x60, 0xC0])   # NMI, RESET, IRQ

chr_rom = bytearray(0x2000)
# Tile 0 (the whole background, since the name table starts at zero): a check in colours 1 to 3
for row in range(8):
    chr_rom[row] = 0xAA if row % 2 == 0 else 0x55
    chr_rom[8 + row] = 0xCC if row < 4 else 0x33

header = b"NES\x1a" + bytes([1, 1, 0, 0]) + bytes(8)   # 1 x 16 KB program, 1 x 8 KB tiles, mapper 0

with open(sys.argv[1] if len(sys.argv) > 1 else "test-cart.nes", "wb") as f:
    f.write(header + prg + chr_rom)
