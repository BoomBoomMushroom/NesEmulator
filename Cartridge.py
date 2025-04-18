import os

class Cartridge():
    def __init__(self, romFileLocation=""):
        if romFileLocation == "": return
        if os.path.exists(romFileLocation) == False:
            raise FileNotFoundError(f"ROM file not found! {romFileLocation}")
        
        self.byteOrder = "big"
        self.romPath = romFileLocation
        self.file = None
        
        self.PRGROM_Size = 0 # in 16 KB Units (16384 bytes)
        self.CHRROM_Size = 0 # in 8 KB Units (8192 bytes)
    
        # Flags 6 from INES (see validateROM)
        self.nameTableMirrorDir = 0
        self.hasBatteryBackedRAM = 0
        self.hasTrainer = 0
        self.useAlternativeNameTableLayout = 0
        self.mapperNumber = 0
    
    def validateROM(self):
        # https://www.nesdev.org/wiki/INES
        constant = self.read(4, location=0)
        if constant != b"\x4E\x45\x53\x1A": # (ASCII "NES" followed by MS-DOS end-of-file)
            return False
        
        self.PRGROM_Size = int.from_bytes(self.read(1, location=4), byteorder=self.byteOrder)
        self.CHRROM_Size = int.from_bytes(self.read(1, location=5), byteorder=self.byteOrder)
        # Reverse both to make index 0 the least significant bit
        byteSix = bin(int.from_bytes(self.read(1, location=6), byteorder=self.byteOrder)).replace("0b", "").zfill(8)[::-1]
        byteSeven = bin(int.from_bytes(self.read(1, location=7), byteorder=self.byteOrder)).replace("0b", "").zfill(8)[::-1]
        
        self.mapperNumber = int(f"{byteSeven[4:7+1]}{byteSix[4:7+1]}", 2)
        
        return True
        
    def load(self):
        self.file = open(self.romPath, "rb")
        isValidROM = self.validateROM()
        if isValidROM == False: print("ROM is not valid!")
        
        return isValidROM
    
    def close(self):
        self.file.close()
        return True

    def read(self, numOfBytes, location=0):
        self.file.seek(location, 0)
        data = self.file.read(numOfBytes)
        return data

