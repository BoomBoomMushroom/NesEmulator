# 22 I/O registers (https://en.wikipedia.org/wiki/Ricoh_2A03#:~:text=featuring%20twenty%20two%20memory%2Dmapped%20I/O%20registers)

# High Nibble vs Low Nibble (https://stackoverflow.com/questions/10770735/high-nibble-and-low-nibble-what-are-they#:~:text=Nibble%20is%20half%20a%20byte%20(0%2D15%2C%20or%20one%20hex%20digit).%20Low%20nibble%20are%20the%20bits%200%2D3%3B%20high%20nibble%20are%20bits%204%2D7)
    # Nibble is half a byte (0-15, or one hex digit). Low nibble are the bits 0-3; high nibble are bits 4-7

# Instruction Set (https://en.wikipedia.org/wiki/MOS_Technology_6502#Instruction_table)


# Memory Map
# https://www.nesdev.org/wiki/CPU_memory_map

from BitwiseInts import Int8, UInt8, UInt16
from RAM import RAM

import inspect

class Ricoh2A03:
    def __init__(self, console) -> None:
        
        # Registers
        self.accumulatorRegister = Int8(0)
        self.XRegister = Int8(0)
        self.YRegister = Int8(0)
        self.stackPointer = UInt8(0xFD)
        self.statusRegister = UInt8(0x24)
        self.pc = UInt16(0)
        
        # Flags
        self.negativeFlag = False
        self.overflowFlag = False
        self.ignoredFlag = False
        self.breakFlag = False
        self.decimalModeFlag = False        
        self.interruptDisableFlag = True
        self.zeroFlag = False
        self.carryFlag = False
        self.breakFlag = False # https://www.nesdev.org/wiki/Status_flags#The_B_flag
        
        self.console = console
        self.RAM: RAM = self.console.ram
        self.queuedClockCycles = 0
        
        self.opcodes = {
            0x00: self.empty,
            0x01: self.IndirectX_ORA,
            0x05: self.ZeropageORA,
            0x06: self.ZeropageASL,
            0x08: self.PHP,
            0x09: self.ImmediateORA,
            0x0A: self.AccumulatorASL,
            0x0D: self.AbsoluteORA,
            0x0E: self.AbsoluteASL,
            
            0x10: self.BPL,
            0x11: self.IndirectY_ORA,
            0x15: self.ZeropageX_ORA,
            0x16: self.ZeropageX_ASL,
            0x18: self.CLC,
            0x19: self.AbsoluteY_ORA,
            0x1D: self.AbsoluteX_ORA,
            0x1E: self.AbsoluteX_ASL,
            
            0x20: self.JSR,
            0x21: self.IndirectX_AND,
            0x24: self.ZeropageBIT,
            0x25: self.ZeropageAND,
            0x26: self.ZeropageROL,
            0x28: self.PLP,
            0x29: self.ImmediateAND,
            0x2A: self.AccumulatorROL,
            0x2C: self.AbsoluteBIT,
            0x2D: self.AbsoluteAND,
            0x2E: self.AbsoluteROL,
            
            0x30: self.BMI,
            0x31: self.IndirectY_AND,
            0x35: self.ZeropageX_AND,
            0x36: self.ZeropageX_ROL,
            0x38: self.SEC,
            0x39: self.AbsoluteY_AND,
            0x3D: self.AbsoluteX_AND,
            0x3E: self.AbsoluteX_ROL,
            
            0x40: self.RTI,
            0x41: self.IndirectX_EOR,
            0x45: self.ZeropageEOR,
            0x46: self.ZeropageLSR,
            0x48: self.PHA,
            0x49: self.ImmediateEOR,
            0x4A: self.AccumulatorLSR,
            0x4C: self.AbsoluteJMP,
            0x4D: self.AbsoluteEOR,
            0x4E: self.AbsoluteLSR,
            
            0x50: self.BVC,
            0x51: self.IndirectY_EOR,
            0x55: self.ZeropageX_EOR,
            0x56: self.ZeropageX_LSR,
            #0x58:
            0x59: self.AbsoluteY_EOR,
            0x5D: self.AbsoluteX_EOR,
            0x5E: self.AbsoluteX_LSR,
            
            0x60: self.RTS,
            0x61: self.IndirectX_ADC,
            0x65: self.ZeropageADC,
            0x66: self.ZeropageROR,
            0x68: self.PLA,
            0x69: self.ImmediateADC,
            0x6A: self.AccumulatorROR,
            0x6C: self.IndirectJMP,
            0x6D: self.AbsoluteADC,
            0x6E: self.AbsoluteROR,
            
            0x70: self.BVS,
            0x71: self.IndirectY_ADC,
            0x75: self.ZeropageX_ADC,
            0x76: self.ZeropageX_ROR,
            0x78: self.SEI,
            0x79: self.AbsoluteY_ADC,
            0x7D: self.AbsoluteX_ADC,
            0x7E: self.AbsoluteX_ROR,
            
            0x81: self.IndirectX_STA,
            0x84: self.ZeropageSTY,
            0x85: self.ZeropageSTA,
            0x86: self.ZeropageSTX,
            0x88: self.DEY,
            0x8A: self.TXA,
            0x8C: self.AbsoluteSTY,
            0x8D: self.AbsoluteSTA,
            0x8E: self.AbsoluteSTX,
            
            0x90: self.BCC,
            0x91: self.IndirectY_STA,
            0x94: self.ZeropageX_STY,
            0x95: self.ZeropageX_STA,
            0x96: self.ZeropageY_STX,
            0x98: self.TYA,
            0x99: self.AbsoluteY_STA,
            0x9A: self.TXS,
            0x9D: self.AbsoluteX_STA,
            
            0xA0: self.ImmediateLDY,
            0xA1: self.IndirectX_LDA,
            0xA2: self.ImmediateLDX,
            0xA4: self.ZeropageLDY,
            0xA5: self.ZeropageLDA,
            0xA6: self.ZeropageLDX,
            0xA8: self.TAY,
            0xA9: self.ImmediateLDA,
            0xAA: self.TAX,
            0xAC: self.AbsoluteLDY,
            0xAD: self.AbsoluteLDA,
            0xAE: self.AbsoluteLDX,
            
            0xB0: self.BCS,
            0xB1: self.IndirectY_LDA,
            0xB4: self.ZeropageX_LDY,
            0xB5: self.ZeropageX_LDA,
            0xB6: self.ZeropageY_LDX,
            0xB8: self.CLV,
            0xB9: self.AbsoluteY_LDA,
            0xBA: self.TSX,
            0xBC: self.AbsoluteX_LDY,
            0xBD: self.AbsoluteX_LDA,
            0xBE: self.AbsoluteY_LDX,
            
            0xC0: self.ImmediateCPY,
            0xC1: self.IndirectX_CMP,
            0xC4: self.ZeropageCPY,
            0xC5: self.ZeropageCMP,
            0xC6: self.ZeropageDEC,
            0xC8: self.INY,
            0xC9: self.ImmediateCMP,
            0xCA: self.DEX,
            0xCC: self.AbsoluteCPY,
            0xCD: self.AbsoluteCMP,
            0xCE: self.AbsoluteDEC,
            
            0xD0: self.BNE,
            0xD1: self.IndirectY_CMP,
            0xD5: self.ZeropageX_CMP,
            0xD6: self.ZeropageX_DEC,
            0xD8: self.CLD,
            0xD9: self.AbsoluteY_CMP,
            0xDD: self.AbsoluteX_CMP,
            0xDE: self.AbsoluteX_DEC,
            
            0xE0: self.ImmediateCPX,
            0xE1: self.IndirectX_SBC,
            0xE4: self.ZeropageCPX,
            0xE5: self.ZeropageSBC,
            0xE6: self.ZeropageINC,
            0xE8: self.INX,
            0xE9: self.ImmediateSBC,
            0xEA: self.NOP,
            0xEC: self.AbsoluteCPX,
            0xED: self.AbsoluteSBC,
            0xEE: self.AbsoluteINC,
            0xF0: self.BEQ,
            
            0xF1: self.IndirectY_SBC,
            0xF5: self.ZeropageX_SBC,
            0xF6: self.ZeropageX_INC,
            0xF8: self.SED,
            0xF9: self.AbsoluteY_SBC,
            0xFD: self.AbsoluteX_SBC,
            0xFE: self.AbsoluteX_INC,
            
            0xA3: self.IllegalIndirectX_LAX,
            0xA7: self.IllegalZeropageLAX,
            0xAF: self.IllegalAbsoluteLAX,
            0xB3: self.IllegalIndirectY_LAX,
            0xB7: self.IllegalZeropageY_LAX,
            0xBF: self.IllegalAbsoluteY_LAX,
            0x83: self.IllegalIndirectX_SAX,
            0x87: self.IllegalZeropageSAX,
            0x8F: self.IllegalAbsoluteSAX,
            0x97: self.IllegalZeropageY_SAX,
            
            0xC3: self.IllegalIndirectX_DCP,
            0xC7: self.IllegalZeropageDCP,
            0xCF: self.IllegalAbsoluteDCP,
            0xD3: self.IllegalIndirectY_DCP,
            0xD7: self.IllegalZeropageX_DCP,
            0xDB: self.IllegalAbsoluteY_DCP,
            0xDF: self.IllegalAbsoluteX_DCP,
            
            0xE3: self.IllegalIndirectX_ISB,
            0xE7: self.IllegalZeropageISB,
            0xEF: self.IllegalAbsoluteISB,
            0xF3: self.IllegalIndirectY_ISB,
            0xF7: self.IllegalZeropageX_ISB,
            0xFB: self.IllegalAbsoluteY_ISB,
            0xFF: self.IllegalAbsoluteX_ISB,
            
            0x03: self.IllegalIndirectX_SLO,
            0x07: self.IllegalZeropageSLO,
            0x0F: self.IllegalAbsoluteSLO,
            0x13: self.IllegalIndirectY_SLO,
            0x17: self.IllegalZeropageX_SLO,
            0x1B: self.IllegalAbsoluteY_SLO,
            0x1F: self.IllegalAbsoluteX_SLO,
            
            0x23: self.IllegalIndirectX_RLA,
            0x27: self.IllegalZeropageRLA,
            0x2F: self.IllegalAbsoluteRLA,
            0x33: self.IllegalIndirectY_RLA,
            0x37: self.IllegalZeropageX_RLA,
            0x3B: self.IllegalAbsoluteY_RLA,
            0x3F: self.IllegalAbsoluteX_RLA,
            
            0x43: self.IllegalIndirectX_SRE,
            0x47: self.IllegalZeropageSRE,
            0x4F: self.IllegalAbsoluteSRE,
            0x53: self.IllegalIndirectY_SRE,
            0x57: self.IllegalZeropageX_SRE,
            0x5B: self.IllegalAbsoluteY_SRE,
            0x5F: self.IllegalAbsoluteX_SRE,
            
            0x63: self.IllegalIndirectX_RRA,
            0x67: self.IllegalZeropageRRA,
            0x6F: self.IllegalAbsoluteRRA,
            0x73: self.IllegalIndirectY_RRA,
            0x77: self.IllegalZeropageX_RRA,
            0x7B: self.IllegalAbsoluteY_RRA,
            0x7F: self.IllegalAbsoluteX_RRA,
            
            
            0xEB: self.IllegalSBC,
            0x1A: self.IllegalNOP_OneByte,
            0x3A: self.IllegalNOP_OneByte,
            0x5A: self.IllegalNOP_OneByte,
            0x7A: self.IllegalNOP_OneByte,
            0xDA: self.IllegalNOP_OneByte,
            0xFA: self.IllegalNOP_OneByte,
            
            0x80: self.IllegalNOP_TwoByte,
            0x82: self.IllegalNOP_TwoByte,
            0x89: self.IllegalNOP_TwoByte,
            0xC2: self.IllegalNOP_TwoByte,
            0xE2: self.IllegalNOP_TwoByte,
            0x04: self.IllegalNOP_TwoByte,
            0x44: self.IllegalNOP_TwoByte,
            0x64: self.IllegalNOP_TwoByte,
            0x14: self.IllegalNOP_TwoByte,
            0x34: self.IllegalNOP_TwoByte,
            0x54: self.IllegalNOP_TwoByte,
            0x74: self.IllegalNOP_TwoByte,
            0xD4: self.IllegalNOP_TwoByte,
            0xF4: self.IllegalNOP_TwoByte,
            
            0x0C: self.IllegalNOP_ThreeByte,
            0x1C: self.IllegalNOP_ThreeByte,
            0x3C: self.IllegalNOP_ThreeByte,
            0x5C: self.IllegalNOP_ThreeByte,
            0x7C: self.IllegalNOP_ThreeByte,
            0xDC: self.IllegalNOP_ThreeByte,
            0xFC: self.IllegalNOP_ThreeByte,
        }
        
        #self.doPrint = True
        self.doPrint = False
        
        self.nestestWithoutPPU = False
        self.nestestWithoutPPUStopAddress = 0x0800
        
        self.haltAllExecutionBecauseOfNoInstruction = False
        self.outputLog = ""
    
    def loadRom(self, rom):
        romLength = len(rom)

        # skip the 16 byte header
        romNoHeaders = rom[0x10:]
        romNoHeaderLen = len(romNoHeaders)
        
        # Load PRG ROM into memory at 0x8000
        self.RAM.writeSpace(UInt16(0x8000), UInt16(0x8000) + romLength, rom)
        
        # Mirror PRG ROM to 0xC000 for simple ROMs
        self.RAM.writeSpace(UInt16(0xC000), UInt16(0xC000) + romNoHeaderLen, romNoHeaders)
        
    def reset(self):
        # RESET VECTOR
        lowByte = self.readByte(UInt16(0xFFFC))
        highByte = self.readByte(UInt16(0xFFFD))
        
        # Set the PC to the address found at the reset vector
        if self.nestestWithoutPPU:
            self.stackPointer = UInt8(0xFF)
            self.pushStackPointer(0x08) # 0x0800
            self.pushStackPointer(0x00)
            self.pc = UInt16(0xC000)
        else:
            self.pc = self.combineTwoBytesToOneAddress(highByte, lowByte)
    
    
    def step(self):
        if self.queuedClockCycles > 0:
            self.queuedClockCycles -= 1
            return 0
        
        if self.haltAllExecutionBecauseOfNoInstruction: return -1
        if self.pc == None:
            if self.doPrint: print("Program Counter is null! This usually means the ROM wasn't loaded")
            return -1
        
        if self.nestestWithoutPPU:
            if self.pc.getWriteableInt() == self.nestestWithoutPPUStopAddress:
                print("Nestest is done testing...")
                return -1
        
        instructionHex: Int8 = self.readInstruction()
        instructionFunction = self.decodeInstruction(instructionHex)
        
        if instructionFunction == -1:
            if self.doPrint: print("Illegal Opcode")
            self.pc += 0x1
            instructionFunction = None
            return
        if instructionFunction == None:
            if self.doPrint: print(f"Something went wrong! An instruction doesn't seem to have a function! PC: {self.pc.getHex()}; instruction: {instructionHex}")
            self.haltAllExecutionBecauseOfNoInstruction = True
            return
        
        self.queuedClockCycles += instructionFunction()
        
        self.pc += 0x1
        
        self.updateStatusRegister()
    
    def updateStatusRegister(self) -> None:
        # https://www.nesdev.org/wiki/Status_flags
        flagString = "0b"
        flagString += "1" if self.negativeFlag else "0"
        flagString += "1" if self.overflowFlag else "0"
        flagString += "1"
        flagString += "1" if self.breakFlag else "0"
        flagString += "1" if self.decimalModeFlag else "0"
        flagString += "1" if self.interruptDisableFlag else "0"
        flagString += "1" if self.zeroFlag else "0"
        flagString += "1" if self.carryFlag else "0"
        
        self.statusRegister = UInt8(int(flagString, 2))
    
    def setFlagsFromStatusRegister(self, statusRegister: UInt8):
        binary = bin(statusRegister.value).split("0b")[1]
        while len(binary) < 8: binary = "0" + binary
        
        self.negativeFlag = binary[0] == "1"
        self.overflowFlag = binary[1] == "1"
        #unused = binary[2]
        self.breakFlag = binary[3] == "1"
        self.decimalModeFlag = binary[4] == "1"
        self.interruptDisableFlag = binary[5] == "1"
        self.zeroFlag = binary[6] == "1"
        self.carryFlag = binary[7] == "1"
    
    def readInstruction(self) -> UInt8:
        return self.readByte(self.pc)
    
    def readByte(self, address: UInt16) -> UInt8:
        byte = self.RAM.readAddress(address)
        return UInt8(byte)
    
    def addToOutputLog(self, message) -> None:
        self.outputLog += message + "\n"
    
    def logInstruction(self, opcode: str, instructionName: str, operand1: str = "  ", operand2: str = "  ", instructionParameter: str = "    ", isIllegal=False):
        startRegistersLen = 48
        
        isIllegalChar = "*" if isIllegal else " "
        pt1 = f"{self.pc.getHex()}  {opcode} {operand1} {operand2} {isIllegalChar}{instructionName} {instructionParameter}"
        while len(pt1) < startRegistersLen:
            pt1 += " "
        
        self.addToOutputLog(pt1 + self.registerStatesString())
    
    
    def disassembleInstructions(self, startAddress: int = 0, endAddress: int = 0):
        if type(startAddress) != int: startAddress = startAddress.value
        if type(endAddress) != int: endAddress = endAddress.value
        
        while startAddress < endAddress:
            address: UInt16 = UInt16(startAddress)
            opcode = self.readByte(address)
            try:
                opcodeHex = opcode.getHex()
                func = self.opcodes[opcode.getWriteableInt()]
                
                
                src = inspect.getsource(func)
                bytesReadOntopOfPC = src.count("self.pc + 0x")
                operands = ""

                for i in range(1, bytesReadOntopOfPC):
                    operand = self.readByte(address + i)
                    operands += f" {operand.getHex()}"

                startAddress += bytesReadOntopOfPC
                print(f"${address.getHex()}: ({opcodeHex}) {func.__name__}{operands}")
            except:
                pass

            startAddress += 1
    
    def updateNegativeFlag(self, value: Int8, getResult = False) -> None:
        newValue: bool = (value.value & 0x80) != 0
        if getResult: return newValue
        self.negativeFlag = (value.value & 0x80) != 0
    
    def updateZeroFlag(self, value: Int8, getResult = False) -> None:
        newValue: bool = value.value == 0
        if getResult: return newValue
        self.zeroFlag = newValue
    
    # Implied Addressing:
    #   use the accumulator register to hold data
    #   No operands! (instructions that comprise only an opcode without an operand) [https://www.google.com/search?q=implied+addressing+mode]
    
    # Absolute Addressing:
    #   2 bytes (low byte, high byte) after the opcode 
    #   example LDA 0xC000 (Load Accumulator) ~ load data from 0xC000 into accumulator register
    
    # Absolute, Y-Index Addressing:
    #   Similar to absolute but the address is modified by the Y register
    #   address + Y (with carry); Ex. LDA, 0xC000,Y ~ load data from 0xC000 + value in Y register
    
    # Immediate Addressing:
    #   operand is encoded directly after the opcode (usually 1 byte)
    #   Ex. LDA 0xFF ~ loads 0xFF aka 255 into the accumulator register
    
    # Indirect Addressing:
    #   operand's address is stored at a memory address specified after the opcode (2 bytes)
    #   Ex. LDA 0xC000 ~ Reads data from address 0xC000 and loads it into the accumulator register
    
    # Zero Page Addressing:
    #   Address is encoded directly after the opcode (1 byte)
    #   high vs low byte. ex. address 0xFF77 ; FF is the high byte and 77 is the low byte
    #   high byte is assumed to be 00 (address range 0x0000 to 0x00FF)
    #   Ex. LDA 0xFF ~ loads data from address 0x00FF into the accumulator register
    
    # Zero Page, X-Index Addressing:
    #   Address is made by adding the zero page address to the value in the X register
    #   ex. LDA 0xFF ~ loads data from 0xFF + X into the accumulator register
    
    # Relative Addressing:
    #   Signed offset (1 byte) immediately after the opcode
    #   Ex. BEQ 0x10 (branch if equal) ~ jumps to the instruction 10 bytes ahead if the zero flag is set (indicating equality)
    
    # Indirect, X-Index Addressing:
    #   Zero page address + X which points to the address of the value
    #   Ex. LDA 0x73 ~ 0x73 + X (ex. 12) -> 0x85
    #   Fetch 2 bytes, one at 0x85 and another at 0x85 + 0x1 (0x86) to form a 16 bit (2 byte address)
    #   that 2 byte address is used to get the value
    
    # Indirect Y-Index Addressing:
    #   Same as Indirect, X-Index Addressing but add Y instead of X
    
    
    
    # Finish the addressing learning here (https://gemini.google.com/app/562f75670af265e6)
    
    def registerStatesString(self) -> str:
        return f"A:{self.accumulatorRegister.getHex()} X:{self.XRegister.getHex()} Y:{self.YRegister.getHex()} P:{self.statusRegister.getHex()} SP:{self.stackPointer.getHex()} PPU: NOT IMPLEMENTED YET"
    
    def combineTwoBytesToOneAddress(self, highByte: UInt8, lowByte: UInt8) -> UInt16:        
        combined: UInt16 = UInt16(highByte.value) << 8
        combined |= UInt16(lowByte.value)
        return combined
    
    # Stack Pointer Handling
    def getStackPointerAddress(self) -> UInt16:
        # The stack is located in the memory addresses from "0x0100" to "0x01FF"
        address: UInt16 = UInt16(0x0100 + self.stackPointer.value)
        return address
    def popStackPointer(self):
        self.stackPointer += 0x1
        address: UInt16 = self.getStackPointerAddress()
        return self.RAM.readAddress(address)
    def pushStackPointer(self, data):
        address: UInt16 = self.getStackPointerAddress()
        self.RAM.writeAddress(address, data)
        self.stackPointer -= 0x1
    
    def intToBinaryString(self, value: Int8 | UInt8) -> str:
        intValue: int = value.getWriteableInt()
        binary: str = bin(intValue).split("0b")[1]
        while len(binary) < 8: binary = f"0{binary}"
        return binary
     
    def LAX(self, value: UInt8):
        self.accumulatorRegister = value
        #self.updateNegativeFlag(self.accumulatorRegister)
        #self.updateZeroFlag(self.accumulatorRegister)
        
        self.XRegister = value
        self.updateNegativeFlag(self.XRegister)
        self.updateZeroFlag(self.XRegister)
    
    # MAJOR HANDLE FUNCTION
    
    def compareValues(self, valueA: Int8, valueB: Int8):
        valueA1: str = self.intToBinaryString(valueA)
        valueB1: str = self.intToBinaryString(valueB)
        
        # This code is fragile. Dont touch?
        
        inverseB = ""
        for char in valueB1: inverseB += "1" if char == "0" else "0"
        
        negativeB = ""
        carry = 0
        
        one = "00000001"
        
        for i in range(7, -1, -1):
            r = carry
            r += 1 if inverseB[i] == "1" else 0
            r += 1 if one[i] == "1" else 0
            negativeB = ('1' if r % 2 == 1 else "0") + negativeB
            carry = 0 if r < 2 else 1
        
        result = ""
        carry = 0
        
        for i in range(7, -1, -1):
            r = carry
            r += 1 if valueA1[i] == "1" else 0
            r += 1 if negativeB[i] == "1" else 0
            result = ('1' if r % 2 == 1 else "0") + result
            carry = 0 if r < 2 else 1
        
        
        output = int(result, 2)
        
        compareOutput: Int8 = Int8(output)
        
        #unsignedA: UInt8 = UInt8(int(f"0x{valueA.getHex()}", 16))
        #unsignedB: UInt8 = UInt8(int(f"0x{valueB.getHex()}", 16))
        
        unsignedA: int = valueA.getWriteableInt()
        unsignedB: int = valueB.getWriteableInt()
        
        negativeFlag = False
        
        if output < 0:
            negativeFlag = True
        else:
            negativeFlag = self.updateNegativeFlag(compareOutput, True)
        zeroFlag = self.updateZeroFlag(compareOutput, True)
        
        carryFlag = unsignedA >= unsignedB
        
        return (compareOutput, negativeFlag, zeroFlag, carryFlag)
    
    def AND_Values(self, valueA: Int8 | int, valueB: Int8 | int):
        return valueA & valueB
    
    def LDA(self, address: UInt16):
        value: UInt8 = self.readByte(address)
        self.accumulatorRegister = value
    
    def STA(self, address: UInt16):
        self.RAM.writeAddress(address, self.accumulatorRegister.getWriteableInt())
    
    def ORA(self, A: UInt8, B: UInt8):
        return A | B
    
    def EOR(self, A: UInt8, B: UInt8):
        return A ^ B
    
    def ADC(self, A: UInt8, B: UInt8, carryFlag: bool = False):
        carryInt: int = 1 if carryFlag else 0
        
        accumulatorVal: int = A.value
        operandVal: int = B.value
        
        result: int = accumulatorVal + operandVal + carryInt
        resultInt8: UInt8 = UInt8(result)
        
        if ((accumulatorVal ^ operandVal) & 0x80) == 0 and ((accumulatorVal ^ result) & 0x80) != 0:
            overflowFlag = True
        else:
            overflowFlag = False
        
        carryFlag = result > 0xFF
        negativeFlag = (result >> 7 & 1) == 1
        zeroFlag = resultInt8.value == 0
        
        return resultInt8, carryFlag, negativeFlag, zeroFlag, overflowFlag
    
    def SBC(self, A: UInt8, B: UInt8, carryFlag: bool = False):
        # ChatGPT I would die for you!
        # Thank you for the WORKING code!
        # Prompt 1: can you help me subtract 2 binary string numbers in python. the binary numbers are each strings of 8 "1"s or "0"s I also need flags to check if the result at the end is negative, zero, overflowed and a carry this is for my 6502 cpu emulator
        # Prompt 2: can you modify the code above to include the carry flag? on the datasheet it says sbc's formula is \n A - M - C^- -> A \n So i tihnk accumulator (num1) minus operand (num2) minus the opposite of the carry flag.
        
        aBinary = self.intToBinaryString(A)
        bBinary = self.intToBinaryString(B)
        
        
        numA: int = int(aBinary, 2)
        numB: int = int(bBinary, 2)
        carry: int = 1 if carryFlag else 0
        
        result = numA - numB - (1-carry)
        
        negativeFlag = (result & 0b10000000) != 0
        zeroFlag = result == 0
        overflowFlag = False
        if ((numA ^ numB) & 0b10000000) != 0:
            if ((numA & 0b10000000) != (result & 0b10000000)):
                overflowFlag = True
        
        carryFlag = numA >= numB + (1 - carry)
        accumulatorRegister = Int8(result)
        
        return accumulatorRegister, negativeFlag, zeroFlag, overflowFlag, carryFlag
    
    def LSR(self, A: UInt8):
        carryFlag = bin(A.getWriteableInt())[-1] == "1"
        A >>= 1
        negativeFlag = False
        zeroFlag = A.value == 0
        return A, carryFlag, negativeFlag, zeroFlag
    
    def ASL(self, A: UInt8):
        carryFlag = ((A.getWriteableInt() >> 7) & 1) == 1
        A <<= 1
        
        negativeFlag = self.updateNegativeFlag(A, True)
        zeroFlag = self.updateZeroFlag(A, True)
        return A, carryFlag, negativeFlag, zeroFlag
    
    def ROR(self, A: UInt8, carryFlag: bool = False):
        carry: int = 1 if carryFlag else 0
        newCarry: bool = A.getWriteableInt() & 0x01 == 1 # new carry is lsb of accumulator
        
        newAccumulator: int = (A.getWriteableInt() >> 1) | (carry << 7)
        A = Int8(newAccumulator)
        
        negativeFlag = self.updateNegativeFlag(A, True)
        zeroFlag = self.updateZeroFlag(A, True)
        return A, newCarry, negativeFlag, zeroFlag
    
    def ROL(self, A: UInt8, carryFlag: bool = False):
        carry: int = 1 if carryFlag else 0
        # new carry is msb of accumulator
        newCarry: bool = bin(A.getWriteableInt()).split("0b")[1].zfill(8)[0] == "1"
        
        newAccumulator: int = (A.getWriteableInt() << 1) | carry
        A = Int8(newAccumulator)
        
        carryFlag = newCarry == 1
        negativeFlag = self.updateNegativeFlag(A, True)
        zeroFlag = self.updateZeroFlag(A, True)
        return A, carryFlag, negativeFlag, zeroFlag
    
    def BIT(self, A: UInt8, B: UInt8):
        andValue: Int8 = B & A.value

        negativeFlag = self.updateNegativeFlag(B, True)
        overflowFlag =self.overflowFlag = (B.value & 0x40) != 0
        zeroFlag = self.updateZeroFlag(andValue, True)
        return andValue, negativeFlag, overflowFlag, zeroFlag
    
    # OPCODE FUNCTIONS
    
    def AbsoluteJMP(self) -> int:
        PCL: UInt8 = self.readByte(self.pc + 0x1)
        PCH: UInt8 = self.readByte(self.pc + 0x2)
        address: UInt16 = self.combineTwoBytesToOneAddress(PCH, PCL)
        
        self.logInstruction(self.readByte(self.pc).getHex(), "JMP", PCL.getHex(), PCH.getHex(), f"${address.getHex()}")
        
        self.pc = address - 0x1 # Remove 1 so that when the PC increments it cancels out
        
        return 3 # 3 clock cycles
    
    def ImmediateLDX(self) -> int:
        operand: Int8 = self.readByte(self.pc + 0x1)

        self.logInstruction(self.readByte(self.pc).getHex(), "LDX", operand.getHex(), instructionParameter=f"#${operand.getHex()}")

        self.XRegister = operand
        
        self.updateZeroFlag(self.XRegister)
        self.updateNegativeFlag(self.XRegister)
        
        self.pc += 0x1
        
        return 2
    
    def ZeropageSTX(self):
        operand: UInt16 = self.readByte(self.pc + 0x1)
        oldValue = self.readByte(operand)
        self.RAM.writeAddress(operand, self.XRegister.getWriteableInt())
        
        self.logInstruction(self.readByte(self.pc).getHex(), "STX", operand.getHex(), instructionParameter=f"${operand.getHex()} = {oldValue.getHex()}")
        
        self.pc += 0x1
        return 3
    
    def JSR(self) -> int:
        PCL: UInt8 = self.readByte(self.pc + 0x1)
        PCH: UInt8 = self.readByte(self.pc + 0x2)
        address: UInt16 = self.combineTwoBytesToOneAddress(PCH, PCL) - 0x1 # Remove 1 so that when the PC increments it cancels out
        
        returnAddressToPush: UInt16 = self.pc + 0x2
        
        lowByteReturnAddr: UInt16 = returnAddressToPush & 0xFF
        highByteReturnAddr: UInt16 = returnAddressToPush >> 8

        self.logInstruction(self.readByte(self.pc).getHex(), "JSR", PCL.getHex(), PCH.getHex(), instructionParameter=f"${(address+1).getHex()}")

        self.pushStackPointer( UInt8(highByteReturnAddr.value).value ) # High Byte
        self.pushStackPointer( UInt8(lowByteReturnAddr.value).value )  # Low Byte
        
        self.pc = address
        return 6
    
    def NOP(self) -> int:
        self.logInstruction(self.readByte(self.pc).getHex(), "NOP")
        return 2
        
    def SEC(self) -> int:
        self.carryFlag = True
        self.logInstruction(self.readByte(self.pc).getHex(), "SEC")
        return 2
    
    def BCS(self) -> int:
        operand: Int8 = self.readByte(self.pc + 0x1)
        
        self.logInstruction(self.readByte(self.pc).getHex(), "BCS", operand.getHex(), instructionParameter=f"${(self.pc+operand.value+2).getHex()}")
        
        if self.carryFlag == True:
            self.pc += operand.value
        
        self.pc += 0x1
        return 2
    
    def CLC(self):
        self.carryFlag = False
        self.logInstruction(self.readByte(self.pc).getHex(), "CLC")
        return 2
    
    def BCC(self):
        operand: Int8 = self.readByte(self.pc + 0x1)
        addressIfBranched: UInt16 = self.pc + operand.value
        
        self.logInstruction(self.readByte(self.pc).getHex(), "BCC", operand.getHex(), instructionParameter=f"${(addressIfBranched+2).getHex()}")
        
        if self.carryFlag == False:
            self.pc = addressIfBranched
        
        self.pc += 0x1
        return 2
    
    def ImmediateLDA(self):
        operand: Int8 = self.readByte(self.pc + 0x1)

        self.logInstruction(self.readByte(self.pc).getHex(), "LDA", operand.getHex(), instructionParameter=f"#${operand.getHex()}")
        
        self.accumulatorRegister = operand
        
        self.updateZeroFlag(self.accumulatorRegister)
        self.updateNegativeFlag(self.accumulatorRegister)
        
        self.pc += 0x1
        return 2
    
    def BEQ(self):
        operand: Int8 = self.readByte(self.pc + 0x1)
        addressIfBranched: UInt16 = self.pc + operand.value
        self.logInstruction(self.readByte(self.pc).getHex(), "BEQ", operand.getHex(), instructionParameter=f"${(addressIfBranched+2).getHex()}")

        if self.zeroFlag == True:
            self.pc = addressIfBranched
        
        self.pc += 0x1
        return 2
    
    def BNE(self):
        operand: Int8 = Int8(self.readByte(self.pc + 0x1).value)
        addressIfBranched: UInt16 = self.pc + operand.value
        
        self.logInstruction(self.readByte(self.pc).getHex(), "BNE", operand.getHex(), instructionParameter=f"${(addressIfBranched+2).getHex()}")
        if self.zeroFlag == False:
            self.pc = addressIfBranched
        
        
        self.pc += 0x1
        return 2
    
    def ZeropageSTA(self):
        operand: UInt8 = self.readByte(self.pc + 0x1)
        oldValue: UInt8 = self.readByte(operand)
        
        self.STA(operand)
        
        self.logInstruction(self.readByte(self.pc).getHex(), "STA", operand.getHex(), instructionParameter=f"${operand.getHex()} = {oldValue.getHex()}")
        
        self.pc += 0x1
        return 3
    
    def ZeropageBIT(self):
        operand: Int8 = self.readByte(self.pc + 0x1)
        valueToTest: UInt8 = self.readByte(UInt16(operand.value))

        self.logInstruction(self.readByte(self.pc).getHex(), "BIT", operand.getHex(), instructionParameter=f"${operand.getHex()} = {valueToTest.getHex()}")
        
        andValue, negativeFlag, overflowFlag, zeroFlag = self.BIT(self.accumulatorRegister, valueToTest)
        self.negativeFlag = negativeFlag
        self.overflowFlag = overflowFlag
        self.zeroFlag = zeroFlag
        
        self.pc += 0x1
        
        return 3
    
    def BVS(self):
        offset: Int8 = self.readByte(self.pc + 0x1)
        newAddressIfBranched: UInt16 = self.pc + offset.value
        
        self.logInstruction(self.readByte(self.pc).getHex(), "BVS", offset.getHex(), instructionParameter=f"${(newAddressIfBranched+2).getHex()}")
        
        if self.overflowFlag == True:
            self.pc = newAddressIfBranched
        
        self.pc += 0x1
        return 2
    
    def BVC(self):
        offset: Int8 = self.readByte(self.pc + 0x1)
        newAddressIfBranch: UInt16 = self.pc + offset.value
        
        self.logInstruction(self.readByte(self.pc).getHex(), "BVC", offset.getHex(), instructionParameter=f"${(newAddressIfBranch + 2).getHex()}")
        
        if self.overflowFlag == False:
            self.pc = newAddressIfBranch
        
        self.pc += 0x1
        return 2
    
    def BPL(self):
        offset: Int8 = Int8(self.readByte(self.pc + 0x1).value)
        newAddressIfBranch: UInt16 = self.pc + offset.value
        
        self.logInstruction(self.readByte(self.pc).getHex(), "BPL", offset.getHex(), instructionParameter=f"${(newAddressIfBranch + 2).getHex()}")
        
        if self.negativeFlag == False:
            self.pc = newAddressIfBranch
        
        self.pc += 0x1
        return 2
    
    def RTS(self):
        self.logInstruction(self.readByte(self.pc).getHex(), "RTS")

        lowByte: UInt8 = UInt8(self.popStackPointer())
        highByte: UInt8 = UInt8(self.popStackPointer())
        returnAddress = self.combineTwoBytesToOneAddress(highByte, lowByte)
        
        self.pc = returnAddress
        
        return 6
    
    def SEI(self):
        self.logInstruction(self.readByte(self.pc).getHex(), "SEI")

        self.interruptDisableFlag = True
        return 2
    
    def SED(self):
        self.logInstruction(self.readByte(self.pc).getHex(), "SED")
        
        self.decimalModeFlag = True
        return 2
    
    def PHP(self):
        self.logInstruction(self.readByte(self.pc).getHex(), "PHP")
        
        currentStatus: UInt8 = self.statusRegister
        statusToPush: UInt8 = currentStatus | 0x30
        self.pushStackPointer(statusToPush.value)
                        
        return 3
    
    def PLA(self):
        self.logInstruction(self.readByte(self.pc).getHex(), "PLA")
        
        valueOnStack: int = self.popStackPointer()
        self.accumulatorRegister = Int8(valueOnStack)
        
        self.updateNegativeFlag(self.accumulatorRegister)
        self.updateZeroFlag(self.accumulatorRegister)
        
        return 4
    
    def ImmediateAND(self):
        operand = self.readByte(self.pc + 0x1)
        value: int = operand.value
        
        self.logInstruction(self.readByte(self.pc).getHex(), "AND", self.readByte(self.pc+0x1).getHex(), instructionParameter=f"#${self.readByte(self.pc+0x1).getHex()}")
        
        andResult = self.AND_Values(self.accumulatorRegister, value)
        self.accumulatorRegister = andResult
        
        self.updateNegativeFlag(self.accumulatorRegister)
        self.updateZeroFlag(self.accumulatorRegister)
        
        self.pc += 0x1
        return 2
    
    def ImmediateCMP(self):
        operand: UInt8 = self.readByte(self.pc + 0x1)
        valueToCompare = operand.value
        
        compareResult, negativeFlag, zeroFlag, carryFlag = self.compareValues(self.accumulatorRegister, Int8(valueToCompare))
        
        self.negativeFlag = negativeFlag
        self.zeroFlag = zeroFlag
        self.carryFlag = carryFlag
        
        self.logInstruction(self.readByte(self.pc).getHex(), "CMP", self.readByte(self.pc+0x1).getHex(), instructionParameter=f"#${self.readByte(self.pc+0x1).getHex()}")
        
        self.pc += 0x1
        return 2
    
    def CLD(self):
        self.logInstruction(self.readByte(self.pc).getHex(), "CLD")
        
        self.decimalModeFlag = False
        return 2
    
    def PHA(self):
        self.logInstruction(self.readByte(self.pc).getHex(), "PHA")
        self.pushStackPointer(self.accumulatorRegister.getWriteableInt())
        return 3
    
    def PLP(self):
        self.logInstruction(self.readByte(self.pc).getHex(), "PLP")
        
        stackValue: UInt8 = UInt8(self.popStackPointer())
        bits4and5 = (self.statusRegister >> 4) & 3
        
        newStatusValue: UInt8 = stackValue
        newStatusValue &= ~(3 << 4)
        newStatusValue = bits4and5 << 4 | newStatusValue
        
        self.setFlagsFromStatusRegister(newStatusValue)
        self.updateStatusRegister()
        
        return 4
    
    def BMI(self):
        offset: Int8 = self.readByte(self.pc + 0x1)
        newAddressIfBranched: UInt16 = self.pc + offset.value
        
        self.logInstruction(self.readByte(self.pc).getHex(), "BMI", offset.getHex(), instructionParameter=f"${(newAddressIfBranched+2).getHex()}")
        
        if self.negativeFlag == True:
            self.pc = newAddressIfBranched
        
        self.pc += 0x1
        return 2
    
    def ImmediateORA(self):
        operand: UInt8 = self.readByte(self.pc + 0x1)
        
        self.logInstruction(self.readByte(self.pc).getHex(), "ORA", operand.getHex(), instructionParameter=f"#${operand.getHex()}")
        
        orResult: Int8 = self.ORA(self.accumulatorRegister, operand)
        self.accumulatorRegister = orResult
        
        self.updateNegativeFlag(self.accumulatorRegister)
        self.updateZeroFlag(self.accumulatorRegister)
        
        self.pc += 0x1
        return 2
    
    def CLV(self):
        self.logInstruction(self.readByte(self.pc).getHex(), "CLV")
        
        self.overflowFlag = False
        return 2
    
    def ImmediateEOR(self):
        operand: UInt8 = self.readByte(self.pc + 0x1)
    
        self.logInstruction(self.readByte(self.pc).getHex(), "EOR", operand.getHex(), instructionParameter=f"#${operand.getHex()}")
    
        eorResult: Int8 = self.EOR(self.accumulatorRegister, operand)
        self.accumulatorRegister = eorResult
    
        self.updateNegativeFlag(self.accumulatorRegister)
        self.updateZeroFlag(self.accumulatorRegister)
    
        self.pc += 0x1
        return 2
    
    
    
    def ImmediateADC(self):
        # I hate this function so much. If i have to deal with this again I will kms
        operand: UInt8 = self.readByte(self.pc + 0x1)
        
        self.logInstruction(self.readByte(self.pc).getHex(), "ADC", operand.getHex(), instructionParameter=f"#${operand.getHex()}")
        
        resultInt8, carryFlag, negativeFlag, zeroFlag, overflowFlag = self.ADC(self.accumulatorRegister, operand, self.carryFlag)

        self.carryFlag = carryFlag
        self.negativeFlag = negativeFlag
        self.zeroFlag = zeroFlag
        self.overflowFlag = overflowFlag
        
        self.accumulatorRegister = resultInt8
        
        self.pc += 0x1
        return 2
    
    def ImmediateLDY(self):
        operand: UInt8 = self.readByte(self.pc + 0x1)
        self.logInstruction(self.readByte(self.pc).getHex(), "LDY", operand.getHex(), instructionParameter=f"#${operand.getHex()}")
        
        self.YRegister = Int8(operand.value)
        
        self.updateNegativeFlag(self.YRegister)
        self.updateZeroFlag(self.YRegister)
        
        self.pc += 0x1
        return 2
    
    def ImmediateCPY(self):
        operand: UInt8 = self.readByte(self.pc + 0x1)
        valueToCompare = operand.getWriteableInt()
        
        compareResult, negativeFlag, zeroFlag, carryFlag = self.compareValues(self.YRegister, Int8(valueToCompare))
        
        self.negativeFlag = negativeFlag
        self.zeroFlag = zeroFlag
        self.carryFlag = carryFlag
        
        self.logInstruction(self.readByte(self.pc).getHex(), "CPY", self.readByte(self.pc+0x1).getHex(), instructionParameter=f"#${self.readByte(self.pc+0x1).getHex()}")
        
        self.pc += 0x1
        return 2
    
    def ImmediateCPX(self):
        operand: UInt8 = self.readByte(self.pc + 0x1)
        valueToCompare = operand.getWriteableInt()
        
        compareResult, negativeFlag, zeroFlag, carryFlag = self.compareValues(self.XRegister, Int8(valueToCompare))
        
        self.negativeFlag = negativeFlag
        self.zeroFlag = zeroFlag
        self.carryFlag = carryFlag
        
        self.logInstruction(self.readByte(self.pc).getHex(), "CPX", self.readByte(self.pc+0x1).getHex(), instructionParameter=f"#${self.readByte(self.pc+0x1).getHex()}")
        
        self.pc += 0x1
        return 2
    
    def ImmediateSBC(self, illegal: bool = False):
        operand: UInt8 = self.readByte(self.pc + 0x1)
        
        self.logInstruction(self.readByte(self.pc).getHex(), "SBC", operand.getHex(), instructionParameter=f"#${operand.getHex()}", isIllegal=illegal)
        
        
        accumulatorRegister, negativeFlag, zeroFlag, overflowFlag, carryFlag = self.SBC(self.accumulatorRegister, operand, self.carryFlag)
        
        self.accumulatorRegister = accumulatorRegister
        self.negativeFlag = negativeFlag
        self.zeroFlag = zeroFlag
        self.overflowFlag = overflowFlag
        self.carryFlag = carryFlag
        
        self.pc += 0x1
        return 2

    
    def INY(self):
        self.logInstruction(self.readByte(self.pc).getHex(), "INY")
        self.YRegister += 1
        self.updateNegativeFlag(self.YRegister)
        self.updateZeroFlag(self.YRegister)
        
        return 2
    
    def INX(self):
        self.logInstruction(self.readByte(self.pc).getHex(), "INX")
        self.XRegister += 1
        self.updateNegativeFlag(self.XRegister)
        self.updateZeroFlag(self.XRegister)
        
        return 2
    
    def DEY(self):
        self.logInstruction(self.readByte(self.pc).getHex(), "DEY")
        self.YRegister -= 1
        self.updateNegativeFlag(self.YRegister)
        self.updateZeroFlag(self.YRegister)
        
        return 2
    
    def DEX(self):
        self.logInstruction(self.readByte(self.pc).getHex(), "DEX")
        self.XRegister -= 1
        self.updateNegativeFlag(self.XRegister)
        self.updateZeroFlag(self.XRegister)
        
        return 2
    
    def TAY(self):
        self.logInstruction(self.readByte(self.pc).getHex(), "TAY")
        self.YRegister = self.accumulatorRegister
        self.updateNegativeFlag(self.YRegister)
        self.updateZeroFlag(self.YRegister)
        return 2
    
    def TAX(self):
        self.logInstruction(self.readByte(self.pc).getHex(), "TAX")
        self.XRegister = self.accumulatorRegister
        self.updateNegativeFlag(self.XRegister)
        self.updateZeroFlag(self.XRegister)
        return 2
    
    def TYA(self):
        self.logInstruction(self.readByte(self.pc).getHex(), "TYA")
        self.accumulatorRegister = self.YRegister
        self.updateNegativeFlag(self.accumulatorRegister)
        self.updateZeroFlag(self.accumulatorRegister)
        return 2
    
    def TXA(self):
        self.logInstruction(self.readByte(self.pc).getHex(), "TXA")
        self.accumulatorRegister = self.XRegister
        self.updateNegativeFlag(self.accumulatorRegister)
        self.updateZeroFlag(self.accumulatorRegister)
        return 2
    
    def TSX(self):
        self.logInstruction(self.readByte(self.pc).getHex(), "TSX")
        self.XRegister = self.stackPointer
        self.updateNegativeFlag(self.XRegister)
        self.updateZeroFlag(self.XRegister)
        
        return 2
    
    def AbsoluteSTX(self):
        operand1: UInt8 = self.readByte(self.pc + 0x1)
        operand2: UInt8 = self.readByte(self.pc + 0x2)
        fullAddress: UInt16 = self.combineTwoBytesToOneAddress(operand2, operand1)

        self.logInstruction(self.readByte(self.pc).getHex(), "STX", operand1.getHex(), operand2.getHex(), instructionParameter=f"${fullAddress.getHex()} = {self.readByte(fullAddress).getHex()}")

        self.RAM.writeAddress(fullAddress, self.XRegister.getWriteableInt())

        self.pc += 0x2
        return 4
    
    def TXS(self):
        self.logInstruction(self.readByte(self.pc).getHex(), "TXS")
        self.stackPointer = self.XRegister
        return 2
    
    def AbsoluteLDX(self):
        operand1: UInt8 = self.readByte(self.pc + 0x1)
        operand2: UInt8 = self.readByte(self.pc + 0x2)
        fullAddress: UInt16 = self.combineTwoBytesToOneAddress(operand2, operand1)

        valueFromMemory = self.readByte(fullAddress)

        self.logInstruction(self.readByte(self.pc).getHex(), "LDX", operand1.getHex(), operand2.getHex(), instructionParameter=f"${fullAddress.getHex()} = {valueFromMemory.getHex()}")

        self.XRegister = valueFromMemory

        self.updateNegativeFlag(self.XRegister)
        self.updateZeroFlag(self.XRegister)

        self.pc += 0x2
        return 4
    
    def AbsoluteLDA(self):
        operand1: UInt8 = self.readByte(self.pc + 0x1)
        operand2: UInt8 = self.readByte(self.pc + 0x2)
        fullAddress: UInt16 = self.combineTwoBytesToOneAddress(operand2, operand1)
        valueFromMemory: UInt8 = self.readByte(fullAddress)

        self.logInstruction(self.readByte(self.pc).getHex(), "LDA", operand1.getHex(), operand2.getHex(), instructionParameter=f"${fullAddress.getHex()} = {valueFromMemory.getHex()}")

        self.LDA(fullAddress)
        self.updateNegativeFlag(self.accumulatorRegister)
        self.updateZeroFlag(self.accumulatorRegister)

        self.pc += 0x2
        return 4
    
    def RTI(self):
        self.logInstruction(self.readByte(self.pc).getHex(), "RTI")
        
        oldBreakFlag = self.breakFlag
        statusRegisterPulled: UInt8 = UInt8(self.popStackPointer())
        self.setFlagsFromStatusRegister(statusRegisterPulled)
        self.breakFlag = oldBreakFlag
        self.updateStatusRegister()
        
        lowByte: UInt8 = UInt8(self.popStackPointer())
        highByte: UInt8 = UInt8(self.popStackPointer())
        returnAddress = self.combineTwoBytesToOneAddress(highByte, lowByte)
        self.pc = returnAddress - 0x1
        
        return 6
    
    def AccumulatorLSR(self):
        self.logInstruction(self.readByte(self.pc).getHex(), "LSR", instructionParameter="A")
        
        result, carryFlag, negativeFlag, zeroFlag = self.LSR(self.accumulatorRegister)
        self.accumulatorRegister = result
        self.carryFlag = carryFlag
        self.negativeFlag = negativeFlag
        self.zeroFlag = zeroFlag
        
        return 2
    
    def AccumulatorASL(self):
        self.logInstruction(self.readByte(self.pc).getHex(), "ASL", instructionParameter="A")
        
        result, carryFlag, negativeFlag, zeroFlag = self.ASL(self.accumulatorRegister)
        
        self.accumulatorRegister = result
        self.carryFlag = carryFlag
        self.negativeFlag = negativeFlag
        self.zeroFlag = zeroFlag
        
        return 2
    
    def AccumulatorROR(self):
        self.logInstruction(self.readByte(self.pc).getHex(), "ROR", instructionParameter="A")
        
        result, carryFlag, negativeFlag, zeroFlag = self.ROR(self.accumulatorRegister, self.carryFlag)
        
        self.accumulatorRegister = result
        self.carryFlag = carryFlag
        self.negativeFlag = negativeFlag
        self.zeroFlag = zeroFlag
        
        return 2
        
    
    def AccumulatorROL(self):
        self.logInstruction(self.readByte(self.pc).getHex(), "ROL", instructionParameter="A")
        
        result, carryFlag, negativeFlag, zeroFlag = self.ROL(self.accumulatorRegister, self.carryFlag)
        self.accumulatorRegister = result
        self.carryFlag = carryFlag
        self.negativeFlag = negativeFlag
        self.zeroFlag = zeroFlag
        
        return 2
    
    def ZeropageLDA(self):
        zeropageAddress: UInt8 = self.readByte(self.pc + 0x1)
        oldValue: Int8 = self.readByte(zeropageAddress)
        
        self.logInstruction(self.readByte(self.pc).getHex(), "LDA", zeropageAddress.getHex(), instructionParameter=f"${zeropageAddress.getHex()} = {oldValue.getHex()}")
        
        self.LDA(zeropageAddress)
        self.updateNegativeFlag(self.accumulatorRegister)
        self.updateZeroFlag(self.accumulatorRegister)
        
        self.pc += 0x1
        return 3
    
    def AbsoluteSTA(self):
        operand1: UInt8 = self.readByte(self.pc + 0x1)
        operand2: UInt8 = self.readByte(self.pc + 0x2)
        fullAddress: UInt16 = self.combineTwoBytesToOneAddress(operand2, operand1)
        oldValue: Int8 = self.readByte(fullAddress)
        
        self.logInstruction(self.readByte(self.pc).getHex(), "STA", operand1.getHex(), operand2.getHex(), instructionParameter=f"${fullAddress.getHex()} = {oldValue.getHex()}")
        
        self.STA(fullAddress)
        
        self.pc += 0x2
        return 4
    
    def IndirectX_LDA(self):
        operand: UInt8 = self.readByte(self.pc + 0x1)
        zeropageAddress: UInt8 = operand + self.XRegister
        lowAddressByte: UInt8 = self.readByte(zeropageAddress)
        highAddressByte: UInt8 = self.readByte(zeropageAddress + 0x1)
        fullAddress: UInt16 = self.combineTwoBytesToOneAddress(highAddressByte, lowAddressByte)
        memoryBefore: UInt8 = self.readByte(fullAddress)
        
        self.logInstruction(self.readByte(self.pc).getHex(), "LDA", operand.getHex(), instructionParameter=f"(${operand.getHex()},X) @ {(zeropageAddress).getHex()} = {fullAddress.getHex()} = {memoryBefore.getHex()}")
        
        self.LDA(fullAddress)
        self.updateNegativeFlag(self.accumulatorRegister)
        self.updateZeroFlag(self.accumulatorRegister)
        
        self.pc += 0x1
        return 6
    
    def IndirectX_STA(self):
        operand: UInt8 = self.readByte(self.pc + 0x1)
        zeropageAddress: UInt8 = operand + self.XRegister
        lowAddressByte: UInt8 = self.readByte(zeropageAddress)
        highAddressByte: UInt8 = self.readByte(zeropageAddress + 0x1)
        fullAddress: UInt16 = self.combineTwoBytesToOneAddress(highAddressByte, lowAddressByte)
        memoryBefore: UInt8 = self.readByte(fullAddress)
        
        self.logInstruction(self.readByte(self.pc).getHex(), "STA", operand.getHex(), instructionParameter=f"(${operand.getHex()},X) @ {(zeropageAddress).getHex()} = {fullAddress.getHex()} = {memoryBefore.getHex()}")        
        
        self.STA(fullAddress)
        
        self.pc += 0x1
        return 6
    
    def IndirectX_ORA(self):
        operand: UInt8 = self.readByte(self.pc + 0x1)
        zeropageAddress: UInt8 = operand + self.XRegister
        lowAddressByte: UInt8 = self.readByte(zeropageAddress)
        highAddressByte: UInt8 = self.readByte(zeropageAddress + 0x1)
        fullAddress: UInt16 = self.combineTwoBytesToOneAddress(highAddressByte, lowAddressByte)
        memoryBefore: UInt8 = self.readByte(fullAddress)
        
        self.logInstruction(self.readByte(self.pc).getHex(), "ORA", operand.getHex(), instructionParameter=f"(${operand.getHex()},X) @ {(zeropageAddress).getHex()} = {fullAddress.getHex()} = {memoryBefore.getHex()}")        
        
        
        orResult: Int8 = self.ORA(self.accumulatorRegister, memoryBefore.getWriteableInt())
        self.accumulatorRegister = orResult
        
        self.updateNegativeFlag(self.accumulatorRegister)
        self.updateZeroFlag(self.accumulatorRegister)
        
        self.pc += 0x1
        return 6
    
    def IndirectX_AND(self):
        operand: UInt8 = self.readByte(self.pc + 0x1)
        zeropageAddress: UInt8 = operand + self.XRegister
        lowAddressByte: UInt8 = self.readByte(zeropageAddress)
        highAddressByte: UInt8 = self.readByte(zeropageAddress + 0x1)
        fullAddress: UInt16 = self.combineTwoBytesToOneAddress(highAddressByte, lowAddressByte)
        memoryBefore: UInt8 = self.readByte(fullAddress)
        
        self.logInstruction(self.readByte(self.pc).getHex(), "AND", operand.getHex(), instructionParameter=f"(${operand.getHex()},X) @ {(zeropageAddress).getHex()} = {fullAddress.getHex()} = {memoryBefore.getHex()}")        
        
        
        andResult: Int8 = self.AND_Values(self.accumulatorRegister, memoryBefore)
        self.accumulatorRegister = andResult
        
        self.updateNegativeFlag(self.accumulatorRegister)
        self.updateZeroFlag(self.accumulatorRegister)
        
        self.pc += 0x1
        return 6
    
    def IndirectX_EOR(self):
        operand: UInt8 = self.readByte(self.pc + 0x1)
        zeropageAddress: UInt8 = operand + self.XRegister
        lowAddressByte: UInt8 = self.readByte(zeropageAddress)
        highAddressByte: UInt8 = self.readByte(zeropageAddress + 0x1)
        fullAddress: UInt16 = self.combineTwoBytesToOneAddress(highAddressByte, lowAddressByte)
        memoryBefore: UInt8 = self.readByte(fullAddress)
        
        self.logInstruction(self.readByte(self.pc).getHex(), "EOR", operand.getHex(), instructionParameter=f"(${operand.getHex()},X) @ {(zeropageAddress).getHex()} = {fullAddress.getHex()} = {memoryBefore.getHex()}")        
        
        eorResult: Int8 = self.EOR(self.accumulatorRegister, memoryBefore)
        self.accumulatorRegister = eorResult
        
        self.updateNegativeFlag(self.accumulatorRegister)
        self.updateZeroFlag(self.accumulatorRegister)
        
        self.pc += 0x1
        return 6
    
    def IndirectX_ADC(self):
        operand: UInt8 = self.readByte(self.pc + 0x1)
        zeropageAddress: UInt8 = operand + self.XRegister
        lowAddressByte: UInt8 = self.readByte(zeropageAddress)
        highAddressByte: UInt8 = self.readByte(zeropageAddress + 0x1)
        fullAddress: UInt16 = self.combineTwoBytesToOneAddress(highAddressByte, lowAddressByte)
        memoryBefore: UInt8 = self.readByte(fullAddress)
        
        self.logInstruction(self.readByte(self.pc).getHex(), "ADC", operand.getHex(), instructionParameter=f"(${operand.getHex()},X) @ {(zeropageAddress).getHex()} = {fullAddress.getHex()} = {memoryBefore.getHex()}")        
        
        resultInt8, carryFlag, negativeFlag, zeroFlag, overflowFlag = self.ADC(self.accumulatorRegister, memoryBefore, self.carryFlag)

        self.carryFlag = carryFlag
        self.negativeFlag = negativeFlag
        self.zeroFlag = zeroFlag
        self.overflowFlag = overflowFlag
        
        self.accumulatorRegister = resultInt8
        
        self.pc += 0x1
        return 6
    
    def IndirectX_CMP(self):
        operand: UInt8 = self.readByte(self.pc + 0x1)
        zeropageAddress: UInt8 = operand + self.XRegister
        lowAddressByte: UInt8 = self.readByte(zeropageAddress)
        highAddressByte: UInt8 = self.readByte(zeropageAddress + 0x1)
        fullAddress: UInt16 = self.combineTwoBytesToOneAddress(highAddressByte, lowAddressByte)
        memoryBefore: UInt8 = self.readByte(fullAddress)
        
        self.logInstruction(self.readByte(self.pc).getHex(), "CMP", operand.getHex(), instructionParameter=f"(${operand.getHex()},X) @ {(zeropageAddress).getHex()} = {fullAddress.getHex()} = {memoryBefore.getHex()}")        
        
        compareResult, negativeFlag, zeroFlag, carryFlag = self.compareValues(self.accumulatorRegister, memoryBefore)
        
        self.negativeFlag = negativeFlag
        self.zeroFlag = zeroFlag
        self.carryFlag = carryFlag
        
        self.pc += 0x1
        return 6
    
    def ZeropageSTY(self):
        operand: UInt8 = self.readByte(self.pc + 0x1)
        valueToReplace: UInt8 = self.readByte(operand)
        
        self.logInstruction(self.readByte(self.pc).getHex(), "STY", operand.getHex(), instructionParameter=f"${operand.getHex()} = {valueToReplace.getHex()}")        
        
        self.RAM.writeAddress(operand, self.YRegister.getWriteableInt())
        
        self.pc += 0x1
        return 3
    
    def IndirectX_SBC(self):
        operand: UInt8 = self.readByte(self.pc + 0x1)
        zeropageAddress: UInt8 = operand + self.XRegister
        lowAddressByte: UInt8 = self.readByte(zeropageAddress)
        highAddressByte: UInt8 = self.readByte(zeropageAddress + 0x1)
        fullAddress: UInt16 = self.combineTwoBytesToOneAddress(highAddressByte, lowAddressByte)
        memoryBefore: UInt8 = self.readByte(fullAddress)
        
        self.logInstruction(self.readByte(self.pc).getHex(), "SBC", operand.getHex(), instructionParameter=f"(${operand.getHex()},X) @ {(zeropageAddress).getHex()} = {fullAddress.getHex()} = {memoryBefore.getHex()}")        
        
        accumulatorRegister, negativeFlag, zeroFlag, overflowFlag, carryFlag = self.SBC(self.accumulatorRegister, memoryBefore, self.carryFlag)
        
        self.accumulatorRegister = accumulatorRegister
        self.negativeFlag = negativeFlag
        self.zeroFlag = zeroFlag
        self.overflowFlag = overflowFlag
        self.carryFlag = carryFlag
        
        self.pc += 0x1
        return 6
    
    def ZeropageLDY(self):
        operand: UInt8 = self.readByte(self.pc + 0x1)
        value: UInt8 = self.readByte(operand)
        self.logInstruction(self.readByte(self.pc).getHex(), "LDY", operand.getHex(), instructionParameter=f"${operand.getHex()} = {value.getHex()}")
        
        self.YRegister = value
        self.updateNegativeFlag(self.YRegister)
        self.updateZeroFlag(self.YRegister)
        
        self.pc += 0x1
        return 3
    
    def ZeropageLDX(self):
        operand: UInt8 = self.readByte(self.pc + 0x1)
        value: UInt8 = self.readByte(operand)
        self.logInstruction(self.readByte(self.pc).getHex(), "LDX", operand.getHex(), instructionParameter=f"${operand.getHex()} = {value.getHex()}")
        
        self.XRegister = value
        self.updateNegativeFlag(self.XRegister)
        self.updateZeroFlag(self.XRegister)
        
        self.pc += 0x1
        return 3
    
    def ZeropageORA(self):
        operand: UInt8 = self.readByte(self.pc + 0x1)
        operandValue: UInt8 = self.readByte(operand)
        
        self.logInstruction(self.readByte(self.pc).getHex(), "ORA", operand.getHex(), instructionParameter=f"${operand.getHex()} = {operandValue.getHex()}")
        
        orResult: Int8 = self.ORA(self.accumulatorRegister, operandValue)
        self.accumulatorRegister = orResult
        
        self.updateNegativeFlag(self.accumulatorRegister)
        self.updateZeroFlag(self.accumulatorRegister)
        
        self.pc += 0x1
        return 3
    
    def ZeropageAND(self):
        operand: UInt8 = self.readByte(self.pc + 0x1)
        value: UInt8 = self.readByte(operand)
        
        self.logInstruction(self.readByte(self.pc).getHex(), "AND", operand.getHex(), instructionParameter=f"${operand.getHex()} = {value.getHex()}")
        
        andResult = self.AND_Values(self.accumulatorRegister, value)
        self.accumulatorRegister = andResult
        
        self.updateNegativeFlag(self.accumulatorRegister)
        self.updateZeroFlag(self.accumulatorRegister)
        
        self.pc += 0x1
        return 3
    
    def ZeropageEOR(self):
        operand: UInt8 = self.readByte(self.pc + 0x1)
        value: UInt8 = self.readByte(operand)
    
        self.logInstruction(self.readByte(self.pc).getHex(), "EOR", operand.getHex(), instructionParameter=f"${operand.getHex()} = {value.getHex()}")
    
        eorResult: Int8 = self.EOR(self.accumulatorRegister, value)
        self.accumulatorRegister = eorResult
    
        self.updateNegativeFlag(self.accumulatorRegister)
        self.updateZeroFlag(self.accumulatorRegister)
    
        self.pc += 0x1
        return 3
    
    def ZeropageADC(self):
        operand: UInt8 = self.readByte(self.pc + 0x1)
        value: UInt8 = self.readByte(operand)
        
        self.logInstruction(self.readByte(self.pc).getHex(), "ADC", operand.getHex(), instructionParameter=f"${operand.getHex()} = {value.getHex()}")
        
        resultInt8, carryFlag, negativeFlag, zeroFlag, overflowFlag = self.ADC(self.accumulatorRegister, value, self.carryFlag)

        self.carryFlag = carryFlag
        self.negativeFlag = negativeFlag
        self.zeroFlag = zeroFlag
        self.overflowFlag = overflowFlag
        
        self.accumulatorRegister = resultInt8
        
        self.pc += 0x1
        return 3
    
    def ZeropageCMP(self):
        operand: UInt8 = self.readByte(self.pc + 0x1)
        valueToCompare: UInt8 = self.readByte(operand)
        
        compareResult, negativeFlag, zeroFlag, carryFlag = self.compareValues(self.accumulatorRegister, valueToCompare)
        
        self.negativeFlag = negativeFlag
        self.zeroFlag = zeroFlag
        self.carryFlag = carryFlag
        
        self.logInstruction(self.readByte(self.pc).getHex(), "CMP", self.readByte(self.pc+0x1).getHex(), instructionParameter=f"${operand.getHex()} = {valueToCompare.getHex()}")
        
        self.pc += 0x1
        return 3
    
    def ZeropageSBC(self):
        operand: UInt8 = self.readByte(self.pc + 0x1)
        value: UInt8 = self.readByte(operand)
        
        self.logInstruction(self.readByte(self.pc).getHex(), "SBC", operand.getHex(), instructionParameter=f"${operand.getHex()} = {value.getHex()}")
        
        accumulatorRegister, negativeFlag, zeroFlag, overflowFlag, carryFlag = self.SBC(self.accumulatorRegister, value, self.carryFlag)
        
        self.accumulatorRegister = accumulatorRegister
        self.negativeFlag = negativeFlag
        self.zeroFlag = zeroFlag
        self.overflowFlag = overflowFlag
        self.carryFlag = carryFlag
        
        self.pc += 0x1
        return 3
    
    def ZeropageCPX(self):
        operand: UInt8 = self.readByte(self.pc + 0x1)
        valueToCompare: UInt8 = self.readByte(operand)
        
        compareResult, negativeFlag, zeroFlag, carryFlag = self.compareValues(self.XRegister, valueToCompare)
        
        self.negativeFlag = negativeFlag
        self.zeroFlag = zeroFlag
        self.carryFlag = carryFlag
        
        self.logInstruction(self.readByte(self.pc).getHex(), "CPX", operand.getHex(), instructionParameter=f"${operand.getHex()} = {valueToCompare.getHex()}")
        
        self.pc += 0x1
        return 3
    
    def ZeropageCPY(self):
        operand: UInt8 = self.readByte(self.pc + 0x1)
        valueToCompare: UInt8 = self.readByte(operand)
        
        compareResult, negativeFlag, zeroFlag, carryFlag = self.compareValues(self.YRegister, valueToCompare)
        
        self.negativeFlag = negativeFlag
        self.zeroFlag = zeroFlag
        self.carryFlag = carryFlag
        
        self.logInstruction(self.readByte(self.pc).getHex(), "CPY", operand.getHex(), instructionParameter=f"${operand.getHex()} = {valueToCompare.getHex()}")
        
        self.pc += 0x1
        return 3
    
    def ZeropageLSR(self):
        operand: UInt8 = self.readByte(self.pc + 0x1)
        valueToShift: UInt8 = self.readByte(operand)
        
        self.logInstruction(self.readByte(self.pc).getHex(), "LSR", operand1=operand.getHex(), instructionParameter=f"${operand.getHex()} = {valueToShift.getHex()}")
        
        result, carryFlag, negativeFlag, zeroFlag = self.LSR(valueToShift)
        self.RAM.writeAddress(operand, result.getWriteableInt())
        self.carryFlag = carryFlag
        self.negativeFlag = negativeFlag
        self.zeroFlag = zeroFlag
        
        self.pc += 0x1
        return 5
    
    def ZeropageASL(self):
        operand: UInt8 = self.readByte(self.pc + 0x1)
        valueToShift: UInt8 = self.readByte(operand)
        
        self.logInstruction(self.readByte(self.pc).getHex(), "ASL", operand1=operand.getHex(), instructionParameter=f"${operand.getHex()} = {valueToShift.getHex()}")
        
        result, carryFlag, negativeFlag, zeroFlag = self.ASL(valueToShift)
        
        self.RAM.writeAddress(operand, result.getWriteableInt())
        self.carryFlag = carryFlag
        self.negativeFlag = negativeFlag
        self.zeroFlag = zeroFlag
        
        self.pc += 0x1
        return 5

    def ZeropageROR(self):
        operand: UInt8 = self.readByte(self.pc + 0x1)
        valueToShift: UInt8 = self.readByte(operand)
        
        self.logInstruction(self.readByte(self.pc).getHex(), "ROR", operand1=operand.getHex(), instructionParameter=f"${operand.getHex()} = {valueToShift.getHex()}")
        
        result, carryFlag, negativeFlag, zeroFlag = self.ROR(valueToShift, self.carryFlag)
        
        self.RAM.writeAddress(operand, result.getWriteableInt())
        self.carryFlag = carryFlag
        self.negativeFlag = negativeFlag
        self.zeroFlag = zeroFlag
        
        self.pc += 0x1
        return 5
    
    def ZeropageROL(self):
        operand: UInt8 = self.readByte(self.pc + 0x1)
        valueToShift: UInt8 = self.readByte(operand)
        self.logInstruction(self.readByte(self.pc).getHex(), "ROL", operand1=operand.getHex(), instructionParameter=f"${operand.getHex()} = {valueToShift.getHex()}")
        
        result, carryFlag, negativeFlag, zeroFlag = self.ROL(valueToShift, self.carryFlag)
        self.RAM.writeAddress(operand, result.getWriteableInt())
        self.carryFlag = carryFlag
        self.negativeFlag = negativeFlag
        self.zeroFlag = zeroFlag
        
        self.pc += 0x1
        return 5
    
    def ZeropageINC(self):
        operand: UInt8 = self.readByte(self.pc + 0x1)
        valueToIncrement: UInt8 = self.readByte(operand)
        self.logInstruction(self.readByte(self.pc).getHex(), "INC", operand1=operand.getHex(), instructionParameter=f"${operand.getHex()} = {valueToIncrement.getHex()}")
        
        newValue = valueToIncrement + 1
        self.RAM.writeAddress(operand, newValue.getWriteableInt())
        
        self.updateNegativeFlag(newValue)
        self.updateZeroFlag(newValue)
        
        self.pc += 0x1
        return 5
    
    def ZeropageDEC(self):
        operand: UInt8 = self.readByte(self.pc + 0x1)
        valueToIncrement: UInt8 = self.readByte(operand)
        self.logInstruction(self.readByte(self.pc).getHex(), "DEC", operand1=operand.getHex(), instructionParameter=f"${operand.getHex()} = {valueToIncrement.getHex()}")
        
        newValue = valueToIncrement - 1
        self.RAM.writeAddress(operand, newValue.getWriteableInt())
        
        self.updateNegativeFlag(newValue)
        self.updateZeroFlag(newValue)
        
        self.pc += 0x1
        return 5
    
    def AbsoluteLDY(self):
        PCL: UInt8 = self.readByte(self.pc + 0x1)
        PCH: UInt8 = self.readByte(self.pc + 0x2)
        address: UInt16 = self.combineTwoBytesToOneAddress(PCH, PCL)
        valueAtAddress = self.readByte(address)
        self.logInstruction(self.readByte(self.pc).getHex(), "LDY", PCL.getHex(), PCH.getHex(), f"${address.getHex()} = {valueAtAddress.getHex()}")
        
        self.YRegister = valueAtAddress
        self.updateNegativeFlag(self.YRegister)
        self.updateZeroFlag(self.YRegister)
        
        self.pc += 0x2
        return 4
    
    def AbsoluteSTY(self):
        PCL: UInt8 = self.readByte(self.pc + 0x1)
        PCH: UInt8 = self.readByte(self.pc + 0x2)
        address: UInt16 = self.combineTwoBytesToOneAddress(PCH, PCL)
        valueAtAddress = self.readByte(address)
        self.logInstruction(self.readByte(self.pc).getHex(), "STY", PCL.getHex(), PCH.getHex(), f"${address.getHex()} = {valueAtAddress.getHex()}")
        
        self.RAM.writeAddress(address, self.YRegister.getWriteableInt())
        
        self.pc += 0x2
        return 4
    
    def AbsoluteBIT(self):
        PCL: UInt8 = self.readByte(self.pc + 0x1)
        PCH: UInt8 = self.readByte(self.pc + 0x2)
        address: UInt16 = self.combineTwoBytesToOneAddress(PCH, PCL)
        valueToTest: UInt8 = self.readByte(address)
        
        self.logInstruction(self.readByte(self.pc).getHex(), "BIT", PCL.getHex(), PCH.getHex(), instructionParameter=f"${address.getHex()} = {valueToTest.getHex()}")
        
        andValue, negativeFlag, overflowFlag, zeroFlag = self.BIT(self.accumulatorRegister, valueToTest)
        self.negativeFlag = negativeFlag
        self.overflowFlag = overflowFlag
        self.zeroFlag = zeroFlag
        
        self.pc += 0x2
        return 4
    
    def AbsoluteORA(self):
        PCL: UInt8 = self.readByte(self.pc + 0x1)
        PCH: UInt8 = self.readByte(self.pc + 0x2)
        address: UInt16 = self.combineTwoBytesToOneAddress(PCH, PCL)
        valueToTest: UInt8 = self.readByte(address)
        
        self.logInstruction(self.readByte(self.pc).getHex(), "ORA", PCL.getHex(), PCH.getHex(), instructionParameter=f"${address.getHex()} = {valueToTest.getHex()}")        
        
        orResult: Int8 = self.ORA(self.accumulatorRegister, valueToTest)
        self.accumulatorRegister = orResult
        
        self.updateNegativeFlag(self.accumulatorRegister)
        self.updateZeroFlag(self.accumulatorRegister)
        
        self.pc += 0x2
        return 4
    
    def AbsoluteAND(self):
        PCL: UInt8 = self.readByte(self.pc + 0x1)
        PCH: UInt8 = self.readByte(self.pc + 0x2)
        address: UInt16 = self.combineTwoBytesToOneAddress(PCH, PCL)
        valueToTest: UInt8 = self.readByte(address)
        value: int = valueToTest.value
        
        self.logInstruction(self.readByte(self.pc).getHex(), "AND", PCL.getHex(), PCH.getHex(), instructionParameter=f"${address.getHex()} = {valueToTest.getHex()}")
        
        andResult = self.AND_Values(self.accumulatorRegister, value)
        self.accumulatorRegister = andResult
        
        self.updateNegativeFlag(self.accumulatorRegister)
        self.updateZeroFlag(self.accumulatorRegister)
        
        self.pc += 0x2
        return 4
    
    def AbsoluteEOR(self):
        PCL: UInt8 = self.readByte(self.pc + 0x1)
        PCH: UInt8 = self.readByte(self.pc + 0x2)
        address: UInt16 = self.combineTwoBytesToOneAddress(PCH, PCL)
        valueToTest: UInt8 = self.readByte(address)
    
        self.logInstruction(self.readByte(self.pc).getHex(), "EOR", PCL.getHex(), PCH.getHex(), instructionParameter=f"${address.getHex()} = {valueToTest.getHex()}")
    
        eorResult: Int8 = self.EOR(self.accumulatorRegister, valueToTest)
        self.accumulatorRegister = eorResult
    
        self.updateNegativeFlag(self.accumulatorRegister)
        self.updateZeroFlag(self.accumulatorRegister)
    
        self.pc += 0x2
        return 4
    
    def AbsoluteADC(self):
        PCL: UInt8 = self.readByte(self.pc + 0x1)
        PCH: UInt8 = self.readByte(self.pc + 0x2)
        address: UInt16 = self.combineTwoBytesToOneAddress(PCH, PCL)
        valueToTest: UInt8 = self.readByte(address)
        
        self.logInstruction(self.readByte(self.pc).getHex(), "ADC", PCL.getHex(), PCH.getHex(), instructionParameter=f"${address.getHex()} = {valueToTest.getHex()}")        
        
        resultInt8, carryFlag, negativeFlag, zeroFlag, overflowFlag = self.ADC(self.accumulatorRegister, valueToTest, self.carryFlag)

        self.carryFlag = carryFlag
        self.negativeFlag = negativeFlag
        self.zeroFlag = zeroFlag
        self.overflowFlag = overflowFlag
        
        self.accumulatorRegister = resultInt8
        
        self.pc += 0x2
        return 4
    
    def AbsoluteCMP(self):
        PCL: UInt8 = self.readByte(self.pc + 0x1)
        PCH: UInt8 = self.readByte(self.pc + 0x2)
        address: UInt16 = self.combineTwoBytesToOneAddress(PCH, PCL)
        valueToCompare: UInt8 = self.readByte(address)
        
        compareResult, negativeFlag, zeroFlag, carryFlag = self.compareValues(self.accumulatorRegister, valueToCompare)
        
        self.negativeFlag = negativeFlag
        self.zeroFlag = zeroFlag
        self.carryFlag = carryFlag
        
        self.logInstruction(self.readByte(self.pc).getHex(), "CMP", PCL.getHex(), PCH.getHex(), instructionParameter=f"${address.getHex()} = {valueToCompare.getHex()}")
        
        self.pc += 0x2
        return 4
    
    def AbsoluteSBC(self):
        PCL: UInt8 = self.readByte(self.pc + 0x1)
        PCH: UInt8 = self.readByte(self.pc + 0x2)
        address: UInt16 = self.combineTwoBytesToOneAddress(PCH, PCL)
        value: UInt8 = self.readByte(address)
        
        self.logInstruction(self.readByte(self.pc).getHex(), "SBC", PCL.getHex(), PCH.getHex(), instructionParameter=f"${address.getHex()} = {value.getHex()}")
        
        accumulatorRegister, negativeFlag, zeroFlag, overflowFlag, carryFlag = self.SBC(self.accumulatorRegister, value, self.carryFlag)
        
        self.accumulatorRegister = accumulatorRegister
        self.negativeFlag = negativeFlag
        self.zeroFlag = zeroFlag
        self.overflowFlag = overflowFlag
        self.carryFlag = carryFlag
        
        self.pc += 0x2
        return 4
    
    def AbsoluteCPX(self):
        PCL: UInt8 = self.readByte(self.pc + 0x1)
        PCH: UInt8 = self.readByte(self.pc + 0x2)
        address: UInt16 = self.combineTwoBytesToOneAddress(PCH, PCL)
        valueToCompare: UInt8 = self.readByte(address)
        
        compareResult, negativeFlag, zeroFlag, carryFlag = self.compareValues(self.XRegister, valueToCompare)
        
        self.negativeFlag = negativeFlag
        self.zeroFlag = zeroFlag
        self.carryFlag = carryFlag
        
        self.logInstruction(self.readByte(self.pc).getHex(), "CPX", PCL.getHex(), PCH.getHex(), instructionParameter=f"${address.getHex()} = {valueToCompare.getHex()}")
        
        self.pc += 0x2
        return 4
    
    def AbsoluteCPY(self):
        PCL: UInt8 = self.readByte(self.pc + 0x1)
        PCH: UInt8 = self.readByte(self.pc + 0x2)
        address: UInt16 = self.combineTwoBytesToOneAddress(PCH, PCL)
        valueToCompare: UInt8 = self.readByte(address)
        
        compareResult, negativeFlag, zeroFlag, carryFlag = self.compareValues(self.YRegister, valueToCompare)
        
        self.negativeFlag = negativeFlag
        self.zeroFlag = zeroFlag
        self.carryFlag = carryFlag
        
        self.logInstruction(self.readByte(self.pc).getHex(), "CPY", PCL.getHex(), PCH.getHex(), instructionParameter=f"${address.getHex()} = {valueToCompare.getHex()}")
        
        self.pc += 0x2
        return 4
    
    def AbsoluteLSR(self):
        PCL: UInt8 = self.readByte(self.pc + 0x1)
        PCH: UInt8 = self.readByte(self.pc + 0x2)
        address: UInt16 = self.combineTwoBytesToOneAddress(PCH, PCL)
        valueToShift: UInt8 = self.readByte(address)
        
        self.logInstruction(self.readByte(self.pc).getHex(), "LSR", PCL.getHex(), PCH.getHex(), instructionParameter=f"${address.getHex()} = {valueToShift.getHex()}")
        
        result, carryFlag, negativeFlag, zeroFlag = self.LSR(valueToShift)
        self.RAM.writeAddress(address, result.getWriteableInt())
        self.carryFlag = carryFlag
        self.negativeFlag = negativeFlag
        self.zeroFlag = zeroFlag
        
        self.pc += 0x2
        return 6
    
    def AbsoluteASL(self):
        PCL: UInt8 = self.readByte(self.pc + 0x1)
        PCH: UInt8 = self.readByte(self.pc + 0x2)
        address: UInt16 = self.combineTwoBytesToOneAddress(PCH, PCL)
        valueToShift: UInt8 = self.readByte(address)
        
        self.logInstruction(self.readByte(self.pc).getHex(), "ASL", PCL.getHex(), PCH.getHex(), instructionParameter=f"${address.getHex()} = {valueToShift.getHex()}")
        
        result, carryFlag, negativeFlag, zeroFlag = self.ASL(valueToShift)
        
        self.RAM.writeAddress(address, result.getWriteableInt())
        self.carryFlag = carryFlag
        self.negativeFlag = negativeFlag
        self.zeroFlag = zeroFlag
        
        self.pc += 0x2
        return 6
    
    def AbsoluteROR(self):
        PCL: UInt8 = self.readByte(self.pc + 0x1)
        PCH: UInt8 = self.readByte(self.pc + 0x2)
        address: UInt16 = self.combineTwoBytesToOneAddress(PCH, PCL)
        valueToShift: UInt8 = self.readByte(address)
        
        self.logInstruction(self.readByte(self.pc).getHex(), "ROR", PCL.getHex(), PCH.getHex(), instructionParameter=f"${address.getHex()} = {valueToShift.getHex()}")
        
        result, carryFlag, negativeFlag, zeroFlag = self.ROR(valueToShift, self.carryFlag)
        
        self.RAM.writeAddress(address, result.getWriteableInt())
        self.carryFlag = carryFlag
        self.negativeFlag = negativeFlag
        self.zeroFlag = zeroFlag
        
        self.pc += 0x2
        return 6
    
    def AbsoluteROL(self):
        PCL: UInt8 = self.readByte(self.pc + 0x1)
        PCH: UInt8 = self.readByte(self.pc + 0x2)
        address: UInt16 = self.combineTwoBytesToOneAddress(PCH, PCL)
        valueToShift: UInt8 = self.readByte(address)
        self.logInstruction(self.readByte(self.pc).getHex(), "ROL", PCL.getHex(), PCH.getHex(), instructionParameter=f"${address.getHex()} = {valueToShift.getHex()}")
        
        result, carryFlag, negativeFlag, zeroFlag = self.ROL(valueToShift, self.carryFlag)
        self.RAM.writeAddress(address, result.getWriteableInt())
        self.carryFlag = carryFlag
        self.negativeFlag = negativeFlag
        self.zeroFlag = zeroFlag
        
        self.pc += 0x2
        return 6
    
    def AbsoluteINC(self):
        PCL: UInt8 = self.readByte(self.pc + 0x1)
        PCH: UInt8 = self.readByte(self.pc + 0x2)
        address: UInt16 = self.combineTwoBytesToOneAddress(PCH, PCL)
        valueToIncrement: UInt8 = self.readByte(address)
        self.logInstruction(self.readByte(self.pc).getHex(), "INC", PCL.getHex(), PCH.getHex(), instructionParameter=f"${address.getHex()} = {valueToIncrement.getHex()}")
        
        newValue = valueToIncrement + 1
        self.RAM.writeAddress(address, newValue.getWriteableInt())
        
        self.updateNegativeFlag(newValue)
        self.updateZeroFlag(newValue)
        
        self.pc += 0x2
        return 6
    
    def AbsoluteDEC(self):
        PCL: UInt8 = self.readByte(self.pc + 0x1)
        PCH: UInt8 = self.readByte(self.pc + 0x2)
        address: UInt16 = self.combineTwoBytesToOneAddress(PCH, PCL)
        valueToIncrement: UInt8 = self.readByte(address)
        self.logInstruction(self.readByte(self.pc).getHex(), "DEC", PCL.getHex(), PCH.getHex(), instructionParameter=f"${address.getHex()} = {valueToIncrement.getHex()}")
        
        newValue = valueToIncrement - 1
        self.RAM.writeAddress(address, newValue.getWriteableInt())
        
        self.updateNegativeFlag(newValue)
        self.updateZeroFlag(newValue)
        
        self.pc += 0x2
        return 6
    
    def IndirectY_LDA(self):
        operand: UInt8 = self.readByte(self.pc + 0x1)
        baseAddressLow: UInt8 = self.readByte(operand)
        baseAddressHigh: UInt8 = self.readByte(operand + 0x1)
        baseAddress: UInt16 = self.combineTwoBytesToOneAddress(baseAddressHigh, baseAddressLow)
        newAddress: UInt8 = baseAddress + self.YRegister.getWriteableInt()
        memoryBefore: UInt8 = self.readByte(newAddress)
        
        self.logInstruction(self.readByte(self.pc).getHex(), "LDA", operand.getHex(), instructionParameter=f"(${operand.getHex()}),Y = {baseAddress.getHex()} @ {newAddress.getHex()} = {memoryBefore.getHex()}")
        
        self.LDA(newAddress)
        self.updateNegativeFlag(self.accumulatorRegister)
        self.updateZeroFlag(self.accumulatorRegister)
        
        self.pc += 0x1
        return 5
    
    def IndirectY_ORA(self):
        operand: UInt8 = self.readByte(self.pc + 0x1)
        baseAddressLow: UInt8 = self.readByte(operand)
        baseAddressHigh: UInt8 = self.readByte(operand + 0x1)
        baseAddress: UInt16 = self.combineTwoBytesToOneAddress(baseAddressHigh, baseAddressLow)
        newAddress: UInt8 = baseAddress + self.YRegister.getWriteableInt()
        valueToTest: UInt8 = self.readByte(newAddress)
        
        self.logInstruction(self.readByte(self.pc).getHex(), "ORA", operand.getHex(), instructionParameter=f"(${operand.getHex()}),Y = {baseAddress.getHex()} @ {newAddress.getHex()} = {valueToTest.getHex()}")        
        
        orResult: Int8 = self.ORA(self.accumulatorRegister, valueToTest)
        self.accumulatorRegister = orResult
        
        self.updateNegativeFlag(self.accumulatorRegister)
        self.updateZeroFlag(self.accumulatorRegister)
        
        self.pc += 0x1
        return 5
    
    def IndirectY_AND(self):
        operand: UInt8 = self.readByte(self.pc + 0x1)
        baseAddressLow: UInt8 = self.readByte(operand)
        baseAddressHigh: UInt8 = self.readByte(operand + 0x1)
        baseAddress: UInt16 = self.combineTwoBytesToOneAddress(baseAddressHigh, baseAddressLow)
        newAddress: UInt8 = baseAddress + self.YRegister.getWriteableInt()
        valueToTest: UInt8 = self.readByte(newAddress)
        
        self.logInstruction(self.readByte(self.pc).getHex(), "AND", operand.getHex(), instructionParameter=f"(${operand.getHex()}),Y = {baseAddress.getHex()} @ {newAddress.getHex()} = {valueToTest.getHex()}")
        
        andResult = self.AND_Values(self.accumulatorRegister, valueToTest)
        self.accumulatorRegister = andResult
        
        self.updateNegativeFlag(self.accumulatorRegister)
        self.updateZeroFlag(self.accumulatorRegister)
        
        self.pc += 0x1
        return 5
    
    def IndirectY_EOR(self):
        operand: UInt8 = self.readByte(self.pc + 0x1)
        baseAddressLow: UInt8 = self.readByte(operand)
        baseAddressHigh: UInt8 = self.readByte(operand + 0x1)
        baseAddress: UInt16 = self.combineTwoBytesToOneAddress(baseAddressHigh, baseAddressLow)
        newAddress: UInt8 = baseAddress + self.YRegister.getWriteableInt()
        valueToTest: UInt8 = self.readByte(newAddress)
        
        self.logInstruction(self.readByte(self.pc).getHex(), "EOR", operand.getHex(), instructionParameter=f"(${operand.getHex()}),Y = {baseAddress.getHex()} @ {newAddress.getHex()} = {valueToTest.getHex()}")
        
        andResult = self.EOR(self.accumulatorRegister, valueToTest)
        self.accumulatorRegister = andResult
        
        self.updateNegativeFlag(self.accumulatorRegister)
        self.updateZeroFlag(self.accumulatorRegister)
        
        self.pc += 0x1
        return 5
    
    def IndirectY_ADC(self):
        operand: UInt8 = self.readByte(self.pc + 0x1)
        baseAddressLow: UInt8 = self.readByte(operand)
        baseAddressHigh: UInt8 = self.readByte(operand + 0x1)
        baseAddress: UInt16 = self.combineTwoBytesToOneAddress(baseAddressHigh, baseAddressLow)
        newAddress: UInt8 = baseAddress + self.YRegister.getWriteableInt()
        valueToTest: UInt8 = self.readByte(newAddress)
        
        self.logInstruction(self.readByte(self.pc).getHex(), "ADC", operand.getHex(), instructionParameter=f"(${operand.getHex()}),Y = {baseAddress.getHex()} @ {newAddress.getHex()} = {valueToTest.getHex()}")        
        
        resultInt8, carryFlag, negativeFlag, zeroFlag, overflowFlag = self.ADC(self.accumulatorRegister, valueToTest, self.carryFlag)

        self.carryFlag = carryFlag
        self.negativeFlag = negativeFlag
        self.zeroFlag = zeroFlag
        self.overflowFlag = overflowFlag
        
        self.accumulatorRegister = resultInt8
        
        self.pc += 0x1
        return 5
    
    def IndirectY_CMP(self):
        operand: UInt8 = self.readByte(self.pc + 0x1)
        baseAddressLow: UInt8 = self.readByte(operand)
        baseAddressHigh: UInt8 = self.readByte(operand + 0x1)
        baseAddress: UInt16 = self.combineTwoBytesToOneAddress(baseAddressHigh, baseAddressLow)
        newAddress: UInt8 = baseAddress + self.YRegister.getWriteableInt()
        valueToTest: UInt8 = self.readByte(newAddress)
        
        self.logInstruction(self.readByte(self.pc).getHex(), "CMP", operand.getHex(), instructionParameter=f"(${operand.getHex()}),Y = {baseAddress.getHex()} @ {newAddress.getHex()} = {valueToTest.getHex()}")        
        
        compareResult, negativeFlag, zeroFlag, carryFlag = self.compareValues(self.accumulatorRegister, valueToTest)
        
        self.negativeFlag = negativeFlag
        self.zeroFlag = zeroFlag
        self.carryFlag = carryFlag
        
        self.pc += 0x1
        return 5
    
    def IndirectY_SBC(self):
        operand: UInt8 = self.readByte(self.pc + 0x1)
        baseAddressLow: UInt8 = self.readByte(operand)
        baseAddressHigh: UInt8 = self.readByte(operand + 0x1)
        baseAddress: UInt16 = self.combineTwoBytesToOneAddress(baseAddressHigh, baseAddressLow)
        newAddress: UInt8 = baseAddress + self.YRegister.getWriteableInt()
        valueToTest: UInt8 = self.readByte(newAddress)
        
        self.logInstruction(self.readByte(self.pc).getHex(), "SBC", operand.getHex(), instructionParameter=f"(${operand.getHex()}),Y = {baseAddress.getHex()} @ {newAddress.getHex()} = {valueToTest.getHex()}")        
        
        accumulatorRegister, negativeFlag, zeroFlag, overflowFlag, carryFlag = self.SBC(self.accumulatorRegister, valueToTest, self.carryFlag)
        
        self.accumulatorRegister = accumulatorRegister
        self.negativeFlag = negativeFlag
        self.zeroFlag = zeroFlag
        self.overflowFlag = overflowFlag
        self.carryFlag = carryFlag
        
        self.pc += 0x1
        return 5
    
    def IndirectY_STA(self):
        operand: UInt8 = self.readByte(self.pc + 0x1)
        baseAddressLow: UInt8 = self.readByte(operand)
        baseAddressHigh: UInt8 = self.readByte(operand + 0x1)
        baseAddress: UInt16 = self.combineTwoBytesToOneAddress(baseAddressHigh, baseAddressLow)
        newAddress: UInt8 = baseAddress + self.YRegister.getWriteableInt()
        valueToTest: UInt8 = self.readByte(newAddress)
        
        self.logInstruction(self.readByte(self.pc).getHex(), "STA", operand.getHex(), instructionParameter=f"(${operand.getHex()}),Y = {baseAddress.getHex()} @ {newAddress.getHex()} = {valueToTest.getHex()}")        
        
        self.STA(newAddress)
        
        self.pc += 0x1
        return 6
    
    def IndirectJMP(self) -> int:
        PCL: UInt8 = self.readByte(self.pc + 0x1)
        PCH: UInt8 = self.readByte(self.pc + 0x2)
        addressWhereStored: UInt16 = self.combineTwoBytesToOneAddress(PCH, PCL)
        jumpLow: UInt8 = self.readByte(addressWhereStored)
        
        # Edge Case: http://www.6502.org/tutorials/6502opcodes.html#JMP:~:text=AN%20INDIRECT%20JUMP%20MUST%20NEVER%20USE%20A%0AVECTOR%20BEGINNING%20ON%20THE%20LAST%20BYTE%0AOF%20A%20PAGE
        edgeCaseOffset: int = 0x100 if PCL.getWriteableInt() == 0xFF else 0
        jumpHigh: UInt8 = self.readByte(addressWhereStored + 0x1 - edgeCaseOffset)
        
        jumpAddress: UInt16 = self.combineTwoBytesToOneAddress(jumpHigh, jumpLow)
        
        self.logInstruction(self.readByte(self.pc).getHex(), "JMP", PCL.getHex(), PCH.getHex(), f"(${addressWhereStored.getHex()}) = {jumpAddress.getHex()}")
        
        self.pc = jumpAddress - 0x1 # Remove 1 so that when the PC increments it cancels out
        
        return 5
    
    def AbsoluteY_LDA(self):
        operand1: UInt8 = self.readByte(self.pc + 0x1)
        operand2: UInt8 = self.readByte(self.pc + 0x2)
        fullAddress: UInt16 = self.combineTwoBytesToOneAddress(operand2, operand1)
        effectiveAddress: UInt16 = fullAddress + self.YRegister.getWriteableInt()
        valueFromMemory: UInt8 = self.readByte(effectiveAddress)

        self.logInstruction(self.readByte(self.pc).getHex(), "LDA", operand1.getHex(), operand2.getHex(), instructionParameter=f"${fullAddress.getHex()},Y @ {effectiveAddress.getHex()} = {valueFromMemory.getHex()}")

        self.accumulatorRegister = valueFromMemory

        self.updateNegativeFlag(self.accumulatorRegister)
        self.updateZeroFlag(self.accumulatorRegister)

        self.pc += 0x2
        return 4
    
    def AbsoluteY_ORA(self):
        operand1: UInt8 = self.readByte(self.pc + 0x1)
        operand2: UInt8 = self.readByte(self.pc + 0x2)
        fullAddress: UInt16 = self.combineTwoBytesToOneAddress(operand2, operand1)
        effectiveAddress: UInt16 = fullAddress + self.YRegister.getWriteableInt()
        valueFromMemory: UInt8 = self.readByte(effectiveAddress)
        
        self.logInstruction(self.readByte(self.pc).getHex(), "ORA", operand1.getHex(), operand2=operand2.getHex(), instructionParameter=f"${fullAddress.getHex()},Y @ {effectiveAddress.getHex()} = {valueFromMemory.getHex()}")        
        
        orResult: Int8 = self.ORA(self.accumulatorRegister, valueFromMemory)
        self.accumulatorRegister = orResult
        
        self.updateNegativeFlag(self.accumulatorRegister)
        self.updateZeroFlag(self.accumulatorRegister)
        
        self.pc += 0x2
        return 4
    
    def AbsoluteY_AND(self):
        operand1: UInt8 = self.readByte(self.pc + 0x1)
        operand2: UInt8 = self.readByte(self.pc + 0x2)
        fullAddress: UInt16 = self.combineTwoBytesToOneAddress(operand2, operand1)
        effectiveAddress: UInt16 = fullAddress + self.YRegister.getWriteableInt()
        valueFromMemory: UInt8 = self.readByte(effectiveAddress)
        
        self.logInstruction(self.readByte(self.pc).getHex(), "AND", operand1.getHex(), operand2.getHex(), instructionParameter=f"${fullAddress.getHex()},Y @ {effectiveAddress.getHex()} = {valueFromMemory.getHex()}")
        
        andResult = self.AND_Values(self.accumulatorRegister, valueFromMemory)
        self.accumulatorRegister = andResult
        
        self.updateNegativeFlag(self.accumulatorRegister)
        self.updateZeroFlag(self.accumulatorRegister)
        
        self.pc += 0x2
        return 4
    
    def AbsoluteY_EOR(self):
        operand1: UInt8 = self.readByte(self.pc + 0x1)
        operand2: UInt8 = self.readByte(self.pc + 0x2)
        fullAddress: UInt16 = self.combineTwoBytesToOneAddress(operand2, operand1)
        effectiveAddress: UInt16 = fullAddress + self.YRegister.getWriteableInt()
        valueFromMemory: UInt8 = self.readByte(effectiveAddress)
        
        self.logInstruction(self.readByte(self.pc).getHex(), "EOR", operand1.getHex(), operand2.getHex(), instructionParameter=f"${fullAddress.getHex()},Y @ {effectiveAddress.getHex()} = {valueFromMemory.getHex()}")
        
        andResult = self.EOR(self.accumulatorRegister, valueFromMemory)
        self.accumulatorRegister = andResult
        
        self.updateNegativeFlag(self.accumulatorRegister)
        self.updateZeroFlag(self.accumulatorRegister)
        
        self.pc += 0x2
        return 5
    
    def AbsoluteY_ADC(self):
        operand1: UInt8 = self.readByte(self.pc + 0x1)
        operand2: UInt8 = self.readByte(self.pc + 0x2)
        fullAddress: UInt16 = self.combineTwoBytesToOneAddress(operand2, operand1)
        effectiveAddress: UInt16 = fullAddress + self.YRegister.getWriteableInt()
        valueFromMemory: UInt8 = self.readByte(effectiveAddress)
        
        self.logInstruction(self.readByte(self.pc).getHex(), "ADC", operand1.getHex(), operand2.getHex(), instructionParameter=f"${fullAddress.getHex()},Y @ {effectiveAddress.getHex()} = {valueFromMemory.getHex()}")        
        
        resultInt8, carryFlag, negativeFlag, zeroFlag, overflowFlag = self.ADC(self.accumulatorRegister, valueFromMemory, self.carryFlag)

        self.carryFlag = carryFlag
        self.negativeFlag = negativeFlag
        self.zeroFlag = zeroFlag
        self.overflowFlag = overflowFlag
        
        self.accumulatorRegister = resultInt8
        
        self.pc += 0x2
        return 4
    
    def AbsoluteY_CMP(self):
        operand1: UInt8 = self.readByte(self.pc + 0x1)
        operand2: UInt8 = self.readByte(self.pc + 0x2)
        fullAddress: UInt16 = self.combineTwoBytesToOneAddress(operand2, operand1)
        effectiveAddress: UInt16 = fullAddress + self.YRegister.getWriteableInt()
        valueFromMemory: UInt8 = self.readByte(effectiveAddress)
        
        self.logInstruction(self.readByte(self.pc).getHex(), "CMP", operand1.getHex(), operand2.getHex(), instructionParameter=f"${fullAddress.getHex()},Y @ {effectiveAddress.getHex()} = {valueFromMemory.getHex()}")        
        
        compareResult, negativeFlag, zeroFlag, carryFlag = self.compareValues(self.accumulatorRegister, valueFromMemory)
        
        self.negativeFlag = negativeFlag
        self.zeroFlag = zeroFlag
        self.carryFlag = carryFlag
        
        self.pc += 0x2
        return 4
    
    def AbsoluteY_SBC(self):
        operand1: UInt8 = self.readByte(self.pc + 0x1)
        operand2: UInt8 = self.readByte(self.pc + 0x2)
        fullAddress: UInt16 = self.combineTwoBytesToOneAddress(operand2, operand1)
        effectiveAddress: UInt16 = fullAddress + self.YRegister.getWriteableInt()
        valueFromMemory: UInt8 = self.readByte(effectiveAddress)
        
        self.logInstruction(self.readByte(self.pc).getHex(), "SBC", operand1.getHex(), operand2.getHex(), instructionParameter=f"${fullAddress.getHex()},Y @ {effectiveAddress.getHex()} = {valueFromMemory.getHex()}")        
        
        accumulatorRegister, negativeFlag, zeroFlag, overflowFlag, carryFlag = self.SBC(self.accumulatorRegister, valueFromMemory, self.carryFlag)
        
        self.accumulatorRegister = accumulatorRegister
        self.negativeFlag = negativeFlag
        self.zeroFlag = zeroFlag
        self.overflowFlag = overflowFlag
        self.carryFlag = carryFlag
        
        self.pc += 0x2
        return 4
    
    def AbsoluteY_STA(self):
        operand1: UInt8 = self.readByte(self.pc + 0x1)
        operand2: UInt8 = self.readByte(self.pc + 0x2)
        fullAddress: UInt16 = self.combineTwoBytesToOneAddress(operand2, operand1)
        effectiveAddress: UInt16 = fullAddress + self.YRegister.getWriteableInt()
        valueFromMemory: UInt8 = self.readByte(effectiveAddress)
        
        self.logInstruction(self.readByte(self.pc).getHex(), "STA", operand1.getHex(), operand2.getHex(), instructionParameter=f"${fullAddress.getHex()},Y @ {effectiveAddress.getHex()} = {valueFromMemory.getHex()}")        
        
        self.STA(effectiveAddress)
        
        self.pc += 0x2
        return 5
    
    def ZeropageX_LDY(self):
        operand: UInt8 = self.readByte(self.pc + 0x1)
        zeropageAddress: UInt8 = operand + self.XRegister.value 
        value: UInt8 = self.readByte(zeropageAddress)
        self.logInstruction(self.readByte(self.pc).getHex(), "LDY", operand.getHex(), instructionParameter=f"${operand.getHex()},X @ {zeropageAddress.getHex()} = {value.getHex()}")
        
        self.YRegister = value
        self.updateNegativeFlag(self.YRegister)
        self.updateZeroFlag(self.YRegister)
        
        self.pc += 0x1
        return 4
    
    def ZeropageX_STY(self):
        operand: UInt8 = self.readByte(self.pc + 0x1)
        zeropageAddress: UInt8 = operand + self.XRegister.value 
        value: UInt8 = self.readByte(zeropageAddress)
        
        self.logInstruction(self.readByte(self.pc).getHex(), "STY", operand.getHex(), instructionParameter=f"${operand.getHex()},X @ {zeropageAddress.getHex()} = {value.getHex()}")        
        
        self.RAM.writeAddress(zeropageAddress, self.YRegister.getWriteableInt())
        
        self.pc += 0x1
        return 4
    
    
    def ZeropageX_ORA(self):
        operand: UInt8 = self.readByte(self.pc + 0x1)
        zeropageAddress: UInt8 = operand + self.XRegister.value 
        value: UInt8 = self.readByte(zeropageAddress)
        
        self.logInstruction(self.readByte(self.pc).getHex(), "ORA", operand.getHex(), instructionParameter=f"${operand.getHex()},X @ {zeropageAddress.getHex()} = {value.getHex()}")        
        
        orResult: Int8 = self.ORA(self.accumulatorRegister, value)
        self.accumulatorRegister = orResult
        
        self.updateNegativeFlag(self.accumulatorRegister)
        self.updateZeroFlag(self.accumulatorRegister)
        
        self.pc += 0x1
        return 4
    
    def ZeropageX_AND(self):
        operand: UInt8 = self.readByte(self.pc + 0x1)
        zeropageAddress: UInt8 = operand + self.XRegister.value 
        value: UInt8 = self.readByte(zeropageAddress)
        
        self.logInstruction(self.readByte(self.pc).getHex(), "AND", operand.getHex(), instructionParameter=f"${operand.getHex()},X @ {zeropageAddress.getHex()} = {value.getHex()}")
        
        andResult = self.AND_Values(self.accumulatorRegister, value)
        self.accumulatorRegister = andResult
        
        self.updateNegativeFlag(self.accumulatorRegister)
        self.updateZeroFlag(self.accumulatorRegister)
        
        self.pc += 0x1
        return 4
    
    def ZeropageX_EOR(self):
        operand: UInt8 = self.readByte(self.pc + 0x1)
        zeropageAddress: UInt8 = operand + self.XRegister.value 
        value: UInt8 = self.readByte(zeropageAddress)
        
        self.logInstruction(self.readByte(self.pc).getHex(), "EOR", operand.getHex(), instructionParameter=f"${operand.getHex()},X @ {zeropageAddress.getHex()} = {value.getHex()}")
        
        andResult = self.EOR(self.accumulatorRegister, value)
        self.accumulatorRegister = andResult
        
        self.updateNegativeFlag(self.accumulatorRegister)
        self.updateZeroFlag(self.accumulatorRegister)
        
        self.pc += 0x1
        return 5
    
    def ZeropageX_ADC(self):
        operand: UInt8 = self.readByte(self.pc + 0x1)
        zeropageAddress: UInt8 = operand + self.XRegister.value 
        value: UInt8 = self.readByte(zeropageAddress)
        
        self.logInstruction(self.readByte(self.pc).getHex(), "ADC", operand.getHex(), instructionParameter=f"${operand.getHex()},X @ {zeropageAddress.getHex()} = {value.getHex()}")        
        
        resultInt8, carryFlag, negativeFlag, zeroFlag, overflowFlag = self.ADC(self.accumulatorRegister, value, self.carryFlag)

        self.carryFlag = carryFlag
        self.negativeFlag = negativeFlag
        self.zeroFlag = zeroFlag
        self.overflowFlag = overflowFlag
        
        self.accumulatorRegister = resultInt8
        
        self.pc += 0x1
        return 4
    
    def ZeropageX_CMP(self):
        operand: UInt8 = self.readByte(self.pc + 0x1)
        zeropageAddress: UInt8 = operand + self.XRegister.value 
        value: UInt8 = self.readByte(zeropageAddress)
        
        self.logInstruction(self.readByte(self.pc).getHex(), "CMP", operand.getHex(), instructionParameter=f"${operand.getHex()},X @ {zeropageAddress.getHex()} = {value.getHex()}")        
        
        compareResult, negativeFlag, zeroFlag, carryFlag = self.compareValues(self.accumulatorRegister, value)
        
        self.negativeFlag = negativeFlag
        self.zeroFlag = zeroFlag
        self.carryFlag = carryFlag
        
        self.pc += 0x1
        return 4
    def ZeropageX_SBC(self):
        operand: UInt8 = self.readByte(self.pc + 0x1)
        zeropageAddress: UInt8 = operand + self.XRegister.value 
        value: UInt8 = self.readByte(zeropageAddress)
        
        self.logInstruction(self.readByte(self.pc).getHex(), "SBC", operand.getHex(), instructionParameter=f"${operand.getHex()},X @ {zeropageAddress.getHex()} = {value.getHex()}")        
        
        accumulatorRegister, negativeFlag, zeroFlag, overflowFlag, carryFlag = self.SBC(self.accumulatorRegister, value, self.carryFlag)
        
        self.accumulatorRegister = accumulatorRegister
        self.negativeFlag = negativeFlag
        self.zeroFlag = zeroFlag
        self.overflowFlag = overflowFlag
        self.carryFlag = carryFlag
        
        self.pc += 0x1
        return 4
    
    def ZeropageX_STA(self):
        operand: UInt8 = self.readByte(self.pc + 0x1)
        zeropageAddress: UInt8 = operand + self.XRegister.value 
        value: UInt8 = self.readByte(zeropageAddress)
        
        self.logInstruction(self.readByte(self.pc).getHex(), "STA", operand.getHex(), instructionParameter=f"${operand.getHex()},X @ {zeropageAddress.getHex()} = {value.getHex()}")        
        
        self.STA(zeropageAddress)
        
        self.pc += 0x1
        return 5
    
    def ZeropageX_LDA(self):
        operand: UInt8 = self.readByte(self.pc + 0x1)
        zeropageAddress: UInt8 = operand + self.XRegister.value
        value: UInt8 = self.readByte(zeropageAddress)
        
        self.logInstruction(self.readByte(self.pc).getHex(), "LDA", operand.getHex(), instructionParameter=f"${operand.getHex()},X @ {zeropageAddress.getHex()} = {value.getHex()}")
        
        self.LDA(zeropageAddress)
        self.updateNegativeFlag(self.accumulatorRegister)
        self.updateZeroFlag(self.accumulatorRegister)
        
        self.pc += 0x1
        return 4
    
    def ZeropageX_LSR(self):
        operand: UInt8 = self.readByte(self.pc + 0x1)
        zeropageAddress: UInt8 = operand + self.XRegister.value 
        valueToShift: UInt8 = self.readByte(zeropageAddress)
        
        self.logInstruction(self.readByte(self.pc).getHex(), "LSR", operand1=operand.getHex(), instructionParameter=f"${operand.getHex()},X @ {zeropageAddress.getHex()} = {valueToShift.getHex()}")
        
        result, carryFlag, negativeFlag, zeroFlag = self.LSR(valueToShift)
        self.RAM.writeAddress(zeropageAddress, result.getWriteableInt())
        self.carryFlag = carryFlag
        self.negativeFlag = negativeFlag
        self.zeroFlag = zeroFlag
        
        self.pc += 0x1
        return 6
    
    def ZeropageX_ASL(self):
        operand: UInt8 = self.readByte(self.pc + 0x1)
        zeropageAddress: UInt8 = operand + self.XRegister.value 
        valueToShift: UInt8 = self.readByte(zeropageAddress)
        
        self.logInstruction(self.readByte(self.pc).getHex(), "ASL", operand1=operand.getHex(), instructionParameter=f"${operand.getHex()},X @ {zeropageAddress.getHex()} = {valueToShift.getHex()}")
        
        result, carryFlag, negativeFlag, zeroFlag = self.ASL(valueToShift)
        
        self.RAM.writeAddress(zeropageAddress, result.getWriteableInt())
        self.carryFlag = carryFlag
        self.negativeFlag = negativeFlag
        self.zeroFlag = zeroFlag
        
        self.pc += 0x1
        return 6
    
    def ZeropageX_ROR(self):
        operand: UInt8 = self.readByte(self.pc + 0x1)
        zeropageAddress: UInt8 = operand + self.XRegister.value 
        valueToShift: UInt8 = self.readByte(zeropageAddress)
        
        self.logInstruction(self.readByte(self.pc).getHex(), "ROR", operand1=operand.getHex(), instructionParameter=f"${operand.getHex()},X @ {zeropageAddress.getHex()} = {valueToShift.getHex()}")
        
        result, carryFlag, negativeFlag, zeroFlag = self.ROR(valueToShift, self.carryFlag)
        
        self.RAM.writeAddress(zeropageAddress, result.getWriteableInt())
        self.carryFlag = carryFlag
        self.negativeFlag = negativeFlag
        self.zeroFlag = zeroFlag
        
        self.pc += 0x1
        return 6
    
    def ZeropageX_ROL(self):
        operand: UInt8 = self.readByte(self.pc + 0x1)
        zeropageAddress: UInt8 = operand + self.XRegister.value 
        valueToShift: UInt8 = self.readByte(zeropageAddress)
        self.logInstruction(self.readByte(self.pc).getHex(), "ROL", operand1=operand.getHex(), instructionParameter=f"${operand.getHex()},X @ {zeropageAddress.getHex()} = {valueToShift.getHex()}")
        
        result, carryFlag, negativeFlag, zeroFlag = self.ROL(valueToShift, self.carryFlag)
        self.RAM.writeAddress(zeropageAddress, result.getWriteableInt())
        self.carryFlag = carryFlag
        self.negativeFlag = negativeFlag
        self.zeroFlag = zeroFlag
        
        self.pc += 0x1
        return 6
    
    def ZeropageX_INC(self):
        operand: UInt8 = self.readByte(self.pc + 0x1)
        zeropageAddress: UInt8 = operand + self.XRegister.value 
        valueToIncrement: UInt8 = self.readByte(zeropageAddress)
        self.logInstruction(self.readByte(self.pc).getHex(), "INC", operand1=operand.getHex(), instructionParameter=f"${operand.getHex()},X @ {zeropageAddress.getHex()} = {valueToIncrement.getHex()}")
        
        newValue = valueToIncrement + 1
        self.RAM.writeAddress(zeropageAddress, newValue.getWriteableInt())
        
        self.updateNegativeFlag(newValue)
        self.updateZeroFlag(newValue)
        
        self.pc += 0x1
        return 6
    
    def ZeropageX_DEC(self):
        operand: UInt8 = self.readByte(self.pc + 0x1)
        zeropageAddress: UInt8 = operand + self.XRegister.value 
        valueToIncrement: UInt8 = self.readByte(zeropageAddress)
        self.logInstruction(self.readByte(self.pc).getHex(), "DEC", operand1=operand.getHex(), instructionParameter=f"${operand.getHex()},X @ {zeropageAddress.getHex()} = {valueToIncrement.getHex()}")
        
        newValue = valueToIncrement - 1
        self.RAM.writeAddress(zeropageAddress, newValue.getWriteableInt())
        
        self.updateNegativeFlag(newValue)
        self.updateZeroFlag(newValue)
        
        self.pc += 0x1
        return 6
    
    def ZeropageY_LDX(self):
        operand: UInt8 = self.readByte(self.pc + 0x1)
        zeropageAddress: UInt8 = operand + self.YRegister.value 
        value: UInt8 = self.readByte(zeropageAddress)
        self.logInstruction(self.readByte(self.pc).getHex(), "LDX", operand.getHex(), instructionParameter=f"${operand.getHex()},Y @ {zeropageAddress.getHex()} = {value.getHex()}")
        
        self.XRegister = value
        self.updateNegativeFlag(self.XRegister)
        self.updateZeroFlag(self.XRegister)
        
        self.pc += 0x1
        return 4
    
    def ZeropageY_STX(self):
        operand: UInt8 = self.readByte(self.pc + 0x1)
        zeropageAddress: UInt8 = operand + self.YRegister.value 
        value: UInt8 = self.readByte(zeropageAddress)
        
        self.logInstruction(self.readByte(self.pc).getHex(), "STX", operand.getHex(), instructionParameter=f"${operand.getHex()},Y @ {zeropageAddress.getHex()} = {value.getHex()}")        
        
        self.RAM.writeAddress(zeropageAddress, self.XRegister.getWriteableInt())
        
        self.pc += 0x1
        return 4
    
    def AbsoluteX_LDY(self):
        operand1: UInt8 = self.readByte(self.pc + 0x1)
        operand2: UInt8 = self.readByte(self.pc + 0x2)
        fullAddress: UInt16 = self.combineTwoBytesToOneAddress(operand2, operand1)
        effectiveAddress: UInt16 = fullAddress + self.XRegister.getWriteableInt()
        valueFromMemory: UInt8 = self.readByte(effectiveAddress)
        
        self.logInstruction(self.readByte(self.pc).getHex(), "LDY", operand1.getHex(), operand2.getHex(), f"${fullAddress.getHex()},X @ {effectiveAddress.getHex()} = {valueFromMemory.getHex()}")
        
        self.YRegister = valueFromMemory
        self.updateNegativeFlag(self.YRegister)
        self.updateZeroFlag(self.YRegister)
        
        self.pc += 0x2
        return 4
    
    def AbsoluteX_ORA(self):
        operand1: UInt8 = self.readByte(self.pc + 0x1)
        operand2: UInt8 = self.readByte(self.pc + 0x2)
        fullAddress: UInt16 = self.combineTwoBytesToOneAddress(operand2, operand1)
        effectiveAddress: UInt16 = fullAddress + self.XRegister.getWriteableInt()
        valueFromMemory: UInt8 = self.readByte(effectiveAddress)
        
        self.logInstruction(self.readByte(self.pc).getHex(), "ORA", operand1.getHex(), operand2.getHex(), f"${fullAddress.getHex()},X @ {effectiveAddress.getHex()} = {valueFromMemory.getHex()}")        
        
        orResult: Int8 = self.ORA(self.accumulatorRegister, valueFromMemory)
        self.accumulatorRegister = orResult
        
        self.updateNegativeFlag(self.accumulatorRegister)
        self.updateZeroFlag(self.accumulatorRegister)
        
        self.pc += 0x2
        return 4
    
    def AbsoluteX_AND(self):
        operand1: UInt8 = self.readByte(self.pc + 0x1)
        operand2: UInt8 = self.readByte(self.pc + 0x2)
        fullAddress: UInt16 = self.combineTwoBytesToOneAddress(operand2, operand1)
        effectiveAddress: UInt16 = fullAddress + self.XRegister.getWriteableInt()
        valueFromMemory: UInt8 = self.readByte(effectiveAddress)
        
        self.logInstruction(self.readByte(self.pc).getHex(), "AND", operand1.getHex(), operand2.getHex(), f"${fullAddress.getHex()},X @ {effectiveAddress.getHex()} = {valueFromMemory.getHex()}")
        
        andResult = self.AND_Values(self.accumulatorRegister, valueFromMemory)
        self.accumulatorRegister = andResult
        
        self.updateNegativeFlag(self.accumulatorRegister)
        self.updateZeroFlag(self.accumulatorRegister)
        
        self.pc += 0x2
        return 4
    
    def AbsoluteX_EOR(self):
        operand1: UInt8 = self.readByte(self.pc + 0x1)
        operand2: UInt8 = self.readByte(self.pc + 0x2)
        fullAddress: UInt16 = self.combineTwoBytesToOneAddress(operand2, operand1)
        effectiveAddress: UInt16 = fullAddress + self.XRegister.getWriteableInt()
        valueFromMemory: UInt8 = self.readByte(effectiveAddress)
        
        self.logInstruction(self.readByte(self.pc).getHex(), "EOR", operand1.getHex(), operand2.getHex(), f"${fullAddress.getHex()},X @ {effectiveAddress.getHex()} = {valueFromMemory.getHex()}")
        
        andResult = self.EOR(self.accumulatorRegister, valueFromMemory)
        self.accumulatorRegister = andResult
        
        self.updateNegativeFlag(self.accumulatorRegister)
        self.updateZeroFlag(self.accumulatorRegister)
        
        self.pc += 0x2
        return 4
    
    def AbsoluteX_ADC(self):
        operand1: UInt8 = self.readByte(self.pc + 0x1)
        operand2: UInt8 = self.readByte(self.pc + 0x2)
        fullAddress: UInt16 = self.combineTwoBytesToOneAddress(operand2, operand1)
        effectiveAddress: UInt16 = fullAddress + self.XRegister.getWriteableInt()
        valueFromMemory: UInt8 = self.readByte(effectiveAddress)
        
        self.logInstruction(self.readByte(self.pc).getHex(), "ADC", operand1.getHex(), operand2.getHex(), f"${fullAddress.getHex()},X @ {effectiveAddress.getHex()} = {valueFromMemory.getHex()}")        
        
        resultInt8, carryFlag, negativeFlag, zeroFlag, overflowFlag = self.ADC(self.accumulatorRegister, valueFromMemory, self.carryFlag)

        self.carryFlag = carryFlag
        self.negativeFlag = negativeFlag
        self.zeroFlag = zeroFlag
        self.overflowFlag = overflowFlag
        
        self.accumulatorRegister = resultInt8
        
        self.pc += 0x2
        return 4
    
    def AbsoluteX_CMP(self):
        operand1: UInt8 = self.readByte(self.pc + 0x1)
        operand2: UInt8 = self.readByte(self.pc + 0x2)
        fullAddress: UInt16 = self.combineTwoBytesToOneAddress(operand2, operand1)
        effectiveAddress: UInt16 = fullAddress + self.XRegister.getWriteableInt()
        valueFromMemory: UInt8 = self.readByte(effectiveAddress)
        
        self.logInstruction(self.readByte(self.pc).getHex(), "CMP", operand1.getHex(), operand2.getHex(), f"${fullAddress.getHex()},X @ {effectiveAddress.getHex()} = {valueFromMemory.getHex()}")        
        
        compareResult, negativeFlag, zeroFlag, carryFlag = self.compareValues(self.accumulatorRegister, valueFromMemory)
        
        self.negativeFlag = negativeFlag
        self.zeroFlag = zeroFlag
        self.carryFlag = carryFlag
        
        self.pc += 0x2
        return 4
    
    def AbsoluteX_SBC(self):
        operand1: UInt8 = self.readByte(self.pc + 0x1)
        operand2: UInt8 = self.readByte(self.pc + 0x2)
        fullAddress: UInt16 = self.combineTwoBytesToOneAddress(operand2, operand1)
        effectiveAddress: UInt16 = fullAddress + self.XRegister.getWriteableInt()
        valueFromMemory: UInt8 = self.readByte(effectiveAddress)
        
        self.logInstruction(self.readByte(self.pc).getHex(), "SBC", operand1.getHex(), operand2.getHex(), f"${fullAddress.getHex()},X @ {effectiveAddress.getHex()} = {valueFromMemory.getHex()}")        
        
        accumulatorRegister, negativeFlag, zeroFlag, overflowFlag, carryFlag = self.SBC(self.accumulatorRegister, valueFromMemory, self.carryFlag)
        
        self.accumulatorRegister = accumulatorRegister
        self.negativeFlag = negativeFlag
        self.zeroFlag = zeroFlag
        self.overflowFlag = overflowFlag
        self.carryFlag = carryFlag
        
        self.pc += 0x2
        return 4
    
    def AbsoluteX_STA(self):
        operand1: UInt8 = self.readByte(self.pc + 0x1)
        operand2: UInt8 = self.readByte(self.pc + 0x2)
        fullAddress: UInt16 = self.combineTwoBytesToOneAddress(operand2, operand1)
        effectiveAddress: UInt16 = fullAddress + self.XRegister.getWriteableInt()
        valueFromMemory: UInt8 = self.readByte(effectiveAddress)
        
        self.logInstruction(self.readByte(self.pc).getHex(), "STA", operand1.getHex(), operand2.getHex(), f"${fullAddress.getHex()},X @ {effectiveAddress.getHex()} = {valueFromMemory.getHex()}")        
        
        self.STA(effectiveAddress)
        
        self.pc += 0x2
        return 4
    
    def AbsoluteX_LDA(self):
        operand1: UInt8 = self.readByte(self.pc + 0x1)
        operand2: UInt8 = self.readByte(self.pc + 0x2)
        fullAddress: UInt16 = self.combineTwoBytesToOneAddress(operand2, operand1)
        effectiveAddress: UInt16 = fullAddress + self.XRegister.getWriteableInt()
        valueFromMemory: UInt8 = self.readByte(effectiveAddress)
        
        self.logInstruction(self.readByte(self.pc).getHex(), "LDA", operand1.getHex(), operand2.getHex(), f"${fullAddress.getHex()},X @ {effectiveAddress.getHex()} = {valueFromMemory.getHex()}")
        
        self.LDA(effectiveAddress)
        self.updateNegativeFlag(self.accumulatorRegister)
        self.updateZeroFlag(self.accumulatorRegister)
        
        self.pc += 0x2
        return 4
    
    def AbsoluteX_LSR(self):
        operand1: UInt8 = self.readByte(self.pc + 0x1)
        operand2: UInt8 = self.readByte(self.pc + 0x2)
        fullAddress: UInt16 = self.combineTwoBytesToOneAddress(operand2, operand1)
        effectiveAddress: UInt16 = fullAddress + self.XRegister.getWriteableInt()
        valueFromMemory: UInt8 = self.readByte(effectiveAddress)
        
        self.logInstruction(self.readByte(self.pc).getHex(), "LSR", operand1.getHex(), operand2.getHex(), f"${fullAddress.getHex()},X @ {effectiveAddress.getHex()} = {valueFromMemory.getHex()}")
        
        result, carryFlag, negativeFlag, zeroFlag = self.LSR(valueFromMemory)
        self.RAM.writeAddress(effectiveAddress, result.getWriteableInt())
        self.carryFlag = carryFlag
        self.negativeFlag = negativeFlag
        self.zeroFlag = zeroFlag
        
        self.pc += 0x2
        return 7
    
    def AbsoluteX_ASL(self):
        operand1: UInt8 = self.readByte(self.pc + 0x1)
        operand2: UInt8 = self.readByte(self.pc + 0x2)
        fullAddress: UInt16 = self.combineTwoBytesToOneAddress(operand2, operand1)
        effectiveAddress: UInt16 = fullAddress + self.XRegister.getWriteableInt()
        valueFromMemory: UInt8 = self.readByte(effectiveAddress)
        
        self.logInstruction(self.readByte(self.pc).getHex(), "ASL", operand1.getHex(), operand2.getHex(), f"${fullAddress.getHex()},X @ {effectiveAddress.getHex()} = {valueFromMemory.getHex()}")
        
        result, carryFlag, negativeFlag, zeroFlag = self.ASL(valueFromMemory)
        
        self.RAM.writeAddress(effectiveAddress, result.getWriteableInt())
        self.carryFlag = carryFlag
        self.negativeFlag = negativeFlag
        self.zeroFlag = zeroFlag
        
        self.pc += 0x2
        return 7
    
    def AbsoluteX_ROR(self):
        operand1: UInt8 = self.readByte(self.pc + 0x1)
        operand2: UInt8 = self.readByte(self.pc + 0x2)
        fullAddress: UInt16 = self.combineTwoBytesToOneAddress(operand2, operand1)
        effectiveAddress: UInt16 = fullAddress + self.XRegister.getWriteableInt()
        valueFromMemory: UInt8 = self.readByte(effectiveAddress)
        
        self.logInstruction(self.readByte(self.pc).getHex(), "ROR", operand1.getHex(), operand2.getHex(), f"${fullAddress.getHex()},X @ {effectiveAddress.getHex()} = {valueFromMemory.getHex()}")
        
        result, carryFlag, negativeFlag, zeroFlag = self.ROR(valueFromMemory, self.carryFlag)
        
        self.RAM.writeAddress(effectiveAddress, result.getWriteableInt())
        self.carryFlag = carryFlag
        self.negativeFlag = negativeFlag
        self.zeroFlag = zeroFlag
        
        self.pc += 0x2
        return 7
    
    def AbsoluteX_ROL(self):
        operand1: UInt8 = self.readByte(self.pc + 0x1)
        operand2: UInt8 = self.readByte(self.pc + 0x2)
        fullAddress: UInt16 = self.combineTwoBytesToOneAddress(operand2, operand1)
        effectiveAddress: UInt16 = fullAddress + self.XRegister.getWriteableInt()
        valueFromMemory: UInt8 = self.readByte(effectiveAddress)
        self.logInstruction(self.readByte(self.pc).getHex(), "ROL", operand1.getHex(), operand2.getHex(), f"${fullAddress.getHex()},X @ {effectiveAddress.getHex()} = {valueFromMemory.getHex()}")
        
        result, carryFlag, negativeFlag, zeroFlag = self.ROL(valueFromMemory, self.carryFlag)
        self.RAM.writeAddress(effectiveAddress, result.getWriteableInt())
        self.carryFlag = carryFlag
        self.negativeFlag = negativeFlag
        self.zeroFlag = zeroFlag
        
        self.pc += 0x2
        return 7
    
    def AbsoluteX_INC(self):
        operand1: UInt8 = self.readByte(self.pc + 0x1)
        operand2: UInt8 = self.readByte(self.pc + 0x2)
        fullAddress: UInt16 = self.combineTwoBytesToOneAddress(operand2, operand1)
        effectiveAddress: UInt16 = fullAddress + self.XRegister.getWriteableInt()
        valueFromMemory: UInt8 = self.readByte(effectiveAddress)
        self.logInstruction(self.readByte(self.pc).getHex(), "INC", operand1.getHex(), operand2.getHex(), f"${fullAddress.getHex()},X @ {effectiveAddress.getHex()} = {valueFromMemory.getHex()}")
        
        newValue = valueFromMemory + 1
        self.RAM.writeAddress(effectiveAddress, newValue.getWriteableInt())
        
        self.updateNegativeFlag(newValue)
        self.updateZeroFlag(newValue)
        
        self.pc += 0x2
        return 7
    
    def AbsoluteX_DEC(self):
        operand1: UInt8 = self.readByte(self.pc + 0x1)
        operand2: UInt8 = self.readByte(self.pc + 0x2)
        fullAddress: UInt16 = self.combineTwoBytesToOneAddress(operand2, operand1)
        effectiveAddress: UInt16 = fullAddress + self.XRegister.getWriteableInt()
        valueFromMemory: UInt8 = self.readByte(effectiveAddress)
        self.logInstruction(self.readByte(self.pc).getHex(), "DEC", operand1.getHex(), operand2.getHex(), f"${fullAddress.getHex()},X @ {effectiveAddress.getHex()} = {valueFromMemory.getHex()}")
        
        newValue = valueFromMemory - 1
        self.RAM.writeAddress(effectiveAddress, newValue.getWriteableInt())
        
        self.updateNegativeFlag(newValue)
        self.updateZeroFlag(newValue)
        
        self.pc += 0x2
        return 7
    
    def AbsoluteY_LDX(self):
        operand1: UInt8 = self.readByte(self.pc + 0x1)
        operand2: UInt8 = self.readByte(self.pc + 0x2)
        fullAddress: UInt16 = self.combineTwoBytesToOneAddress(operand2, operand1)
        effectiveAddress: UInt16 = fullAddress + self.YRegister.getWriteableInt()
        valueFromMemory: UInt8 = self.readByte(effectiveAddress)

        self.logInstruction(self.readByte(self.pc).getHex(), "LDX", operand1.getHex(), operand2.getHex(), instructionParameter=f"${fullAddress.getHex()},Y @ {effectiveAddress.getHex()} = {valueFromMemory.getHex()}")

        self.XRegister = valueFromMemory

        self.updateNegativeFlag(self.XRegister)
        self.updateZeroFlag(self.XRegister)

        self.pc += 0x2
        return 4
    
    
    
    # ILLEGAL OPCODES
    def IllegalNOP_OneByte(self):
        self.logInstruction(self.readByte(self.pc).getHex(), "NOP", isIllegal=True)
        return 2
    
    def IllegalNOP_TwoByte(self):
        operand = self.readByte(self.pc + 0x1)
        opcodeHex = self.readByte(self.pc).getHex()
        
        self.logInstruction(opcodeHex, "NOP", operand1=operand.getHex(), isIllegal=True)
        self.pc += 0x1
        return 2
    
    def IllegalNOP_ThreeByte(self):
        operand1 = self.readByte(self.pc + 0x1)
        operand2 = self.readByte(self.pc + 0x2)
        opcodeHex = self.readByte(self.pc).getHex()
        
        self.logInstruction(opcodeHex, "NOP", operand1=operand1.getHex(), operand2=operand2.getHex(), isIllegal=True)
        self.pc += 0x2
        return 2
    
    def IllegalIndirectX_LAX(self):
        operand: UInt8 = self.readByte(self.pc + 0x1)
        zeropageAddress: UInt8 = operand + self.XRegister
        lowAddressByte: UInt8 = self.readByte(zeropageAddress)
        highAddressByte: UInt8 = self.readByte(zeropageAddress + 0x1)
        fullAddress: UInt16 = self.combineTwoBytesToOneAddress(highAddressByte, lowAddressByte)
        value: UInt8 = self.readByte(fullAddress)

        self.logInstruction(self.readByte(self.pc).getHex(), "LAX", operand1=operand.getHex(), instructionParameter=f"(${operand.getHex()},X) @ {zeropageAddress.getHex()} = {fullAddress.getHex()} = {value.getHex()}", isIllegal=True)

        self.LAX(value)
        
        self.pc += 0x1
        return 6
    
    def IllegalZeropageLAX(self):
        operand: UInt8 = self.readByte(self.pc + 0x1)
        value: UInt8 = self.readByte(operand)

        self.logInstruction(self.readByte(self.pc).getHex(), "LAX", operand1=operand.getHex(), instructionParameter=f"${operand.getHex()} = {value.getHex()}", isIllegal=True)

        self.LAX(value)
        
        self.pc += 0x1
        return 3
    
    def IllegalAbsoluteLAX(self):
        operand1: UInt8 = self.readByte(self.pc + 0x1)
        operand2: UInt8 = self.readByte(self.pc + 0x2)
        address: UInt16 = self.combineTwoBytesToOneAddress(operand2, operand1)
        value: UInt8 = self.readByte(address)

        self.logInstruction(self.readByte(self.pc).getHex(), "LAX", operand1.getHex(), operand2.getHex(), instructionParameter=f"${address.getHex()} = {value.getHex()}", isIllegal=True)

        self.LAX(value)
        
        self.pc += 0x2
        return 4
    
    def IllegalIndirectY_LAX(self):
        operand: UInt8 = self.readByte(self.pc + 0x1)
        baseAddressLow: UInt8 = self.readByte(operand)
        baseAddressHigh: UInt8 = self.readByte(operand + 0x1)
        baseAddress: UInt16 = self.combineTwoBytesToOneAddress(baseAddressHigh, baseAddressLow)
        newAddress: UInt8 = baseAddress + self.YRegister.getWriteableInt()
        valueToTest: UInt8 = self.readByte(newAddress)
        
        self.logInstruction(self.readByte(self.pc).getHex(), "LAX", operand.getHex(), instructionParameter=f"(${operand.getHex()}),Y = {baseAddress.getHex()} @ {newAddress.getHex()} = {valueToTest.getHex()}", isIllegal=True)        
        
        self.LAX(valueToTest)
        
        self.pc += 0x1
        return 5
    
    def IllegalZeropageY_LAX(self):
        operand: UInt8 = self.readByte(self.pc + 0x1)
        zeropageAddress: UInt8 = operand + self.YRegister.value
        value: UInt8 = self.readByte(zeropageAddress)
        
        self.logInstruction(self.readByte(self.pc).getHex(), "LAX", operand.getHex(), instructionParameter=f"${operand.getHex()},Y @ {zeropageAddress.getHex()} = {value.getHex()}", isIllegal=True)
        
        self.LAX(value)
        
        self.pc += 0x1
        return 4
    
    def IllegalAbsoluteY_LAX(self):
        operand1: UInt8 = self.readByte(self.pc + 0x1)
        operand2: UInt8 = self.readByte(self.pc + 0x2)
        fullAddress: UInt16 = self.combineTwoBytesToOneAddress(operand2, operand1)
        effectiveAddress: UInt16 = fullAddress + self.YRegister.getWriteableInt()
        valueFromMemory: UInt8 = self.readByte(effectiveAddress)
        
        self.logInstruction(self.readByte(self.pc).getHex(), "LAX", operand1.getHex(), operand2=operand2.getHex(), instructionParameter=f"${fullAddress.getHex()},Y @ {effectiveAddress.getHex()} = {valueFromMemory.getHex()}", isIllegal=True)        
        
        self.LAX(valueFromMemory)
        
        self.pc += 0x2
        return 4
    
    def IllegalIndirectX_SAX(self):
        operand: UInt8 = self.readByte(self.pc + 0x1)
        zeropageAddress: UInt8 = operand + self.XRegister
        lowAddressByte: UInt8 = self.readByte(zeropageAddress)
        highAddressByte: UInt8 = self.readByte(zeropageAddress + 0x1)
        fullAddress: UInt16 = self.combineTwoBytesToOneAddress(highAddressByte, lowAddressByte)
        memoryBefore: UInt8 = self.readByte(fullAddress)
        
        self.logInstruction(self.readByte(self.pc).getHex(), "SAX", operand.getHex(), instructionParameter=f"(${operand.getHex()},X) @ {(zeropageAddress).getHex()} = {fullAddress.getHex()} = {memoryBefore.getHex()}", isIllegal=True)
        
        andResult: Int8 = self.AND_Values(self.accumulatorRegister, self.XRegister)
        self.RAM.writeAddress(fullAddress, andResult.getWriteableInt())
        
        self.pc += 0x1
        return 6
    
    def IllegalZeropageSAX(self):
        operand: UInt8 = self.readByte(self.pc + 0x1)
        value: UInt8 = self.readByte(operand)
        
        self.logInstruction(self.readByte(self.pc).getHex(), "SAX", operand.getHex(), instructionParameter=f"${operand.getHex()} = {value.getHex()}", isIllegal=True)
        
        andResult = self.AND_Values(self.accumulatorRegister, self.XRegister)
        self.RAM.writeAddress(operand, andResult.getWriteableInt())
        
        self.pc += 0x1
        return 3
    
    def IllegalAbsoluteSAX(self):
        PCL: UInt8 = self.readByte(self.pc + 0x1)
        PCH: UInt8 = self.readByte(self.pc + 0x2)
        address: UInt16 = self.combineTwoBytesToOneAddress(PCH, PCL)
        valueToTest: UInt8 = self.readByte(address)
        
        self.logInstruction(self.readByte(self.pc).getHex(), "SAX", PCL.getHex(), PCH.getHex(), instructionParameter=f"${address.getHex()} = {valueToTest.getHex()}", isIllegal=True)
        
        andResult = self.AND_Values(self.accumulatorRegister, self.XRegister)
        self.RAM.writeAddress(address, andResult.getWriteableInt())
        
        self.pc += 0x2
        return 4
    
    def IllegalZeropageY_SAX(self):
        operand: UInt8 = self.readByte(self.pc + 0x1)
        zeropageAddress: UInt8 = operand + self.YRegister.value 
        value: UInt8 = self.readByte(zeropageAddress)
        
        self.logInstruction(self.readByte(self.pc).getHex(), "SAX", operand.getHex(), instructionParameter=f"${operand.getHex()},Y @ {zeropageAddress.getHex()} = {value.getHex()}", isIllegal=True)
        
        andResult = self.AND_Values(self.accumulatorRegister, self.XRegister)
        self.RAM.writeAddress(zeropageAddress, andResult.getWriteableInt())

        self.pc += 0x1
        return 4
    
    def IllegalSBC(self): #USBC
        return self.ImmediateSBC(illegal=True)
    
    def IllegalIndirectX_DCP(self):
        operand: UInt8 = self.readByte(self.pc + 0x1)
        zeropageAddress: UInt8 = operand + self.XRegister
        lowAddressByte: UInt8 = self.readByte(zeropageAddress)
        highAddressByte: UInt8 = self.readByte(zeropageAddress + 0x1)
        fullAddress: UInt16 = self.combineTwoBytesToOneAddress(highAddressByte, lowAddressByte)
        memoryBefore: UInt8 = self.readByte(fullAddress)
        
        self.logInstruction(self.readByte(self.pc).getHex(), "DCP", operand.getHex(), instructionParameter=f"(${operand.getHex()},X) @ {(zeropageAddress).getHex()} = {fullAddress.getHex()} = {memoryBefore.getHex()}", isIllegal=True)
        
        memoryBefore -= 1
        self.RAM.writeAddress(fullAddress, memoryBefore.getWriteableInt())
        
        compareResult, negativeFlag, zeroFlag, carryFlag = self.compareValues(self.accumulatorRegister, memoryBefore)
        self.negativeFlag = negativeFlag
        self.zeroFlag = zeroFlag
        self.carryFlag = carryFlag
        
        self.pc += 0x1
        return 8
    
    def IllegalZeropageDCP(self):
        operand: UInt8 = self.readByte(self.pc + 0x1)
        operandValue: UInt8 = self.readByte(operand)
        
        self.logInstruction(self.readByte(self.pc).getHex(), "DCP", operand.getHex(), instructionParameter=f"${operand.getHex()} = {operandValue.getHex()}", isIllegal=True)        
        
        operandValue -= 1
        self.RAM.writeAddress(operand, operandValue.getWriteableInt())
        
        compareResult, negativeFlag, zeroFlag, carryFlag = self.compareValues(self.accumulatorRegister, operandValue)
        self.negativeFlag = negativeFlag
        self.zeroFlag = zeroFlag
        self.carryFlag = carryFlag
        
        self.pc += 0x1
        return 5
    
    def IllegalAbsoluteDCP(self):
        PCL: UInt8 = self.readByte(self.pc + 0x1)
        PCH: UInt8 = self.readByte(self.pc + 0x2)
        address: UInt16 = self.combineTwoBytesToOneAddress(PCH, PCL)
        valueToTest: UInt8 = self.readByte(address)
        
        self.logInstruction(self.readByte(self.pc).getHex(), "DCP", PCL.getHex(), PCH.getHex(), instructionParameter=f"${address.getHex()} = {valueToTest.getHex()}", isIllegal=True)        
        
        valueToTest -= 1
        self.RAM.writeAddress(address, valueToTest.getWriteableInt())
        
        compareResult, negativeFlag, zeroFlag, carryFlag = self.compareValues(self.accumulatorRegister, valueToTest)
        self.negativeFlag = negativeFlag
        self.zeroFlag = zeroFlag
        self.carryFlag = carryFlag
        
        self.pc += 0x2
        return 6
    
    def IllegalIndirectY_DCP(self):
        operand: UInt8 = self.readByte(self.pc + 0x1)
        baseAddressLow: UInt8 = self.readByte(operand)
        baseAddressHigh: UInt8 = self.readByte(operand + 0x1)
        baseAddress: UInt16 = self.combineTwoBytesToOneAddress(baseAddressHigh, baseAddressLow)
        newAddress: UInt8 = baseAddress + self.YRegister.getWriteableInt()
        valueToTest: UInt8 = self.readByte(newAddress)
        
        self.logInstruction(self.readByte(self.pc).getHex(), "DCP", operand.getHex(), instructionParameter=f"(${operand.getHex()}),Y = {baseAddress.getHex()} @ {newAddress.getHex()} = {valueToTest.getHex()}", isIllegal=True)        
        
        valueToTest -= 1
        self.RAM.writeAddress(newAddress, valueToTest.getWriteableInt())
        
        compareResult, negativeFlag, zeroFlag, carryFlag = self.compareValues(self.accumulatorRegister, valueToTest)
        self.negativeFlag = negativeFlag
        self.zeroFlag = zeroFlag
        self.carryFlag = carryFlag
        
        self.pc += 0x1
        return 8
    
    def IllegalZeropageX_DCP(self):
        operand: UInt8 = self.readByte(self.pc + 0x1)
        zeropageAddress: UInt8 = operand + self.XRegister.value 
        value: UInt8 = self.readByte(zeropageAddress)
        
        self.logInstruction(self.readByte(self.pc).getHex(), "DCP", operand.getHex(), instructionParameter=f"${operand.getHex()},X @ {zeropageAddress.getHex()} = {value.getHex()}", isIllegal=True)
        
        value -= 1
        self.RAM.writeAddress(zeropageAddress, value.getWriteableInt())
        
        compareResult, negativeFlag, zeroFlag, carryFlag = self.compareValues(self.accumulatorRegister, value)
        self.negativeFlag = negativeFlag
        self.zeroFlag = zeroFlag
        self.carryFlag = carryFlag
        
        self.pc += 0x1
        return 6
    
    def IllegalAbsoluteY_DCP(self):
        operand1: UInt8 = self.readByte(self.pc + 0x1)
        operand2: UInt8 = self.readByte(self.pc + 0x2)
        fullAddress: UInt16 = self.combineTwoBytesToOneAddress(operand2, operand1)
        effectiveAddress: UInt16 = fullAddress + self.YRegister.getWriteableInt()
        valueFromMemory: UInt8 = self.readByte(effectiveAddress)
        
        self.logInstruction(self.readByte(self.pc).getHex(), "DCP", operand1.getHex(), operand2=operand2.getHex(), instructionParameter=f"${fullAddress.getHex()},Y @ {effectiveAddress.getHex()} = {valueFromMemory.getHex()}", isIllegal=True)        
        
        valueFromMemory -= 1
        self.RAM.writeAddress(effectiveAddress, valueFromMemory.getWriteableInt())
        
        compareResult, negativeFlag, zeroFlag, carryFlag = self.compareValues(self.accumulatorRegister, valueFromMemory)
        self.negativeFlag = negativeFlag
        self.zeroFlag = zeroFlag
        self.carryFlag = carryFlag
        
        self.pc += 0x2
        return 7
    
    def IllegalAbsoluteX_DCP(self):
        operand1: UInt8 = self.readByte(self.pc + 0x1)
        operand2: UInt8 = self.readByte(self.pc + 0x2)
        fullAddress: UInt16 = self.combineTwoBytesToOneAddress(operand2, operand1)
        effectiveAddress: UInt16 = fullAddress + self.XRegister.getWriteableInt()
        valueFromMemory: UInt8 = self.readByte(effectiveAddress)
        
        self.logInstruction(self.readByte(self.pc).getHex(), "DCP", operand1.getHex(), operand2.getHex(), f"${fullAddress.getHex()},X @ {effectiveAddress.getHex()} = {valueFromMemory.getHex()}", isIllegal=True)        
        
        valueFromMemory -= 1
        self.RAM.writeAddress(effectiveAddress, valueFromMemory.getWriteableInt())
        
        compareResult, negativeFlag, zeroFlag, carryFlag = self.compareValues(self.accumulatorRegister, valueFromMemory)
        self.negativeFlag = negativeFlag
        self.zeroFlag = zeroFlag
        self.carryFlag = carryFlag
        
        self.pc += 0x2
        return 7
    
    def IllegalIndirectX_ISB(self): # ISC (ISB, INS) | Nestest likes ISB i guess
        operand: UInt8 = self.readByte(self.pc + 0x1)
        zeropageAddress: UInt8 = operand + self.XRegister
        lowAddressByte: UInt8 = self.readByte(zeropageAddress)
        highAddressByte: UInt8 = self.readByte(zeropageAddress + 0x1)
        fullAddress: UInt16 = self.combineTwoBytesToOneAddress(highAddressByte, lowAddressByte)
        memoryBefore: UInt8 = self.readByte(fullAddress)
        
        self.logInstruction(self.readByte(self.pc).getHex(), "ISB", operand.getHex(), instructionParameter=f"(${operand.getHex()},X) @ {(zeropageAddress).getHex()} = {fullAddress.getHex()} = {memoryBefore.getHex()}", isIllegal=True)
        
        memoryBefore += 1
        self.RAM.writeAddress(fullAddress, memoryBefore.getWriteableInt())
        
        accumulatorRegister, negativeFlag, zeroFlag, overflowFlag, carryFlag = self.SBC(self.accumulatorRegister, memoryBefore, self.carryFlag)
        
        self.accumulatorRegister = accumulatorRegister
        self.negativeFlag = negativeFlag
        self.zeroFlag = zeroFlag
        self.overflowFlag = overflowFlag
        self.carryFlag = carryFlag
        
        self.pc += 0x1
        return 8
    
    def IllegalZeropageISB(self):
        operand: UInt8 = self.readByte(self.pc + 0x1)
        operandValue: UInt8 = self.readByte(operand)
        
        self.logInstruction(self.readByte(self.pc).getHex(), "ISB", operand.getHex(), instructionParameter=f"${operand.getHex()} = {operandValue.getHex()}", isIllegal=True)        
        
        operandValue += 1
        self.RAM.writeAddress(operand, operandValue.getWriteableInt())
        
        accumulatorRegister, negativeFlag, zeroFlag, overflowFlag, carryFlag = self.SBC(self.accumulatorRegister, operandValue, self.carryFlag)
        
        self.accumulatorRegister = accumulatorRegister
        self.negativeFlag = negativeFlag
        self.zeroFlag = zeroFlag
        self.overflowFlag = overflowFlag
        self.carryFlag = carryFlag
        
        self.pc += 0x1
        return 5
    
    def IllegalAbsoluteISB(self):
        PCL: UInt8 = self.readByte(self.pc + 0x1)
        PCH: UInt8 = self.readByte(self.pc + 0x2)
        address: UInt16 = self.combineTwoBytesToOneAddress(PCH, PCL)
        valueToTest: UInt8 = self.readByte(address)
        
        self.logInstruction(self.readByte(self.pc).getHex(), "ISB", PCL.getHex(), PCH.getHex(), instructionParameter=f"${address.getHex()} = {valueToTest.getHex()}", isIllegal=True)        
        
        valueToTest += 1
        self.RAM.writeAddress(address, valueToTest.getWriteableInt())
        
        accumulatorRegister, negativeFlag, zeroFlag, overflowFlag, carryFlag = self.SBC(self.accumulatorRegister, valueToTest, self.carryFlag)
        
        self.accumulatorRegister = accumulatorRegister
        self.negativeFlag = negativeFlag
        self.zeroFlag = zeroFlag
        self.overflowFlag = overflowFlag
        self.carryFlag = carryFlag
        
        self.pc += 0x2
        return 6
    
    def IllegalIndirectY_ISB(self):
        operand: UInt8 = self.readByte(self.pc + 0x1)
        baseAddressLow: UInt8 = self.readByte(operand)
        baseAddressHigh: UInt8 = self.readByte(operand + 0x1)
        baseAddress: UInt16 = self.combineTwoBytesToOneAddress(baseAddressHigh, baseAddressLow)
        newAddress: UInt8 = baseAddress + self.YRegister.getWriteableInt()
        valueToTest: UInt8 = self.readByte(newAddress)
        
        self.logInstruction(self.readByte(self.pc).getHex(), "ISB", operand.getHex(), instructionParameter=f"(${operand.getHex()}),Y = {baseAddress.getHex()} @ {newAddress.getHex()} = {valueToTest.getHex()}", isIllegal=True)        
        
        valueToTest += 1
        self.RAM.writeAddress(newAddress, valueToTest.getWriteableInt())
        
        accumulatorRegister, negativeFlag, zeroFlag, overflowFlag, carryFlag = self.SBC(self.accumulatorRegister, valueToTest, self.carryFlag)
        
        self.accumulatorRegister = accumulatorRegister
        self.negativeFlag = negativeFlag
        self.zeroFlag = zeroFlag
        self.overflowFlag = overflowFlag
        self.carryFlag = carryFlag
        
        self.pc += 0x1
        return 8
    
    def IllegalZeropageX_ISB(self):
        operand: UInt8 = self.readByte(self.pc + 0x1)
        zeropageAddress: UInt8 = operand + self.XRegister.value 
        value: UInt8 = self.readByte(zeropageAddress)
        
        self.logInstruction(self.readByte(self.pc).getHex(), "ISB", operand.getHex(), instructionParameter=f"${operand.getHex()},X @ {zeropageAddress.getHex()} = {value.getHex()}", isIllegal=True)
        
        value += 1
        self.RAM.writeAddress(zeropageAddress, value.getWriteableInt())
        
        accumulatorRegister, negativeFlag, zeroFlag, overflowFlag, carryFlag = self.SBC(self.accumulatorRegister, value, self.carryFlag)
        
        self.accumulatorRegister = accumulatorRegister
        self.negativeFlag = negativeFlag
        self.zeroFlag = zeroFlag
        self.overflowFlag = overflowFlag
        self.carryFlag = carryFlag
        
        self.pc += 0x1
        return 6
    
    def IllegalAbsoluteY_ISB(self):
        operand1: UInt8 = self.readByte(self.pc + 0x1)
        operand2: UInt8 = self.readByte(self.pc + 0x2)
        fullAddress: UInt16 = self.combineTwoBytesToOneAddress(operand2, operand1)
        effectiveAddress: UInt16 = fullAddress + self.YRegister.getWriteableInt()
        valueFromMemory: UInt8 = self.readByte(effectiveAddress)
        
        self.logInstruction(self.readByte(self.pc).getHex(), "ISB", operand1.getHex(), operand2=operand2.getHex(), instructionParameter=f"${fullAddress.getHex()},Y @ {effectiveAddress.getHex()} = {valueFromMemory.getHex()}", isIllegal=True)        
        
        valueFromMemory += 1
        self.RAM.writeAddress(effectiveAddress, valueFromMemory.getWriteableInt())
        
        accumulatorRegister, negativeFlag, zeroFlag, overflowFlag, carryFlag = self.SBC(self.accumulatorRegister, valueFromMemory, self.carryFlag)
        
        self.accumulatorRegister = accumulatorRegister
        self.negativeFlag = negativeFlag
        self.zeroFlag = zeroFlag
        self.overflowFlag = overflowFlag
        self.carryFlag = carryFlag
        
        self.pc += 0x2
        return 7
    
    def IllegalAbsoluteX_ISB(self):
        operand1: UInt8 = self.readByte(self.pc + 0x1)
        operand2: UInt8 = self.readByte(self.pc + 0x2)
        fullAddress: UInt16 = self.combineTwoBytesToOneAddress(operand2, operand1)
        effectiveAddress: UInt16 = fullAddress + self.XRegister.getWriteableInt()
        valueFromMemory: UInt8 = self.readByte(effectiveAddress)
        
        self.logInstruction(self.readByte(self.pc).getHex(), "ISB", operand1.getHex(), operand2.getHex(), f"${fullAddress.getHex()},X @ {effectiveAddress.getHex()} = {valueFromMemory.getHex()}", isIllegal=True)        
        
        valueFromMemory += 1
        self.RAM.writeAddress(effectiveAddress, valueFromMemory.getWriteableInt())
        
        accumulatorRegister, negativeFlag, zeroFlag, overflowFlag, carryFlag = self.SBC(self.accumulatorRegister, valueFromMemory, self.carryFlag)
        
        self.accumulatorRegister = accumulatorRegister
        self.negativeFlag = negativeFlag
        self.zeroFlag = zeroFlag
        self.overflowFlag = overflowFlag
        self.carryFlag = carryFlag
        
        self.pc += 0x2
        return 7
    
    
    def IllegalIndirectX_SLO(self):
        operand: UInt8 = self.readByte(self.pc + 0x1)
        zeropageAddress: UInt8 = operand + self.XRegister
        lowAddressByte: UInt8 = self.readByte(zeropageAddress)
        highAddressByte: UInt8 = self.readByte(zeropageAddress + 0x1)
        fullAddress: UInt16 = self.combineTwoBytesToOneAddress(highAddressByte, lowAddressByte)
        memoryBefore: UInt8 = self.readByte(fullAddress)
        
        self.logInstruction(self.readByte(self.pc).getHex(), "SLO", operand.getHex(), instructionParameter=f"(${operand.getHex()},X) @ {(zeropageAddress).getHex()} = {fullAddress.getHex()} = {memoryBefore.getHex()}", isIllegal=True)
        
        
        aslResult, carryFlag, negativeFlag, zeroFlag = self.ASL(memoryBefore)
        self.RAM.writeAddress(fullAddress, aslResult.getWriteableInt())        
        self.carryFlag = carryFlag
        
        orResult: Int8 = self.ORA(self.accumulatorRegister, aslResult.getWriteableInt())
        self.accumulatorRegister = orResult
        self.updateNegativeFlag(self.accumulatorRegister)
        self.updateZeroFlag(self.accumulatorRegister)
        
        
        self.pc += 0x1
        return 8
    
    def IllegalZeropageSLO(self):
        operand: UInt8 = self.readByte(self.pc + 0x1)
        operandValue: UInt8 = self.readByte(operand)
        
        self.logInstruction(self.readByte(self.pc).getHex(), "SLO", operand.getHex(), instructionParameter=f"${operand.getHex()} = {operandValue.getHex()}", isIllegal=True)        
        
        aslResult, carryFlag, negativeFlag, zeroFlag = self.ASL(operandValue)
        self.RAM.writeAddress(operand, aslResult.getWriteableInt())        
        self.carryFlag = carryFlag
        
        orResult: Int8 = self.ORA(self.accumulatorRegister, aslResult.getWriteableInt())
        self.accumulatorRegister = orResult
        self.updateNegativeFlag(self.accumulatorRegister)
        self.updateZeroFlag(self.accumulatorRegister)
        
        self.pc += 0x1
        return 5
    
    def IllegalAbsoluteSLO(self):
        PCL: UInt8 = self.readByte(self.pc + 0x1)
        PCH: UInt8 = self.readByte(self.pc + 0x2)
        address: UInt16 = self.combineTwoBytesToOneAddress(PCH, PCL)
        valueToTest: UInt8 = self.readByte(address)
        
        self.logInstruction(self.readByte(self.pc).getHex(), "SLO", PCL.getHex(), PCH.getHex(), instructionParameter=f"${address.getHex()} = {valueToTest.getHex()}", isIllegal=True)        
        
        aslResult, carryFlag, negativeFlag, zeroFlag = self.ASL(valueToTest)
        self.RAM.writeAddress(address, aslResult.getWriteableInt())        
        self.carryFlag = carryFlag
        
        orResult: Int8 = self.ORA(self.accumulatorRegister, aslResult.getWriteableInt())
        self.accumulatorRegister = orResult
        self.updateNegativeFlag(self.accumulatorRegister)
        self.updateZeroFlag(self.accumulatorRegister)
        
        self.pc += 0x2
        return 6
    
    def IllegalIndirectY_SLO(self):
        operand: UInt8 = self.readByte(self.pc + 0x1)
        baseAddressLow: UInt8 = self.readByte(operand)
        baseAddressHigh: UInt8 = self.readByte(operand + 0x1)
        baseAddress: UInt16 = self.combineTwoBytesToOneAddress(baseAddressHigh, baseAddressLow)
        newAddress: UInt8 = baseAddress + self.YRegister.getWriteableInt()
        valueToTest: UInt8 = self.readByte(newAddress)
        
        self.logInstruction(self.readByte(self.pc).getHex(), "SLO", operand.getHex(), instructionParameter=f"(${operand.getHex()}),Y = {baseAddress.getHex()} @ {newAddress.getHex()} = {valueToTest.getHex()}", isIllegal=True)        
        
        aslResult, carryFlag, negativeFlag, zeroFlag = self.ASL(valueToTest)
        self.RAM.writeAddress(newAddress, aslResult.getWriteableInt())        
        self.carryFlag = carryFlag
        
        orResult: Int8 = self.ORA(self.accumulatorRegister, aslResult.getWriteableInt())
        self.accumulatorRegister = orResult
        self.updateNegativeFlag(self.accumulatorRegister)
        self.updateZeroFlag(self.accumulatorRegister)
        
        self.pc += 0x1
        return 8
    
    def IllegalZeropageX_SLO(self):
        operand: UInt8 = self.readByte(self.pc + 0x1)
        zeropageAddress: UInt8 = operand + self.XRegister.value 
        value: UInt8 = self.readByte(zeropageAddress)
        
        self.logInstruction(self.readByte(self.pc).getHex(), "SLO", operand.getHex(), instructionParameter=f"${operand.getHex()},X @ {zeropageAddress.getHex()} = {value.getHex()}", isIllegal=True)
        
        aslResult, carryFlag, negativeFlag, zeroFlag = self.ASL(value)
        self.RAM.writeAddress(zeropageAddress, aslResult.getWriteableInt())        
        self.carryFlag = carryFlag
        
        orResult: Int8 = self.ORA(self.accumulatorRegister, aslResult.getWriteableInt())
        self.accumulatorRegister = orResult
        self.updateNegativeFlag(self.accumulatorRegister)
        self.updateZeroFlag(self.accumulatorRegister)
        
        self.pc += 0x1
        return 6
    
    def IllegalAbsoluteY_SLO(self):
        operand1: UInt8 = self.readByte(self.pc + 0x1)
        operand2: UInt8 = self.readByte(self.pc + 0x2)
        fullAddress: UInt16 = self.combineTwoBytesToOneAddress(operand2, operand1)
        effectiveAddress: UInt16 = fullAddress + self.YRegister.getWriteableInt()
        valueFromMemory: UInt8 = self.readByte(effectiveAddress)
        
        self.logInstruction(self.readByte(self.pc).getHex(), "SLO", operand1.getHex(), operand2=operand2.getHex(), instructionParameter=f"${fullAddress.getHex()},Y @ {effectiveAddress.getHex()} = {valueFromMemory.getHex()}", isIllegal=True)        
        
        aslResult, carryFlag, negativeFlag, zeroFlag = self.ASL(valueFromMemory)
        self.RAM.writeAddress(effectiveAddress, aslResult.getWriteableInt())        
        self.carryFlag = carryFlag
        
        orResult: Int8 = self.ORA(self.accumulatorRegister, aslResult.getWriteableInt())
        self.accumulatorRegister = orResult
        self.updateNegativeFlag(self.accumulatorRegister)
        self.updateZeroFlag(self.accumulatorRegister)
        
        self.pc += 0x2
        return 7
    
    def IllegalAbsoluteX_SLO(self):
        operand1: UInt8 = self.readByte(self.pc + 0x1)
        operand2: UInt8 = self.readByte(self.pc + 0x2)
        fullAddress: UInt16 = self.combineTwoBytesToOneAddress(operand2, operand1)
        effectiveAddress: UInt16 = fullAddress + self.XRegister.getWriteableInt()
        valueFromMemory: UInt8 = self.readByte(effectiveAddress)
        
        self.logInstruction(self.readByte(self.pc).getHex(), "SLO", operand1.getHex(), operand2.getHex(), f"${fullAddress.getHex()},X @ {effectiveAddress.getHex()} = {valueFromMemory.getHex()}", isIllegal=True)        
        
        aslResult, carryFlag, negativeFlag, zeroFlag = self.ASL(valueFromMemory)
        self.RAM.writeAddress(effectiveAddress, aslResult.getWriteableInt())        
        self.carryFlag = carryFlag
        
        orResult: Int8 = self.ORA(self.accumulatorRegister, aslResult.getWriteableInt())
        self.accumulatorRegister = orResult
        self.updateNegativeFlag(self.accumulatorRegister)
        self.updateZeroFlag(self.accumulatorRegister)
        
        self.pc += 0x2
        return 7
    
    
    def IllegalIndirectX_RLA(self):
        operand: UInt8 = self.readByte(self.pc + 0x1)
        zeropageAddress: UInt8 = operand + self.XRegister
        lowAddressByte: UInt8 = self.readByte(zeropageAddress)
        highAddressByte: UInt8 = self.readByte(zeropageAddress + 0x1)
        fullAddress: UInt16 = self.combineTwoBytesToOneAddress(highAddressByte, lowAddressByte)
        memoryBefore: UInt8 = self.readByte(fullAddress)
        
        self.logInstruction(self.readByte(self.pc).getHex(), "RLA", operand.getHex(), instructionParameter=f"(${operand.getHex()},X) @ {(zeropageAddress).getHex()} = {fullAddress.getHex()} = {memoryBefore.getHex()}", isIllegal=True)
        
        
        rolResult, carryFlag, negativeFlag, zeroFlag = self.ROL(memoryBefore, self.carryFlag)
        self.RAM.writeAddress(fullAddress, rolResult.getWriteableInt())       
        self.carryFlag = carryFlag
        
        andResult: Int8 = self.AND_Values(self.accumulatorRegister, rolResult.getWriteableInt())
        self.accumulatorRegister = andResult
        self.updateNegativeFlag(self.accumulatorRegister)
        self.updateZeroFlag(self.accumulatorRegister)
        
        
        self.pc += 0x1
        return 8
    
    def IllegalZeropageRLA(self):
        operand: UInt8 = self.readByte(self.pc + 0x1)
        operandValue: UInt8 = self.readByte(operand)
        
        self.logInstruction(self.readByte(self.pc).getHex(), "RLA", operand.getHex(), instructionParameter=f"${operand.getHex()} = {operandValue.getHex()}", isIllegal=True)        
        
        rolResult, carryFlag, negativeFlag, zeroFlag = self.ROL(operandValue, self.carryFlag)
        self.RAM.writeAddress(operand, rolResult.getWriteableInt())       
        self.carryFlag = carryFlag
        
        andResult: Int8 = self.AND_Values(self.accumulatorRegister, rolResult.getWriteableInt())
        self.accumulatorRegister = andResult
        self.updateNegativeFlag(self.accumulatorRegister)
        self.updateZeroFlag(self.accumulatorRegister)
        
        self.pc += 0x1
        return 5
    
    def IllegalAbsoluteRLA(self):
        PCL: UInt8 = self.readByte(self.pc + 0x1)
        PCH: UInt8 = self.readByte(self.pc + 0x2)
        address: UInt16 = self.combineTwoBytesToOneAddress(PCH, PCL)
        valueToTest: UInt8 = self.readByte(address)
        
        self.logInstruction(self.readByte(self.pc).getHex(), "RLA", PCL.getHex(), PCH.getHex(), instructionParameter=f"${address.getHex()} = {valueToTest.getHex()}", isIllegal=True)        
        
        rolResult, carryFlag, negativeFlag, zeroFlag = self.ROL(valueToTest, self.carryFlag)
        self.RAM.writeAddress(address, rolResult.getWriteableInt())       
        self.carryFlag = carryFlag
        
        andResult: Int8 = self.AND_Values(self.accumulatorRegister, rolResult.getWriteableInt())
        self.accumulatorRegister = andResult
        self.updateNegativeFlag(self.accumulatorRegister)
        self.updateZeroFlag(self.accumulatorRegister)
        
        self.pc += 0x2
        return 6
    
    def IllegalIndirectY_RLA(self):
        operand: UInt8 = self.readByte(self.pc + 0x1)
        baseAddressLow: UInt8 = self.readByte(operand)
        baseAddressHigh: UInt8 = self.readByte(operand + 0x1)
        baseAddress: UInt16 = self.combineTwoBytesToOneAddress(baseAddressHigh, baseAddressLow)
        newAddress: UInt8 = baseAddress + self.YRegister.getWriteableInt()
        valueToTest: UInt8 = self.readByte(newAddress)
        
        self.logInstruction(self.readByte(self.pc).getHex(), "RLA", operand.getHex(), instructionParameter=f"(${operand.getHex()}),Y = {baseAddress.getHex()} @ {newAddress.getHex()} = {valueToTest.getHex()}", isIllegal=True)        
        
        rolResult, carryFlag, negativeFlag, zeroFlag = self.ROL(valueToTest, self.carryFlag)
        self.RAM.writeAddress(newAddress, rolResult.getWriteableInt())       
        self.carryFlag = carryFlag
        
        andResult: Int8 = self.AND_Values(self.accumulatorRegister, rolResult.getWriteableInt())
        self.accumulatorRegister = andResult
        self.updateNegativeFlag(self.accumulatorRegister)
        self.updateZeroFlag(self.accumulatorRegister)
        
        self.pc += 0x1
        return 8
    
    def IllegalZeropageX_RLA(self):
        operand: UInt8 = self.readByte(self.pc + 0x1)
        zeropageAddress: UInt8 = operand + self.XRegister.value 
        value: UInt8 = self.readByte(zeropageAddress)
        
        self.logInstruction(self.readByte(self.pc).getHex(), "RLA", operand.getHex(), instructionParameter=f"${operand.getHex()},X @ {zeropageAddress.getHex()} = {value.getHex()}", isIllegal=True)
        
        rolResult, carryFlag, negativeFlag, zeroFlag = self.ROL(value, self.carryFlag)
        self.RAM.writeAddress(zeropageAddress, rolResult.getWriteableInt())       
        self.carryFlag = carryFlag
        
        andResult: Int8 = self.AND_Values(self.accumulatorRegister, rolResult.getWriteableInt())
        self.accumulatorRegister = andResult
        self.updateNegativeFlag(self.accumulatorRegister)
        self.updateZeroFlag(self.accumulatorRegister)
        
        self.pc += 0x1
        return 6
    
    def IllegalAbsoluteY_RLA(self):
        operand1: UInt8 = self.readByte(self.pc + 0x1)
        operand2: UInt8 = self.readByte(self.pc + 0x2)
        fullAddress: UInt16 = self.combineTwoBytesToOneAddress(operand2, operand1)
        effectiveAddress: UInt16 = fullAddress + self.YRegister.getWriteableInt()
        valueFromMemory: UInt8 = self.readByte(effectiveAddress)
        
        self.logInstruction(self.readByte(self.pc).getHex(), "RLA", operand1.getHex(), operand2=operand2.getHex(), instructionParameter=f"${fullAddress.getHex()},Y @ {effectiveAddress.getHex()} = {valueFromMemory.getHex()}", isIllegal=True)        
        
        rolResult, carryFlag, negativeFlag, zeroFlag = self.ROL(valueFromMemory, self.carryFlag)
        self.RAM.writeAddress(effectiveAddress, rolResult.getWriteableInt())       
        self.carryFlag = carryFlag
        
        andResult: Int8 = self.AND_Values(self.accumulatorRegister, rolResult.getWriteableInt())
        self.accumulatorRegister = andResult
        self.updateNegativeFlag(self.accumulatorRegister)
        self.updateZeroFlag(self.accumulatorRegister)
        
        self.pc += 0x2
        return 7
    
    def IllegalAbsoluteX_RLA(self):
        operand1: UInt8 = self.readByte(self.pc + 0x1)
        operand2: UInt8 = self.readByte(self.pc + 0x2)
        fullAddress: UInt16 = self.combineTwoBytesToOneAddress(operand2, operand1)
        effectiveAddress: UInt16 = fullAddress + self.XRegister.getWriteableInt()
        valueFromMemory: UInt8 = self.readByte(effectiveAddress)
        
        self.logInstruction(self.readByte(self.pc).getHex(), "RLA", operand1.getHex(), operand2.getHex(), f"${fullAddress.getHex()},X @ {effectiveAddress.getHex()} = {valueFromMemory.getHex()}", isIllegal=True)        
        
        rolResult, carryFlag, negativeFlag, zeroFlag = self.ROL(valueFromMemory, self.carryFlag)
        self.RAM.writeAddress(effectiveAddress, rolResult.getWriteableInt())       
        self.carryFlag = carryFlag
        
        andResult: Int8 = self.AND_Values(self.accumulatorRegister, rolResult.getWriteableInt())
        self.accumulatorRegister = andResult
        self.updateNegativeFlag(self.accumulatorRegister)
        self.updateZeroFlag(self.accumulatorRegister)
        
        self.pc += 0x2
        return 7
    
    def IllegalIndirectX_SRE(self):
        operand: UInt8 = self.readByte(self.pc + 0x1)
        zeropageAddress: UInt8 = operand + self.XRegister
        lowAddressByte: UInt8 = self.readByte(zeropageAddress)
        highAddressByte: UInt8 = self.readByte(zeropageAddress + 0x1)
        fullAddress: UInt16 = self.combineTwoBytesToOneAddress(highAddressByte, lowAddressByte)
        memoryBefore: UInt8 = self.readByte(fullAddress)
        
        self.logInstruction(self.readByte(self.pc).getHex(), "SRE", operand.getHex(), instructionParameter=f"(${operand.getHex()},X) @ {(zeropageAddress).getHex()} = {fullAddress.getHex()} = {memoryBefore.getHex()}", isIllegal=True)
        
        
        lsrResult, carryFlag, negativeFlag, zeroFlag = self.LSR(memoryBefore)
        self.RAM.writeAddress(fullAddress, lsrResult.getWriteableInt())
        self.carryFlag = carryFlag
        
        eorResult: Int8 = self.EOR(self.accumulatorRegister, lsrResult.getWriteableInt())
        self.accumulatorRegister = eorResult
        self.updateNegativeFlag(self.accumulatorRegister)
        self.updateZeroFlag(self.accumulatorRegister)
        
        
        self.pc += 0x1
        return 8

    def IllegalZeropageSRE(self):
        operand: UInt8 = self.readByte(self.pc + 0x1)
        operandValue: UInt8 = self.readByte(operand)
        
        self.logInstruction(self.readByte(self.pc).getHex(), "SRE", operand.getHex(), instructionParameter=f"${operand.getHex()} = {operandValue.getHex()}", isIllegal=True)        
        
        lsrResult, carryFlag, negativeFlag, zeroFlag = self.LSR(operandValue)
        self.RAM.writeAddress(operand, lsrResult.getWriteableInt())
        self.carryFlag = carryFlag
        
        eorResult: Int8 = self.EOR(self.accumulatorRegister, lsrResult.getWriteableInt())
        self.accumulatorRegister = eorResult
        self.updateNegativeFlag(self.accumulatorRegister)
        self.updateZeroFlag(self.accumulatorRegister)
        
        self.pc += 0x1
        return 5
    
    def IllegalAbsoluteSRE(self):
        PCL: UInt8 = self.readByte(self.pc + 0x1)
        PCH: UInt8 = self.readByte(self.pc + 0x2)
        address: UInt16 = self.combineTwoBytesToOneAddress(PCH, PCL)
        valueToTest: UInt8 = self.readByte(address)
        
        self.logInstruction(self.readByte(self.pc).getHex(), "SRE", PCL.getHex(), PCH.getHex(), instructionParameter=f"${address.getHex()} = {valueToTest.getHex()}", isIllegal=True)        
        
        lsrResult, carryFlag, negativeFlag, zeroFlag = self.LSR(valueToTest)
        self.RAM.writeAddress(address, lsrResult.getWriteableInt())
        self.carryFlag = carryFlag
        
        eorResult: Int8 = self.EOR(self.accumulatorRegister, lsrResult.getWriteableInt())
        self.accumulatorRegister = eorResult
        self.updateNegativeFlag(self.accumulatorRegister)
        self.updateZeroFlag(self.accumulatorRegister)
        
        self.pc += 0x2
        return 6
    
    def IllegalIndirectY_SRE(self):
        operand: UInt8 = self.readByte(self.pc + 0x1)
        baseAddressLow: UInt8 = self.readByte(operand)
        baseAddressHigh: UInt8 = self.readByte(operand + 0x1)
        baseAddress: UInt16 = self.combineTwoBytesToOneAddress(baseAddressHigh, baseAddressLow)
        newAddress: UInt8 = baseAddress + self.YRegister.getWriteableInt()
        valueToTest: UInt8 = self.readByte(newAddress)
        
        self.logInstruction(self.readByte(self.pc).getHex(), "SRE", operand.getHex(), instructionParameter=f"(${operand.getHex()}),Y = {baseAddress.getHex()} @ {newAddress.getHex()} = {valueToTest.getHex()}", isIllegal=True)        
        
        lsrResult, carryFlag, negativeFlag, zeroFlag = self.LSR(valueToTest)
        self.RAM.writeAddress(newAddress, lsrResult.getWriteableInt())
        self.carryFlag = carryFlag
        
        eorResult: Int8 = self.EOR(self.accumulatorRegister, lsrResult.getWriteableInt())
        self.accumulatorRegister = eorResult
        self.updateNegativeFlag(self.accumulatorRegister)
        self.updateZeroFlag(self.accumulatorRegister)
        
        self.pc += 0x1
        return 8
    
    def IllegalZeropageX_SRE(self):
        operand: UInt8 = self.readByte(self.pc + 0x1)
        zeropageAddress: UInt8 = operand + self.XRegister.value 
        value: UInt8 = self.readByte(zeropageAddress)
        
        self.logInstruction(self.readByte(self.pc).getHex(), "SRE", operand.getHex(), instructionParameter=f"${operand.getHex()},X @ {zeropageAddress.getHex()} = {value.getHex()}", isIllegal=True)
        
        lsrResult, carryFlag, negativeFlag, zeroFlag = self.LSR(value)
        self.RAM.writeAddress(zeropageAddress, lsrResult.getWriteableInt())
        self.carryFlag = carryFlag
        
        eorResult: Int8 = self.EOR(self.accumulatorRegister, lsrResult.getWriteableInt())
        self.accumulatorRegister = eorResult
        self.updateNegativeFlag(self.accumulatorRegister)
        self.updateZeroFlag(self.accumulatorRegister)
        
        self.pc += 0x1
        return 6
    
    def IllegalAbsoluteY_SRE(self):
        operand1: UInt8 = self.readByte(self.pc + 0x1)
        operand2: UInt8 = self.readByte(self.pc + 0x2)
        fullAddress: UInt16 = self.combineTwoBytesToOneAddress(operand2, operand1)
        effectiveAddress: UInt16 = fullAddress + self.YRegister.getWriteableInt()
        valueFromMemory: UInt8 = self.readByte(effectiveAddress)
        
        self.logInstruction(self.readByte(self.pc).getHex(), "SRE", operand1.getHex(), operand2=operand2.getHex(), instructionParameter=f"${fullAddress.getHex()},Y @ {effectiveAddress.getHex()} = {valueFromMemory.getHex()}", isIllegal=True)        
        
        lsrResult, carryFlag, negativeFlag, zeroFlag = self.LSR(valueFromMemory)
        self.RAM.writeAddress(effectiveAddress, lsrResult.getWriteableInt())
        self.carryFlag = carryFlag
        
        eorResult: Int8 = self.EOR(self.accumulatorRegister, lsrResult.getWriteableInt())
        self.accumulatorRegister = eorResult
        self.updateNegativeFlag(self.accumulatorRegister)
        self.updateZeroFlag(self.accumulatorRegister)
        
        self.pc += 0x2
        return 7
    
    def IllegalAbsoluteX_SRE(self):
        operand1: UInt8 = self.readByte(self.pc + 0x1)
        operand2: UInt8 = self.readByte(self.pc + 0x2)
        fullAddress: UInt16 = self.combineTwoBytesToOneAddress(operand2, operand1)
        effectiveAddress: UInt16 = fullAddress + self.XRegister.getWriteableInt()
        valueFromMemory: UInt8 = self.readByte(effectiveAddress)
        
        self.logInstruction(self.readByte(self.pc).getHex(), "SRE", operand1.getHex(), operand2.getHex(), f"${fullAddress.getHex()},X @ {effectiveAddress.getHex()} = {valueFromMemory.getHex()}", isIllegal=True)        
        
        lsrResult, carryFlag, negativeFlag, zeroFlag = self.LSR(valueFromMemory)
        self.RAM.writeAddress(effectiveAddress, lsrResult.getWriteableInt())
        self.carryFlag = carryFlag
        
        eorResult: Int8 = self.EOR(self.accumulatorRegister, lsrResult.getWriteableInt())
        self.accumulatorRegister = eorResult
        self.updateNegativeFlag(self.accumulatorRegister)
        self.updateZeroFlag(self.accumulatorRegister)
        
        self.pc += 0x2
        return 7
    
    
    
    def IllegalIndirectX_RRA(self):
        operand: UInt8 = self.readByte(self.pc + 0x1)
        zeropageAddress: UInt8 = operand + self.XRegister
        lowAddressByte: UInt8 = self.readByte(zeropageAddress)
        highAddressByte: UInt8 = self.readByte(zeropageAddress + 0x1)
        fullAddress: UInt16 = self.combineTwoBytesToOneAddress(highAddressByte, lowAddressByte)
        memoryBefore: UInt8 = self.readByte(fullAddress)
        
        self.logInstruction(self.readByte(self.pc).getHex(), "RRA", operand.getHex(), instructionParameter=f"(${operand.getHex()},X) @ {(zeropageAddress).getHex()} = {fullAddress.getHex()} = {memoryBefore.getHex()}", isIllegal=True)
        
        
        rorResult, carryFlag, negativeFlag, zeroFlag = self.ROR(memoryBefore, self.carryFlag)
        rorResult: UInt8 = UInt8(rorResult.value)
        self.RAM.writeAddress(fullAddress, rorResult.getWriteableInt())
        self.carryFlag = carryFlag
        
        resultInt8, carryFlag, negativeFlag, zeroFlag, overflowFlag = self.ADC(self.accumulatorRegister, rorResult, self.carryFlag)
        self.accumulatorRegister = resultInt8
        self.carryFlag = carryFlag
        self.negativeFlag = negativeFlag
        self.zeroFlag = zeroFlag
        self.overflowFlag = overflowFlag
        
        
        self.pc += 0x1
        return 8

    def IllegalZeropageRRA(self):
        operand: UInt8 = self.readByte(self.pc + 0x1)
        operandValue: UInt8 = self.readByte(operand)
        
        self.logInstruction(self.readByte(self.pc).getHex(), "RRA", operand.getHex(), instructionParameter=f"${operand.getHex()} = {operandValue.getHex()}", isIllegal=True)        
        
        rorResult, carryFlag, negativeFlag, zeroFlag = self.ROR(operandValue, self.carryFlag)
        rorResult: UInt8 = UInt8(rorResult.value)
        self.RAM.writeAddress(operand, rorResult.getWriteableInt())
        self.carryFlag = carryFlag
        
        resultInt8, carryFlag, negativeFlag, zeroFlag, overflowFlag = self.ADC(self.accumulatorRegister, rorResult, self.carryFlag)
        self.accumulatorRegister = resultInt8
        self.carryFlag = carryFlag
        self.negativeFlag = negativeFlag
        self.zeroFlag = zeroFlag
        self.overflowFlag = overflowFlag
        
        self.pc += 0x1
        return 5
    
    def IllegalAbsoluteRRA(self):
        PCL: UInt8 = self.readByte(self.pc + 0x1)
        PCH: UInt8 = self.readByte(self.pc + 0x2)
        address: UInt16 = self.combineTwoBytesToOneAddress(PCH, PCL)
        valueToTest: UInt8 = self.readByte(address)
        
        self.logInstruction(self.readByte(self.pc).getHex(), "RRA", PCL.getHex(), PCH.getHex(), instructionParameter=f"${address.getHex()} = {valueToTest.getHex()}", isIllegal=True)        
        
        rorResult, carryFlag, negativeFlag, zeroFlag = self.ROR(valueToTest, self.carryFlag)
        rorResult: UInt8 = UInt8(rorResult.value)
        self.RAM.writeAddress(address, rorResult.getWriteableInt())
        self.carryFlag = carryFlag
        
        resultInt8, carryFlag, negativeFlag, zeroFlag, overflowFlag = self.ADC(self.accumulatorRegister, rorResult, self.carryFlag)
        self.accumulatorRegister = resultInt8
        self.carryFlag = carryFlag
        self.negativeFlag = negativeFlag
        self.zeroFlag = zeroFlag
        self.overflowFlag = overflowFlag
        
        self.pc += 0x2
        return 6
    
    def IllegalIndirectY_RRA(self):
        operand: UInt8 = self.readByte(self.pc + 0x1)
        baseAddressLow: UInt8 = self.readByte(operand)
        baseAddressHigh: UInt8 = self.readByte(operand + 0x1)
        baseAddress: UInt16 = self.combineTwoBytesToOneAddress(baseAddressHigh, baseAddressLow)
        newAddress: UInt8 = baseAddress + self.YRegister.getWriteableInt()
        valueToTest: UInt8 = self.readByte(newAddress)
        
        self.logInstruction(self.readByte(self.pc).getHex(), "RRA", operand.getHex(), instructionParameter=f"(${operand.getHex()}),Y = {baseAddress.getHex()} @ {newAddress.getHex()} = {valueToTest.getHex()}", isIllegal=True)        
        
        rorResult, carryFlag, negativeFlag, zeroFlag = self.ROR(valueToTest ,self.carryFlag)
        rorResult: UInt8 = UInt8(rorResult.value)
        self.RAM.writeAddress(newAddress, rorResult.getWriteableInt())
        self.carryFlag = carryFlag
        
        resultInt8, carryFlag, negativeFlag, zeroFlag, overflowFlag = self.ADC(self.accumulatorRegister, rorResult, self.carryFlag)
        self.accumulatorRegister = resultInt8
        self.carryFlag = carryFlag
        self.negativeFlag = negativeFlag
        self.zeroFlag = zeroFlag
        self.overflowFlag = overflowFlag
        
        self.pc += 0x1
        return 8
    
    def IllegalZeropageX_RRA(self):
        operand: UInt8 = self.readByte(self.pc + 0x1)
        zeropageAddress: UInt8 = operand + self.XRegister.value 
        value: UInt8 = self.readByte(zeropageAddress)
        
        self.logInstruction(self.readByte(self.pc).getHex(), "RRA", operand.getHex(), instructionParameter=f"${operand.getHex()},X @ {zeropageAddress.getHex()} = {value.getHex()}", isIllegal=True)
        
        rorResult, carryFlag, negativeFlag, zeroFlag = self.ROR(value ,self.carryFlag)
        rorResult: UInt8 = UInt8(rorResult.value)
        self.RAM.writeAddress(zeropageAddress, rorResult.getWriteableInt())
        self.carryFlag = carryFlag
        
        resultInt8, carryFlag, negativeFlag, zeroFlag, overflowFlag = self.ADC(self.accumulatorRegister, rorResult, self.carryFlag)
        self.accumulatorRegister = resultInt8
        self.carryFlag = carryFlag
        self.negativeFlag = negativeFlag
        self.zeroFlag = zeroFlag
        self.overflowFlag = overflowFlag
        
        self.pc += 0x1
        return 6
    
    def IllegalAbsoluteY_RRA(self):
        operand1: UInt8 = self.readByte(self.pc + 0x1)
        operand2: UInt8 = self.readByte(self.pc + 0x2)
        fullAddress: UInt16 = self.combineTwoBytesToOneAddress(operand2, operand1)
        effectiveAddress: UInt16 = fullAddress + self.YRegister.getWriteableInt()
        valueFromMemory: UInt8 = self.readByte(effectiveAddress)
        
        self.logInstruction(self.readByte(self.pc).getHex(), "RRA", operand1.getHex(), operand2=operand2.getHex(), instructionParameter=f"${fullAddress.getHex()},Y @ {effectiveAddress.getHex()} = {valueFromMemory.getHex()}", isIllegal=True)        
        
        rorResult, carryFlag, negativeFlag, zeroFlag = self.ROR(valueFromMemory ,self.carryFlag)
        rorResult: UInt8 = UInt8(rorResult.value)
        self.RAM.writeAddress(effectiveAddress, rorResult.getWriteableInt())
        self.carryFlag = carryFlag
        
        resultInt8, carryFlag, negativeFlag, zeroFlag, overflowFlag = self.ADC(self.accumulatorRegister, rorResult, self.carryFlag)
        self.accumulatorRegister = resultInt8
        self.carryFlag = carryFlag
        self.negativeFlag = negativeFlag
        self.zeroFlag = zeroFlag
        self.overflowFlag = overflowFlag
        
        self.pc += 0x2
        return 7
    
    def IllegalAbsoluteX_RRA(self):
        operand1: UInt8 = self.readByte(self.pc + 0x1)
        operand2: UInt8 = self.readByte(self.pc + 0x2)
        fullAddress: UInt16 = self.combineTwoBytesToOneAddress(operand2, operand1)
        effectiveAddress: UInt16 = fullAddress + self.XRegister.getWriteableInt()
        valueFromMemory: UInt8 = self.readByte(effectiveAddress)
        
        self.logInstruction(self.readByte(self.pc).getHex(), "RRA", operand1.getHex(), operand2.getHex(), f"${fullAddress.getHex()},X @ {effectiveAddress.getHex()} = {valueFromMemory.getHex()}", isIllegal=True)        
        
        rorResult, carryFlag, negativeFlag, zeroFlag = self.ROR(valueFromMemory ,self.carryFlag)
        rorResult: UInt8 = UInt8(rorResult.value)
        self.RAM.writeAddress(effectiveAddress, rorResult.getWriteableInt())
        self.carryFlag = carryFlag
        
        resultInt8, carryFlag, negativeFlag, zeroFlag, overflowFlag = self.ADC(self.accumulatorRegister, rorResult, self.carryFlag)
        self.accumulatorRegister = resultInt8
        self.carryFlag = carryFlag
        self.negativeFlag = negativeFlag
        self.zeroFlag = zeroFlag
        self.overflowFlag = overflowFlag
        
        self.pc += 0x2
        return 7
    
    
    
    def empty(self): return 0
    
    # Decoding!
    
    def decodeInstruction(self, instructionInt8: Int8):
        instruction = instructionInt8.value
        if self.doPrint: print(f"Decoding instruction ~ byte: {instruction}; hex: {hex(instruction)}; program counter: {self.pc.getHex()}")
        
        if instruction in self.opcodes: return self.opcodes[instruction]
        else:
            if self.doPrint: print(f"Opcode unknown! byte: {instruction}; hex: {hex(instruction)}; program counter: {self.pc.getHex()}")
            return -1