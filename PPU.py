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
        self.patternTable: list[bytearray] = [bytearray(4096)] * 2  # two 4 KB pattern tables (https://youtu.be/xdzOvpYPmGE?list=PLrOv9FMX8xJHqMvSGB_9G9nZZ_4IgteYf&t=835)
        # ^^ pattern table reminder ^^ (https://youtu.be/xdzOvpYPmGE?list=PLrOv9FMX8xJHqMvSGB_9G9nZZ_4IgteYf&t=872)
        
        
        # Pattern memory
        #   0x0000 -> 0x1FFF (8KB)
        # Name Table
        #   0x2000 -> 0x2FFF (2KB)
        # Palettes
        #   0x3F00 -> 0x3FFF
        
        # Pygame colors
        # using 2C02 colors. First one on https://www.nesdev.org/wiki/PPU_palettes
        self.colors = {
            0x00: (98,98,98),
            0x01: (0,31,178),
            0x02: (36,4,200),
            0x03: (82,0,178),
            0x04: (115,0,118),
            0x05: (128,0,36),
            0x06: (115,11,0),
            0x07: (82,40,0),
            0x08: (36,68,0),
            0x09: (0,87,0),
            0x0A: (0,92,0),
            0x0B: (0,83,36),
            0x0C: (0,60,118),
            0x0D: (0,0,0), # DONT USE. Results in blacker than black signal. Causes problems for some TVs
            0x0E: (0,0,0),
            0x0F: (0,0,0),
            
            0x10: (171,171,171),
            0x11: (13,87,255),
            0x12: (75,48,255),
            0x13: (138,19,255),
            0x14: (118,8,214),
            0x15: (210,18,105),
            0x16: (199,46,0),
            0x17: (157,84,0),
            0x18: (96,123,0),
            0x19: (32,152,0),
            0x1A: (0,163,0),
            0x1B: (0,153,66),
            0x1C: (0,125,180),
            0x1D: (0,0,0),
            0x1E: (0,0,0),
            0x1F: (0,0,0),
            
            0x20: (255,255,255),
            0x21: (83,174,255),
            0x22: (144,133,255),
            0x23: (211,101,255),
            0x24: (255,87,255),
            0x25: (255,93,207),
            0x26: (255,119,87),
            0x27: (250,158,0),
            0x28: (189,199,0),
            0x29: (122,231,0),
            0x2A: (67,246,17),
            0x2B: (38,239,126),
            0x2C: (44,213,246),
            0x2D: (78,78,78),
            0x2E: (0,0,0),
            0x2F: (0,0,0),
            
            0x30: (255,255,255),
            0x31: (182,255,255),
            0x32: (206,209,255),
            0x33: (233,195,255),
            0x34: (255,188,255),
            0x35: (255,189,244),
            0x36: (255,198,195),
            0x37: (255,213,154),
            0x38: (233,230,129),
            0x39: (206,244,129),
            0x3A: (182,251,154),
            0x3B: (169,250,195),
            0x3C: (169,240,244),
            0x3D: (184,184,184),
            0x3E: (0,0,0),
            0x3F: (0,0,0),
        }
        
        
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
    
    
    def getPatternTable(self, tableIndex):
        for tileY in range(16):
            for tileX in range(16):
                offset = tileY * 256 + tileX * 16
                for row in range(8):
                    tileLSB = self.ram.readAddress(UInt16(tableIndex * 0x1000 + offset + row + 0))
                    tileMSB = self.ram.readAddress(UInt16(tableIndex * 0x1000 + offset + row + 8))
                    
                    for col in range(8):
                        pixel = (tileLSB & 0x01) + (tileMSB & 0x01)
                        tileLSB >>= 1
                        tileMSB >>= 1
                        
                        #print(pixel, hex(pixel))
                        #self.patternTable[tableIndex].setPixel(
                        #    tileX * 8 + (7 - col),
                        #    tileY * 8 + row
                        #)
        
        return self.patternTable[tableIndex]
    
    def getColorFromPaletteRam(self, palette, pixel):
        pass
    
    
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
        