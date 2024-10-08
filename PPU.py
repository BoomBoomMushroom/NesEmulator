from RAM import RAM
from BitwiseInts import Int8, UInt8, UInt16
from Screen import WriteableScreen
from Cartridge import Cartridge

import copy

# Power Up Memory
# https://www.nesdev.org/wiki/PPU_power_up_state

# Memory Map
# https://www.nesdev.org/wiki/CPU_memory_map

# NES PPU registers
#   0x2000 -> 0x2007 | 8 bytes in size
# Mirrors of PPU registers
#   0x2008 -> 0x3FFF | Repeat every 8 bytes

class PPU:
    def __init__(self, console) -> None:
        self.console = console
        self.ram: RAM = self.console.ram
        
        self.reset()
        
        self.screen: WriteableScreen = self.console.screen
        self.frameComplete = False
        
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
    
    def step(self):
        if self.scanline == -1 and self.cycle == 1:
            self.vblank = 0
            self.updateStatusRegister()
        
        if self.scanline == 241 and self.cycle == 1:
            self.vblank = 1
            # if control.enableMNI:
            #   self.nmi = 1
            self.updateStatusRegister()
        
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
    
    
    def getPatternTable(self, tableIndex, paletteIndex):
        patternTable = []
        
        for tileY in range(0, 16):
            for tileX in range(0, 16):
                offset = tileY * 256 + tileX * 16
                
                for row in range(0, 8):
                    lsb = self.readVRAM(tableIndex * 0x1000 + offset + row + 0)
                    msb = self.readVRAM(tableIndex * 0x1000 + offset + row + 8)
                    
                    tile = []
                    
                    for col in range(7, -1, -1): # 8 -> 0 (we're going from l->r but 0 -> 8 is l<-r)
                        pixel = (lsb & 0x01) + (msb & 0x01)
                        lsb >>= 1
                        msb >>= 1
                        tile.append(pixel)
    
    def getColorFromPalette(self, paletteIndex, pixel):
        address = 0x3F00 + (paletteIndex << 2) + pixel
        colorHex = self.readVRAM(address)
        return self.colors[colorHex]
          
    def getPaletteFromIndex(self, paletteIndex, colorTuple=False) -> list:
        paletteStart = 0x3F00
        #backgroundColor = self.vram[paletteStart]
        #allPalettes = self.vram[paletteStart:paletteStart+0x1D]
        #print(len(allPalettes), allPalettes)
        
        palette = []
        for i in range(4):
            address = paletteStart + 1 + (paletteIndex*4) + i
            valueAtAddress = self.vram[address]
            if colorTuple:
                palette.append(self.colors[valueAtAddress])
            else:
                palette.append(valueAtAddress)
        return palette
    
    
    
    
    
    def mirrorRegisters(self):
        dataToMirror = self.ram.readSpace(UInt16(0x2000), UInt16(0x2007)) # 8 bytes
        for newAddressStart in range(UInt16(0x2008).value, UInt16(0x3FFF).value, Int8(0x8).value):
            selfOffsetAddress: UInt16 = UInt16(newAddressStart) + 0x8
            self.ram.writeSpace(UInt16(newAddressStart), selfOffsetAddress, dataToMirror)
    
    def readStatusRegister(self) -> int:
        value = self.status
        
        self.vblank = 0
        self.writeToggle = 0
        self.updateStatusRegister()
        
        return value
    
    def readVRAM(self):
        address = self.address
        data = self.ppuDataBuffer
        self.ppuDataBuffer = self.vram[address]
        
        # Palette gets read instantly
        if address >= 0x3F00 and address <= 0x3F20: # 0x3F1F
            # dont increment if we're reading from the palette
            if address > 0x3F00: self.address -= 1
            data = self.ppuDataBuffer

        self.address += 1
        return data
    
    def writeVRAM(self, data):
        address = self.address
        if address >= 0x3F00 and address <= 0x3F1F:
            mirroredAddress = address & 0x3F1F
            self.vram[mirroredAddress] = data
            if mirroredAddress in [0x3F00, 0x3F04, 0x3F08, 0x3F0C]:
                self.vram[mirroredAddress + 0x10] = data
            elif mirroredAddress in [0x3F10, 0x3F14, 0x3F18, 0x3F1C]:
                self.vram[mirroredAddress - 0x10] = data
        else:
            self.vram[address] = data
    
    def writeRegister(self, register, value, mirrorRegisters: bool = False, fromRAM: bool = False):
        if register == 0x2000:
            self.ctrl = value
        elif register == 0x2001:
            self.mask = value
        elif register == 0x2002:
            self.status = value
        elif register == 0x2003:
            self.address = value
        elif register == 0x2004:
            self.oam[self.address] = value
            self.address += 1
        elif register == 0x2005:
            if self.writeToggle == 0:
                self.scroll = value
                self.writeToggle = 1
            else:
                self.scroll = (self.scroll << 8) | value
                self.writeToggle = 0
            value = self.scroll
        elif register == 0x2006:
            if self.writeToggle == 0:
                self.address = (self.address & 0x00FF) | (value << 8)
                self.writeToggle = 1
            else:
                self.address = (self.address & 0xFF00) | value
                self.writeToggle = 0
        elif register == 0x2007:
            self.writeVRAM(value)
            self.address += 1
            return
        else:
            raise ValueError # Register not found
        
        # Write to address in the RAM
        if fromRAM == False: self.ram.writeAddress(UInt16(register), value)
        if mirrorRegisters: self.mirrorRegisters()
    
    def updateStatusRegister(self):
        binary = f"0b{self.vblank}{self.spriteZeroHit}{self.spriteOverflow}00000"
        self.writeRegister(0x2002, int(binary, 2))
    
    def reset(self):
        self.vram = bytearray(0x4000)
        self.oam = bytearray(256)
        
        self.ppuDataBuffer = 0
        
        self.vramAddress = 0
        self.tempVramAddress = 0
        self.fineX = 0
        self.writeToggle = 0
        
        # PPU STATUS
        self.status = 0x00
        self.vblank = 0 # bit 7
        self.spriteZeroHit = 0 # bit 6
        self.spriteOverflow = 0 # bit 5
        
        self.writeRegister(0x2000, 0)
        self.writeRegister(0x2001, 0)
        self.updateStatusRegister()
        self.writeRegister(0x2003, 0)
        self.writeRegister(0x2005, 0)
        self.writeRegister(0x2006, 0, True)
        
        self.scanline = 0
        self.cycle = 0
        
        
        # Pattern memory
        #   0x0000 -> 0x1FFF (8KB)
        # Name Table
        #   0x2000 -> 0x2FFF (2KB)
        # Palettes
        #   0x3F00 -> 0x3FFF
        
        
        # Pattern table 1 = 0x0000 -> 0x0FFF (VRAM)
        # Pattern table 2 = 0x1000 -> 0x1FFF (VRAM)
        
        # Name Table 1 = 0x2000 -> 0x23FF (VRAM)
        # Name Table 2 = 0x2400 -> 0x27FF (VRAM)
        # Name Table 3 = 0x2800 -> 0x2BFF (VRAM)
        # Name Table 4 = 0x2C00 -> 0x2FFF (VRAM)
        
        # Palette Table = 0x3F00 -> 0x3FFF (VRAM)