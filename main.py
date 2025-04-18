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

running = True
while running:
    NES_CPU.tick()

NES_Memory.dumpMemory()

nestestCartridge.close()