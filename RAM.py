from BitwiseInts import Int8, UInt8, Int16, UInt16

class RAM:
    def __init__(self, bytesAmount, fillValue=0x0) -> None:
        self.memory = bytearray([fillValue] * bytesAmount)
    
    def readAddress(self, address: UInt16):
        return self.memory[address.value]
    def writeAddress(self, address: UInt16, byte):
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