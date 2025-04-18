import random
from Cartridge import Cartridge

class Memory():
    def __init__(self, randomizeMemory=False):
        # Not all of the memory will 100% be used b/c in the getAddress we change the address if it lies in a mirrored zone
        self.memory = bytearray(0xffff + 1)# +1 so we can index from 0x0000 to 0xfff
        
        if randomizeMemory: self.makeMemoryRandom()
    
    def loadCartridgeIntoMemory(self, cartridge: Cartridge):
        PRGROM = bytearray(cartridge.PRGROM_Size * 16384)
        CHRROM = bytearray(cartridge.CHRROM_Size * 8192)
        
        cartridge.file.seek(0x10, 0)
        cartridge.file.readinto(PRGROM)
        cartridge.file.readinto(CHRROM)
        
        self.writeGroup(0x8000, PRGROM)
        if cartridge.PRGROM_Size == 1: # Mirror it again to fill the space
            self.writeGroup(0xc000, PRGROM)
        
    
    def makeMemoryRandom(self):
        for i in range(0, len(self.memory)):
            randomByte = ''.join(random.choice("01") for _ in range(8))
            self.memory[i] = int(randomByte, 2)
    
    def getAddress(self, address):
        mappedAddress = -1
        
        # 0x0000 to 0x07ff is internal RAM (2KB)
        # 0x0800 to 0x1fff are mirrors of the internal RAM (repeated 3 times)
        if address >= 0x0000 and address <= 0x1fff:
            mappedAddress = address % 0x800 # 0x0800 is 2KB in hex (the size of the internal RAM)
        
        # 0x2000 to 0x2007 are the PPU Registers
        # 0x2008 to 0x3fff are mirrors of the PPU registers (repeats every 8 bytes)
        if address >= 0x2000 and address <= 0x3fff:
            mappedAddress = (address % 8) + 0x2000
        
        # 0x4000 to 0x4017 are APU and IO registers
        if address >= 0x4000 and address <= 0x4017:
            mappedAddress = address
        
        # 0x4018 to 0x401f is APU and I/O functionality that is normally disabled
        if address >= 0x4018 and address <= 0x401f:
            mappedAddress = address
        
        # 0x4020 to 0xffff is unmapped and available for cartridges to use
        # 0x6000 to 0x7fff is usually cartridge ram when present
        # 0x8000 to 0xffff is usually cartridge rom and mapper registers
        if address >= 0x4020 and address <= 0xffff:
            mappedAddress = address
        
        return mappedAddress
        
    def writeGroup(self, address, values):
        addressToWrite = self.getAddress(address)
        self.memory[addressToWrite:len(values)] = values
    
    def write(self, address, value):
        addressToWrite = self.getAddress(address)
        self.memory[addressToWrite] = value
    
    def read(self, address):
        addressToRead = self.getAddress(address)
        return self.memory[addressToRead]

    def dumpMemory(self):
        # "lw" b/c it's the initials of someone I like. It's just a file to read the bytes from.
        with open("memory.lw", "wb") as f:
            f.write(self.memory)

