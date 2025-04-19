from Memory import Memory

# TODO: Make the PPU

class PPU():
    def __init__(self, memory: Memory):
        self.memory = memory
        
        self.PPUCTRL_Addr = 0x2000
        self.PPUMASK_Addr = 0x2001
        self.PPUSTATUS_Addr = 0x2002
        self.OAMAADDR_Addr = 0x2003
        self.OAMDATA_Addr = 0x2004
        self.PPUSCROLL_Addr = 0x2005
        self.PPUADDR_Addr = 0x2006
        self.PPUDATA_Addr = 0x2007
        self.OAMDMA_Addr = 0x4014
        
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
    
    def powerup(self):
        # https://www.nesdev.org/wiki/PPU_power_up_state
        self.memory.write(self.PPUCTRL_Addr, 0b0000_0000)
        self.memory.write(self.PPUMASK_Addr, 0b0000_0000)
        self.memory.write(self.PPUSTATUS_Addr, 0b1010_0000)
        self.memory.write(self.OAMAADDR_Addr, 0x00)
        
        self.memory.write(self.PPUSCROLL_Addr, 0x0000)
        self.memory.write(self.PPUADDR_Addr, 0x0000)
        self.memory.write(self.PPUDATA_Addr, 0x00)
    
    def reset(self):
        self.memory.write(self.PPUCTRL_Addr, 0b0000_0000)
        self.memory.write(self.PPUMASK_Addr, 0b0000_0000)
        
        self.memory.write(self.PPUSCROLL_Addr, 0x0000)
        self.memory.write(self.PPUDATA_Addr, 0x00)
    
    def tick(self):
        #self.memory.write(self.PPUSTATUS_Addr, 0b1000_0000)
        pass