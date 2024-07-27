from BitwiseInts import Int8, UInt8, Int16, UInt16
from RAM import RAM

class Cartridge():
    def __init__(self, filePath: str = "") -> None:
        if filePath == "": raise FileNotFoundError # Please specify a file
        
        self.filePath = filePath
        
        self.PRGMemory: bytearray = bytearray(0)
        self.CHRMemory: bytearray = bytearray(0)
        
        self.mapperID: int = 0
        self.PRGBanks: int = 0
        self.CHRBanks: int = 0
        
        # iNES Header
        self.name: str = "" # len 4 (Should just say NES<eof>)
        self.prgRomChunks: int = 0
        self.chrRomChunks: int = 0
        self.mapper1: int = 0
        self.mapper2: int = 0
        self.prgRamSize: int = 0
        self.tvSystem1: int = 0
        self.tvSystem2: int = 0
        self.unusedBytes: bytearray = bytearray(5)
        
        self.loadFile()
    
    def writePRGToRam(self, RAM: RAM):
        prgAsBytes = bytes(self.PRGMemory)
        
        if self.prgRomChunks == 1:
            RAM.writeSpace(UInt16(0x8000), UInt16(0xBFFF), prgAsBytes)
            RAM.writeSpace(UInt16(0xC000), UInt16(0xFFFF), prgAsBytes)
        elif self.prgRomChunks == 2:
            RAM.writeSpace(UInt16(0x8000), UInt16(0xFFFF), prgAsBytes)
    
    
    
    def loadFile(self):
        with open(self.filePath, "rb") as f:
            header: bytes = f.read(0x10) # read first line, 16 bytes
            
            self.name = header[0:4] # bytes 0 to 3
            self.prgRomChunks = int(header[4]) # amount of 16KB units
            self.chrRomChunks = int(header[5]) # amount of 8KB units   0 means board uses CHR RAM
            self.mapper1 = int(header[6])
            self.mapper2 = int(header[7])
            self.prgRamSize = int(header[8])
            self.tvSystem1 = int(header[9])
            self.tvSystem2 = int(header[10])
            self.unusedBytes = header[11:16] # Bytes 11 to 15

            if self.mapper1 & 0x04:
                f.seek(512)

            self.mapperID = ((self.mapper2 >> 4) << 4) | (self.mapper1 >> 4)
            
            # iNES file format (just 1 for now)
            fileType = 1
            
            if fileType == 0:
                pass
            
            elif fileType == 1:
                self.PRGBanks = self.prgRomChunks
                self.PRGMemory = bytearray(self.PRGBanks * 16384)
                f.readinto(self.PRGMemory)
                
                self.CHRBanks = self.chrRomChunks
                self.CHRMemory = bytearray(self.CHRBanks * 8192)
                f.readinto(self.CHRMemory)
            
            elif fileType == 2:
                pass
            
            f.close()
            