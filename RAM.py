from BitwiseInts import UInt16

class RAM:
    def __init__(self, console, bytesAmount, fillValue=0x0) -> None:
        self.memory = bytearray([fillValue] * bytesAmount)
        self.console = console
    
    def readAddress(self, address: UInt16):
        # PPU Reading
        addressValue: int = address.value
        if addressValue == 0x2002: return self.console.ppu.readStatusRegister()
        
        if address.value == 0xC28F:
            print(address)
        
        return self.memory[addressValue]
    def writeAddress(self, address: UInt16, byte, fromPPU: bool=False):
        # PPU Writing
        addressValue: int = address.value
        if addressValue >= 0x2000 and addressValue <= 0x2007:
            if fromPPU == False:
                #print(address, byte, hex(byte))
                self.console.ppu.writeRegister(addressValue, byte, fromPPU=False)
            return
        
        self.memory[addressValue] = byte
    

    def readSpace(self, startAddress: UInt16, endAddress: UInt16):
        return self.memory[startAddress.value:endAddress.value]
    def writeSpace(self, startAddress: UInt16, endAddress: UInt16, fillData):
        self.memory[startAddress.value:endAddress.value] = fillData
    
    
    def dumpRAM(self) -> str:
        output = ""
        bytesPerRow = 16
        
        with open("ramDump.cn", "wb") as f:
            f.write(self.memory)
        
        
        for i in range(len(self.memory)):
            decimalValue = self.memory[i]            
            hexValueWithPrefix = hex(decimalValue)
            hexValue = hexValueWithPrefix.split("0x")[1]
            if len(hexValue) == 1: hexValue = f"0{hexValue}"
            if i % bytesPerRow == 0: output += "\n"
            output += hexValue + " "
            
        return output