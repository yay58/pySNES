"""Headless NES runner for emulator-free specs.

Runs a compiled ROM on py65 with the neslib PPU model wired to the
hardware registers ($2000-$2007, $4014). Frames advance by injecting
NMIs, so specs can assert PPU state (VRAM, scroll, OAM) at exact
frame counts -- deterministically, without FCEUX.
"""

from py65.devices.mpu6502 import MPU
from py65.memory import ObservableMemory

from neslib.font import font_chr
from neslib.library import lib
from neslib.ppu import PPU
from pynes.cart import Cart

PRG_BASE = 0xC000
PRG_SIZE = 16384
HEADER_SIZE = 16
PPU_REGISTERS = range(0x2000, 0x2008)
OAM_DMA = 0x4014


class NESRunner:
    def __init__(self, source):
        cart = Cart(libraries=[lib], chr_banks=1, chr_data=font_chr())
        rom = cart.to_nes(source)
        prg = rom[HEADER_SIZE : HEADER_SIZE + PRG_SIZE]

        self.ppu = PPU()
        self.cpu = MPU()
        memory = ObservableMemory()
        memory.subscribe_to_write(PPU_REGISTERS, self._ppu_write)
        memory.subscribe_to_read(PPU_REGISTERS, self._ppu_read)
        memory.subscribe_to_write([OAM_DMA], self._oam_dma)
        memory.write(PRG_BASE, prg)
        self.cpu.memory = memory

        self.nmi_vector = prg[0x3FFA] | (prg[0x3FFB] << 8)
        self.cpu.pc = prg[0x3FFC] | (prg[0x3FFD] << 8)

    def _ppu_write(self, address, value):
        self.ppu.write_register(address, value)

    def _ppu_read(self, address):
        return self.ppu.read_register(address)

    def _oam_dma(self, address, value):
        page = value << 8
        self.ppu.oam = bytearray(self.cpu.memory[page : page + 256])

    def _run(self, max_steps=1000000):
        """Step the CPU until it parks in an idle loop (JMP-to-self),
        which is how both the main loop and post-RTI code settle."""
        for _ in range(max_steps):
            pc = self.cpu.pc
            self.cpu.step()
            if self.cpu.pc == pc:
                return
        raise RuntimeError('runaway execution (no idle loop reached)')

    def run_reset(self):
        """Run the RESET handler until the main loop parks."""
        self._run()

    def run_frames(self, frames):
        """Advance whole frames: one NMI per frame (when enabled),
        each run to completion."""
        for _ in range(frames):
            if not self.ppu.nmi_enabled:
                continue
            self.cpu.stPushWord(self.cpu.pc)
            self.cpu.stPush(self.cpu.p)
            self.cpu.pc = self.nmi_vector
            self._run(max_steps=100000)
