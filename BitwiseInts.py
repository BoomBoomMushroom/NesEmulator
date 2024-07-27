import time
from line_profiler import LineProfiler

class Int:
    def __init__(self, value=0, bits=8, signed=True, overflowAllowed=True) -> None:
        self.bits = bits
        self.signed = signed
        self.overflowAllowed = overflowAllowed
        self.didOverflow = False
        
        className = type(self).__name__
        self.signed = not ("U" in className)
        self.bits = 16 if "16" in className else 8
        
        bitToPower = (self.bits-1 if self.signed else self.bits)
        if self.signed:
            self.minValueClamping = ((-2 ** bitToPower) + 1) - 1
        else:
            self.minValueClamping = 0
        self.maxValueClamping = (2 ** bitToPower) - 1
        self.offsetClamping = (2 ** self.bits)
        
        #self.value = self.clampValueToRange(value, False, True)
        self.value = self.valueTransformToType(value)

    def getHex(self, prefix=False) -> str:
        hexStr = hex(self.valueToTwosComplementPositiveHex(self.value))
        hexPart = hexStr[2::]
        hexPart.zfill(self.bits // 4)
        hexPart = hexPart.upper()
        if prefix == True: hexPart = "0x" + hexPart
        return hexPart

    def hexToTypeIntValue(self, hex: str) -> int:
        return self.valueTransformToType(int(hex, 16))

    def getWriteableInt(self) -> int:
        return int(self.getHex(), 16)

    def valueTransformToType(self, value):
        #if value < 0: return self.clampValueToRange(value, True, False)
        
        # Convert into binary string and get only the last 8/16 bits (thats whats important)
        bitMask = (1 << self.bits) - 1
        maskedValue = value & bitMask
        
        if self.signed == False:
            return maskedValue
        
        if maskedValue > self.maxValueClamping:
            maskedValue -= (1 << self.bits)
        
        return maskedValue

    def clampValueToRange(self, value, doOverflowCheck=True, firstPast=False) -> int:
        _min = self.minValueClamping
        _max = self.maxValueClamping
        _offset = self.offsetClamping
        
        if value > _max:
            value %= -_offset
            self.didOverflow = doOverflowCheck
            if firstPast: value = _max
            return value

        if value < _min:
            value %= _offset
            self.didOverflow = doOverflowCheck
            if firstPast: value = _min
            return value
        
        return value
    
    def valueToTwosComplementPositiveHex(self, value):
        if value >= 0: return value
        mask = (1 << self.bits) - 1
        value = (mask ^ value) + 1
        value *= -1
        return value
    
    def checkArguments(self, a, b):
        typeA = type(a)
        typeB = type(b)
        
        if typeA == typeB: return b.value
        if typeB == int:
            return b
            #newInt = self.newIntCopy(self, b)
            #return newInt
        
        print(f"{typeA} cannot be paired with {typeB}")
        raise TypeError

    def newIntCopy(self, toCopy, value=0):
        #return type(toCopy)(0, toCopy.bits, toCopy.signed, toCopy.overflowAllowed)
        return type(toCopy)(value, toCopy.overflowAllowed)
    
    def __add__(self, other):
        other = self.checkArguments(self, other)
        value = self.value + other
        newInt = self.newIntCopy(self, value)
        return newInt
    
    def __sub__(self, other):
        other = self.checkArguments(self, other)
        value = self.value - other
        newInt = self.newIntCopy(self, value)
        return newInt
    
    def __mul__(self, other):
        other = self.checkArguments(self, other)
        value = self.value * other
        newInt = self.newIntCopy(self, value)
        return newInt
    
    def __pow__(self, other):
        other = self.checkArguments(self, other)
        value = self.value ** other
        newInt = self.newIntCopy(self, value)
        return newInt
    
    def __lshift__(self, other):
        other = self.checkArguments(self, other)
        valueToBeOperated = self.valueToTwosComplementPositiveHex(self.value)
        value = valueToBeOperated << other
        newInt = self.newIntCopy(self, value)
        return newInt
    
    def __rshift__(self, other):
        other = self.checkArguments(self, other)
        value = self.value >> other
        newInt = self.newIntCopy(self, value)
        return newInt
    
    def __and__(self, other):
        other = self.checkArguments(self, other)
        valueToBeOperated = self.valueToTwosComplementPositiveHex(self.value)
        value = valueToBeOperated & other
        newInt = self.newIntCopy(self, value)
        return newInt
    
    def __or__(self, other):
        other = self.checkArguments(self, other)
        value = self.value | other
        newInt = self.newIntCopy(self, value)
        return newInt
    
    def __xor__(self, other):
        other = self.checkArguments(self, other)
        valueToBeOperated = self.valueToTwosComplementPositiveHex(self.value)
        value = valueToBeOperated ^ other
        newInt = self.newIntCopy(self, value)
        return newInt
    
    def __invert__(self):
        value = ~self.value
        newInt = self.newIntCopy(self, value)
        return newInt
    
    def __neg__(self):
        valueToBeOperated = -abs(self.value)
        value = valueToBeOperated
        newInt = self.newIntCopy(self, value)
        return newInt
    
    def __pos__(self):
        valueToBeOperated = abs(self.value)
        newInt = self.newIntCopy(self, valueToBeOperated)
        return newInt
    
    def __str__(self) -> str:
        return type(self).__name__ + f"({self.value} ~ {self.getHex(True)})"
        #return f"Value: {self.value} ; Hex: {self.getHex(True)} ; Overflow: {self.didOverflow}"

class Int8(Int):
    pass
    #def __init__(self, value=0, overflowAllowed=True) -> None:
    #    super().__init__(value, 8, signed=True, overflowAllowed=overflowAllowed)
class UInt8(Int):
    pass
    #def __init__(self, value=0, overflowAllowed=True) -> None:
    #    super().__init__(value, 8, signed=False, overflowAllowed=overflowAllowed)
class Int16(Int):
    pass
    #def __init__(self, value=0, overflowAllowed=True) -> None:
    #    super().__init__(value, 16, signed=True, overflowAllowed=overflowAllowed)
class UInt16(Int):
    pass
    #def __init__(self, value=0, overflowAllowed=True) -> None:
    #    super().__init__(value, 16, signed=False, overflowAllowed=overflowAllowed)


def toProfile():
    a: UInt8 = UInt8(1293)
    b: UInt8 = UInt8(192)
    
    combined: UInt16 = UInt16(b.value) << 8
    combined |= UInt16(a.value)

if __name__ == "__main__":
    profiler = LineProfiler()
    a: Int8 = Int8(-500, True)
    print(a.maxValueClamping, a.minValueClamping, a.offsetClamping)
    wrapper = profiler(Int(0, 8, True, False).valueTransformToType)
    wrapper(10)
    profiler.print_stats()