from BitwiseInts import UInt16

class RAM:
    def __init__(self, console, bytesAmount, fillValue=0x0) -> None:
        self.memory = bytearray([fillValue] * bytesAmount)
        self.console = console
    
    def readAddress(self, address: UInt16):
        if address.value == 0x2002: return self.console.ppu.readStatusRegister()
        return self.memory[address.value]
    def writeAddress(self, address: UInt16, byte):
        if address.value >= 0x2000 and address.value <= 0x200F:
            print(address, byte, hex(byte))
        self.memory[address.value] = byte
    

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