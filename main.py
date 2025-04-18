from Cartridge import Cartridge
from CPU import CPU
from Memory import Memory

nestestCartridge = Cartridge("./nestest.nes")
nestestCartridge.load()

# Init Console
NES_Memory = Memory(randomizeMemory=False)
NES_Memory.loadCartridgeIntoMemory(nestestCartridge)

#NES_Memory.dumpMemory()

NES_CPU = CPU(NES_Memory)
NES_CPU.reset()
# For nestest im foring it to start at 0xC000 to skip the PPU
NES_CPU.pc = 0xC000

NES_CPU.logsEnabled = True

running = True
while running:
    NES_CPU.tick()

NES_Memory.dumpMemory()

nestestCartridge.close()

# Reference Documents:
# https://en.wikipedia.org/wiki/MOS_Technology_6502#Instruction_table
# https://www.nesdev.org/wiki/Instruction_reference
# https://www.nesdev.org/wiki/CPU_unofficial_opcodes
# https://www.nesdev.org/wiki/CPU_addressing_modes
# https://www.nesdev.org/wiki/CPU_memory_map
# https://github.com/christopherpow/nes-test-roms/tree/master/other <-- NESTEST and it's info is in there
