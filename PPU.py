from RAM import RAM
from BitwiseInts import Int8, UInt8, Int16, UInt16

# Power Up Memory
# https://www.nesdev.org/wiki/PPU_power_up_state

# Memory Map
# https://www.nesdev.org/wiki/CPU_memory_map

# NES PPU registers
#   0x2000 -> 0x2007 | 8 bytes in size
# Mirrors of PPU registers
#   0x2008 -> 0x3FFF | Repeat every 8 bytes

from BitwiseInts import Int8, UInt8, UInt16, UInt16
from Screen import WriteableScreen

class PPU:
    def __init__(self, console) -> None:
        self.console = console
        self.ram: RAM = self.console.ram
        self.screen: WriteableScreen = self.console.screen
        
        self.allNESColors = []
        
        self.scanline = 0
        self.cycle = 0
        self.frameComplete = False
        
        self.nameTables: list[bytearray] = [bytearray(1024)] * 2  # two 1KB name tables (https://youtu.be/xdzOvpYPmGE?list=PLrOv9FMX8xJHqMvSGB_9G9nZZ_4IgteYf&t=807)
        self.paletteTable: bytearray = bytearray(32)
        self.patternTable: list[bytearray] = bytearray(4096) * 2  # two 4 KB pattern tables (https://youtu.be/xdzOvpYPmGE?list=PLrOv9FMX8xJHqMvSGB_9G9nZZ_4IgteYf&t=835)
        # ^^ pattern table reminder ^^ (https://youtu.be/xdzOvpYPmGE?list=PLrOv9FMX8xJHqMvSGB_9G9nZZ_4IgteYf&t=872)
        
        
        # Pattern memory
        #   0x0000 -> 0x1FFF (8KB)
        # Name Table
        #   0x2000 -> 0x2FFF (2KB)
        # Palettes
        #   0x3F00 -> 0x3FFF
        
        
        
        self.vblankFlag = False          # 0 = not in vblank, 1 = in vblank
        self.spriteZeroHitFlag = False  # set when a nonzero pixel of sprite 0 overlaps a nonzero background pixel; cleared at dot 1 of the pre-render line. Used for raster timing.
        self.spriteOverflowFlag = True  # https://www.nesdev.org/wiki/PPU_sprite_evaluation
        
        #self.atPowerRegisters()
    
    def step(self):
        # Some fake noise for now
        self.screen.setPixel(self.cycle - 1, self.scanline, (255,255,255))
        
        #print(f"{self.cycle-1} / 341 ; {self.scanline} / 261 ; {341*261}")
        
        self.cycle += 1
        if self.cycle >= 341:
            self.cycle = 0
            self.scanline += 1
            
            if self.scanline >= 261:
                self.scanline = -1
                self.frameComplete = True
        
        return 0
    
    def readData(self, address: UInt16):
        data: UInt8 = 0x00
        
        if address == 0x0000: # Control
            pass
        if address == 0x0001: # Mask
            pass
        if address == 0x0002: # Status
            pass
        if address == 0x0003: # OAM Address
            pass
        if address == 0x0004: # OAM Data
            pass
        if address == 0x0005: # Scroll
            pass
        if address == 0x0006: # PPU Address
            pass
        if address == 0x0007: # PPU Data
            pass
        
        return data
    
    def writeData(self, address: UInt16):
        data: UInt8 = 0x00
        
        if address == 0x0000: # Control
            pass
        if address == 0x0001: # Mask
            pass
        if address == 0x0002: # Status
            pass
        if address == 0x0003: # OAM Address
            pass
        if address == 0x0004: # OAM Data
            pass
        if address == 0x0005: # Scroll
            pass
        if address == 0x0006: # PPU Address
            pass
        if address == 0x0007: # PPU Data
            pass
        
        return data
    
    
    
    def updatePPUStatus(self):        
        binaryString = f"0b{1 if self.vblankFlag else 0}{1 if self.spriteZeroHitFlag else 0}{1 if self.spriteOverflowFlag else 0}00000"
        PPUStatusAddress = UInt16(0x2002)
        self.ram.writeAddress(PPUStatusAddress, int(binaryString, 2))
        
        self.mirrorRegisters()
    
    def mirrorRegisters(self):
        dataToMirror = self.ram.readSpace(UInt16(0x2000), UInt16(0x2007)) # 8 bytes
        for newAddressStart in range(UInt16(0x2008).value, UInt16(0x3FFF).value, Int8(0x8).value):
            selfOffsetAddress: UInt16 = UInt16(newAddressStart) + 0x8
            self.ram.writeSpace(UInt16(newAddressStart), selfOffsetAddress, dataToMirror)
    
    #; ? = unknown, x = irrelevant, + = often set, U = unchanged
    def atPowerRegisters(self):
        self.ram.writeAddress(UInt16(0x2000), 0b0000_0000)  # PPUCTRL
        self.ram.writeAddress(UInt16(0x2001), 0b0000_0000)  # PPUMASK
        self.ram.writeAddress(UInt16(0x2002), 0b1010_0000)  # PPUSTATUS ~ +0+x xxxx
        self.ram.writeAddress(UInt16(0x2003), 0b00)         # OAMADDR
        self.ram.writeAddress(UInt16(0x2005), 0b0000)       # PPUSCROLL
        self.ram.writeAddress(UInt16(0x2006), 0b0000)       # PPUADDR
        self.ram.writeAddress(UInt16(0x2007), 0b00)         # PPUDATA
        
    def reset(self):
        self.ram.writeAddress(UInt16(0x2000), 0b0000_0000)  # PPUCTRL
        self.ram.writeAddress(UInt16(0x2001), 0b0000_0000)  # PPUMASK
        
        statusMSB = self.ram.readAddress(UInt16(0x2002)) >> 8        # MSB is unchanged
        self.ram.writeAddress(UInt16(0x2002), int(f"0b{statusMSB}110_0000", 2))  # PPUSTATUS ~ U??x xxxx
        
        # self.ram.writeAddress(UInt16(0x2003), 0b00)       # OAMADDR   ~ unchanged
        self.ram.writeAddress(UInt16(0x2005), 0b0000)       # PPUSCROLL
        #self.ram.writeAddress(UInt16(0x2006), 0b0000)      # PPUADDR   ~ unchanged
        self.ram.writeAddress(UInt16(0x2007), 0b00)         # PPUDATA
        