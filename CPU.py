from Memory import Memory

class CPU():
    def __init__(self, memory: Memory):
        self.pc = 0xFFFC
        self.memory = memory
        
        self.regA = 0
        self.regX = 0
        self.regY = 0
        
        self.stackPointer = 0x00
        
        self.carryFlag = 0
        self.zeroFlag = 0
        self.interruptDisableFlag = 1
        self.decimalFlag = 0
        self.overflowFlag = 0
        self.negativeFlag = 0
    
        # APU Power on stuff
        
        
        self.logsEnabled = False
        self.logs = ""
        self.queuedChanges = []

        self.instructionsExecuted = 0
        
        self.instructions = {
            0x00: self.undefined_instruction,
            0x01: lambda: self.indirectX(2, 6, self.ORA),
            0x02: self.undefined_instruction,
                0x04: lambda: self.zeroPage(2, 3, self.NOP, illegal=True),
            0x05: lambda: self.zeroPage(2, 3, self.ORA),
            0x06: lambda: self.zeroPage(2, 5, self.ASL),
            0x08: lambda: self.implicit(self.PHP),
            0x09: lambda: self.immediate(2, 2, self.ORA),
            0x0A: lambda: self.accumulator(1, 2, self.ASL),
                0x0C: lambda: self.absolute(3, 4, self.NOP, illegal=True),
            0x0D: lambda: self.absolute(3, 4, self.ORA),
            0x0E: lambda: self.absolute(3, 6, self.ASL),
            
            0x10: lambda: self.relative(2, 2, self.BPL),
            0x11: lambda: self.indirectY(2, 5, self.ORA),
            0x12: self.undefined_instruction,
                0x14: lambda: self.indirectX(2, 4, self.NOP),
            0x15: lambda: self.zeroPageX(2, 4, self.ORA),
            0x16: lambda: self.zeroPageX(2, 6, self.ASL),
            0x18: lambda: self.implicit(self.CLC),
            0x19: lambda: self.absoluteY(3, 4, self.ORA),
                0x1A: lambda: self.implicit(self.NOP),
                0x1C: lambda: self.indirectX(3, 4, self.NOP),
            0x1D: lambda: self.absoluteX(3, 4, self.ORA),
            0x1E: lambda: self.absoluteX(3, 7, self.ASL),
            
            0x20: lambda: self.absolute(0, 6, self.JSR),
            0x21: lambda: self.indirectX(2, 6, self.AND),
            0x22: self.undefined_instruction,
            0x24: lambda: self.zeroPage(2, 3, self.BIT),
            0x25: lambda: self.zeroPage(2, 3, self.AND),
            0x26: lambda: self.zeroPage(2, 5, self.ROL),
            0x28: lambda: self.implicit(self.PLP),
            0x29: lambda: self.immediate(2, 2, self.AND),
            0x2A: lambda: self.accumulator(1, 2, self.ROL),
            0x2C: lambda: self.absolute(3, 4, self.BIT),
            0x2D: lambda: self.absolute(3, 4, self.AND),
            0x2E: lambda: self.absolute(3, 6, self.ROL),
                0x2F: lambda: self.absolute(3, 6, self.RLA),
            
            0x30: lambda: self.relative(2, 2, self.BMI),
            0x31: lambda: self.indirectY(2, 5, self.AND),
            0x32: self.undefined_instruction,
                0x34: lambda: self.indirectX(2, 4, self.NOP),
            0x35: lambda: self.zeroPageX(2, 4, self.AND),
            0x36: lambda: self.zeroPageX(2, 6, self.ROL),
            0x38: lambda: self.implicit(self.SEC),
            0x39: lambda: self.absoluteY(3, 4, self.AND),
                0x3A: lambda: self.implicit(self.NOP),
                0x3C: lambda: self.indirectX(3, 4, self.NOP),
            0x3D: lambda: self.absoluteX(3, 4, self.AND),
            0x3E: lambda: self.absoluteX(3, 7, self.ROL),
            
            0x40: lambda: self.implicit(self.RTI),
            0x41: lambda: self.indirectX(2, 6, self.EOR),
            0x42: self.undefined_instruction,
                0x43: lambda: self.indirectX(1, 6, self.SRE),
                0x44: lambda: self.zeroPage(2, 3, self.NOP, illegal=True),
            0x45: lambda: self.zeroPage(2, 3, self.EOR),
            0x46: lambda: self.zeroPage(2, 5, self.LSR),
            0x48: lambda: self.implicit(self.PHA),
            0x49: lambda: self.immediate(2, 2, self.EOR),
            0x4A: lambda: self.accumulator(1, 2, self.LSR),
            0x4C: lambda: self.absolute(0, 3, self.JMP),
            0x4D: lambda: self.absolute(3, 4, self.EOR),
            0x4E: lambda: self.absolute(3, 6, self.LSR),
            
            0x50: lambda: self.relative(2, 2, self.BVC),
            0x51: lambda: self.indirectY(2, 5, self.EOR),
            0x52: self.undefined_instruction,
                0x54: lambda: self.indirectX(2, 4, self.NOP),
            0x55: lambda: self.zeroPageX(2, 4, self.EOR),
            0x56: lambda: self.zeroPageX(2, 6, self.LSR),
            0x58: self.undefined_instruction,
            0x59: lambda: self.absoluteY(3, 4, self.EOR),
                0x5A: lambda: self.implicit(self.NOP),
                0x5C: lambda: self.indirectX(3, 4, self.NOP),
            0x5D: lambda: self.absoluteX(3, 4, self.EOR),
            0x5E: lambda: self.absoluteX(3, 7, self.LSR),
            
            0x60: lambda: self.implicit(self.RTS),
            0x61: lambda: self.indirectX(2, 6, self.ADC),
            0x62: self.undefined_instruction,
                0x64: lambda: self.zeroPage(2, 3, self.NOP, illegal=True),
            0x65: lambda: self.zeroPage(2, 3, self.ADC),
            0x66: lambda: self.zeroPage(2, 5, self.ROR),
            0x68: lambda: self.implicit(self.PLA),
            0x69: lambda: self.immediate(2, 2, self.ADC),
            0x6A: lambda: self.accumulator(1, 2, self.ROR),
            0x6C: lambda: self.indirect(0, 5, self.JMP), # 0 bytes b/c of the JMPing we don't want to offset the JMP address
            0x6D: lambda: self.absolute(3, 4, self.ADC),
            0x6E: lambda: self.absolute(3, 6, self.ROR),
            
            0x70: lambda: self.relative(2, 2, self.BVS),
            0x71: lambda: self.indirectY(2, 5, self.ADC),
            0x72: self.undefined_instruction,
                0x74: lambda: self.indirectX(2, 4, self.NOP),
            0x75: lambda: self.zeroPageX(2, 4, self.ADC),
            0x76: lambda: self.zeroPageX(2, 6, self.ROR),
            0x78: lambda: self.implicit(self.SEI),
            0x79: lambda: self.absoluteY(3, 4, self.ADC),
                0x7A: lambda: self.implicit(self.NOP),
                0x7C: lambda: self.indirectX(3, 4, self.NOP),
            0x7D: lambda: self.absoluteX(3, 4, self.ADC),
            0x7E: lambda: self.absoluteX(3, 7, self.ROR),
            
            0x80: lambda: self.ILLEGAL_OPCODE(2, 1),
            0x81: lambda: self.indirectX(2, 6, self.STA),
            0x82: lambda: self.ILLEGAL_OPCODE(2, 1),
                0x83: lambda: self.indirectX(2, 6, self.SAX),
            0x84: lambda: self.zeroPage(2, 3, self.STY),
            0x85: lambda: self.zeroPage(2, 3, self.STA),
            0x86: lambda: self.zeroPage(2, 3, self.STX),
                0x87: lambda: self.zeroPage(2, 3, self.SAX),
            0x88: lambda: self.implicit(self.DEY),
            0x89: self.undefined_instruction,
            0x8A: lambda: self.implicit(self.TXA),
            0x8C: lambda: self.absolute(3, 4, self.STY),
            0x8D: lambda: self.absolute(3, 4, self.STA),
            0x8E: lambda: self.absolute(3, 4, self.STX),
                0x8F: lambda: self.absolute(3, 4, self.SAX),
            
            0x90: lambda: self.relative(2, 2, self.BCC),
            0x91: lambda: self.indirectY(2, 6, self.STA),
            0x92: self.undefined_instruction,
            0x94: lambda: self.zeroPageX(2, 4, self.STY),
            0x95: lambda: self.zeroPageX(2, 4, self.STA),
            0x96: lambda: self.zeroPageY(2, 4, self.STX),
                0x97: lambda: self.zeroPageY(2, 4, self.SAX),
            0x98: lambda: self.implicit(self.TYA),
            0x99: lambda: self.absoluteY(3, 5, self.STA),
            0x9A: lambda: self.implicit(self.TXS),
            0x9C: self.undefined_instruction,
            0x9D: lambda: self.absoluteX(3, 5, self.STA),
            0x9E: self.undefined_instruction,
            
            0xA0: lambda: self.immediate(2, 2, self.LDY),
            0xA1: lambda: self.indirectX(2, 6, self.LDA),
            0xA2: lambda: self.immediate(2, 2, self.LDX),
            0xA4: lambda: self.zeroPage(2, 3, self.LDY),
                0xA3: lambda: self.indirectX(2, 6, self.LAX),
            0xA5: lambda: self.zeroPage(2, 3, self.LDA),
            0xA6: lambda: self.zeroPage(2, 3, self.LDX),
                0xA7: lambda: self.zeroPage(2, 3, self.LAX),
            0xA8: lambda: self.implicit(self.TAY),
            0xA9: lambda: self.immediate(2, 2, self.LDA),
            0xAA: lambda: self.implicit(self.TAX),
            0xAC: lambda: self.absolute(3, 6, self.LDY),
            0xAD: lambda: self.absolute(3, 4, self.LDA),
            0xAE: lambda: self.absolute(3, 4, self.LDX),
                0xAF: lambda: self.absolute(3, 4, self.LAX),
            
            0xB0: lambda: self.relative(2, 2, self.BCS),
            0xB1: lambda: self.indirectY(2, 5, self.LDA),
            0xB2: self.undefined_instruction,
                0xB3: lambda: self.indirectY(2, 6, self.LAX),
            0xB4: lambda: self.zeroPageX(2, 4, self.LDY),
            0xB5: lambda: self.zeroPageX(2, 4, self.LDA),
            0xB6: lambda: self.zeroPageY(2, 4, self.LDX),
                0xB7: lambda: self.zeroPageY(2, 4, self.LAX),
            0xB8: lambda: self.implicit(self.CLV),
            0xB9: lambda: self.absoluteY(3, 4, self.LDA),
            0xBA: lambda: self.implicit(self.TSX),
            0xBC: lambda: self.absoluteX(3, 4, self.LDY),
            0xBD: lambda: self.absoluteX(3, 4, self.LDA),
            0xBE: lambda: self.absoluteY(3, 4, self.LDX),
                0xBF: lambda: self.absoluteY(3, 4, self.LAX),
            
            0xC0: lambda: self.immediate(2, 2, self.CPY),
            0xC1: lambda: self.indirectX(2, 6, self.CMP),
            0xC2: self.undefined_instruction,
                0xC3: lambda: self.indirectX(2, 8, self.DCP),
            0xC4: lambda: self.zeroPage(2, 3, self.CPY),
            0xC5: lambda: self.zeroPage(2, 3, self.CMP),
            0xC6: lambda: self.zeroPage(2, 5, self.DEC),
            0xC8: lambda: self.implicit(self.INY),
            0xC9: lambda: self.immediate(2, 2, self.CMP),
            0xCA: lambda: self.implicit(self.DEX),
            0xCC: lambda: self.absolute(3, 4, self.CPY),
            0xCD: lambda: self.absolute(3, 4, self.CMP),
            0xCE: lambda: self.absolute(3, 6, self.DEC),
            
            0xD0: lambda: self.relative(2, 2, self.BNE),
            0xD1: lambda: self.indirectY(2, 5, self.CMP),
            0xD2: self.undefined_instruction,
                0xD4: lambda: self.indirectX(2, 4, self.NOP),
            0xD5: lambda: self.zeroPageX(2, 4, self.CMP),
            0xD6: lambda: self.zeroPageX(2, 6, self.DEC),
            0xD8: lambda: self.implicit(self.CLD),
            0xD9: lambda: self.absoluteY(3, 4, self.CMP),
                0xDA: lambda: self.implicit(self.NOP),
                0xDC: lambda: self.indirectX(3, 4, self.NOP),
            0xDD: lambda: self.absoluteX(3, 4, self.CMP),
            0xDE: lambda: self.absoluteX(3, 7, self.DEC),
            
            0xE0: lambda: self.immediate(2, 2, self.CPX),
            0xE1: lambda: self.indirectX(2, 6, self.SBC),
            0xE2: self.undefined_instruction,
            0xE4: lambda: self.zeroPage(2, 3, self.CPX),
            0xE5: lambda: self.zeroPage(2, 3, self.SBC),
            0xE6: lambda: self.zeroPage(2, 5, self.INC),
            0xE8: lambda: self.implicit(self.INX),
            0xE9: lambda: self.immediate(2, 2, self.SBC),
            0xEA: lambda: self.implicit(self.NOP),
            0xEC: lambda: self.absolute(3, 4, self.CPX),
                0xEB: lambda: self.immediate(2, 2, self.SBC), # Same as 0xE9
            0xED: lambda: self.absolute(3, 4, self.SBC),
            0xEE: lambda: self.absolute(3, 6, self.INC),
            
            0xF0: lambda: self.relative(2, 2, self.BEQ),
            0xF1: lambda: self.indirectY(2, 5, self.SBC),
            0xF2: self.undefined_instruction,
                0xF4: lambda: self.indirectX(2, 4, self.NOP),
            0xF5: lambda: self.zeroPageX(2, 4, self.SBC),
            0xF6: lambda: self.zeroPageX(2, 6, self.INC),
            0xF8: lambda: self.implicit(self.SED),
            0xF9: lambda: self.absoluteY(3, 4, self.SBC),
                0xFA: lambda: self.implicit(self.NOP),
                0xFC: lambda: self.indirectX(3, 4, self.NOP),
            0xFD: lambda: self.absoluteX(3, 4, self.SBC),
            0xFE: lambda: self.absoluteX(3, 7, self.INC),
        }
    
    def reset(self):
        # RESET VECTOR
        lowByte = self.memory.read(0xFFFC)
        highByte = self.memory.read(0xFFFD)
        self.pc = (highByte << 8) | lowByte
        
        #self.pc = 0xFFFC
        self.stackPointer = (self.stackPointer - 3) % 0x100
        self.interruptDisableFlag = 1
    
        # APU reset stuff
        
    
    def tick(self):
        self.memory.dumpMemory()
        self.handleQueuedChanges()
        
        #self.executeInstruction()

        #"""
        try:
            self.executeInstruction()
        except Exception as e:
            if self.logsEnabled:
                with open("logs.txt", "w") as f:
                    f.write(self.logs)
                    f.close()
                    exit()
        #"""

    def handleQueuedChanges(self):
        """
        {
            "clocksUntil": int, # do change on 0, -1 each clock cycle
            "varToChange": str,
            "newValue": any value,
        }
        """
        i = 0
        while i < len(self.queuedChanges):
            self.queuedChanges[i]["clocksUntil"] -= 1
            if self.queuedChanges[i]["clocksUntil"] > 0:
                i += 1
                continue
            
            if self.queuedChanges[i]["varToChange"] == "InterruptFlag":
                self.interruptDisableFlag = self.queuedChanges[i]["newValue"]
            
            
            self.queuedChanges.pop(i)
            #i -= 1
            #i += 1

    def executeInstruction(self):
        # returns bytes, clock cycles
        opcode = self.memory.read(self.pc)
        instruction = self.instructions[opcode]
        
        #print(f"{hex(self.pc)}: {hex(opcode)}")

        bytesRead, clockCycles = instruction()
        self.instructionsExecuted += 1

        self.pc += bytesRead
        

    # Stack
    def pushStack(self, value: int):
        # On a push we read then decrement it
        
        # add 0x0100 b/c the stack is from 0x0100 to 0x01ff, and the stack pointer is from 0x00 to 0xff
        stackAddress = self.stackPointer + 0x0100
        self.memory.write(stackAddress, value)
        
        # Clamp between 0x00 and 0xff
        self.stackPointer -= 1
        self.stackPointer %= 0x100

    def pullStack(self):
        # On a pull we increment it first then read
        
        # Clamp between 0x00 and 0xff
        self.stackPointer += 1
        self.stackPointer %= 0x100
        
        stackAddress = self.stackPointer + 0x0100
        value = self.memory.read(stackAddress)
        
        return value

    def updateZeroFlag(self, value):
        self.zeroFlag = 1 if (value == 0) else 0
    
    def updateOverflowFlag(self, value):
        self.overflowFlag = (value & 0b01000000) >> 6 # get bit 6 (zero indexed)
    
    def updateNegativeFlag(self, value):
        self.negativeFlag = (value & 0b10000000) >> 7 # get bit 7 (zero indexed)

    def logInstruction(self, addressing, instruction, bytesRead, illegal=False):
        if self.logsEnabled == False: return False
        
        bytesReadString = [ hex(b).split('0x')[1].zfill(2) for b in bytesRead ]
        while len(bytesReadString) < 3: bytesReadString.append("  ")
        
        flagByte = (0b00100000 | 
                    (self.negativeFlag << 7) | 
                    (self.overflowFlag << 6) | 
                    # bit 5 is always a 1                       
                    #(self.breakFlag << 4) | # Doesn't exist
                    (self.decimalFlag << 3) | 
                    (self.interruptDisableFlag << 2) | 
                    (self.zeroFlag << 1) | 
                    (self.carryFlag << 0) )
        
        isIllegal = "*" if illegal else " "
        line = f"{hex(self.pc).split('0x')[1].zfill(4)}  {' '.join(bytesReadString)} {isIllegal}{instruction} {addressing}"
        line += " " * (48 - len(line)) # Make sure the line is 48 characters long before adding registers
        line += f"A:{hex(self.regA).split('0x')[1].zfill(2)} X:{hex(self.regX).split('0x')[1].zfill(2)} Y:{hex(self.regY).split('0x')[1].zfill(2)}"
        line += f" P:{hex(flagByte).split('0x')[1].zfill(2)} SP:{hex(self.stackPointer).split('0x')[1].zfill(2)} PPU:  0, 21 CYC:7"
        
        self.logs += line + "\n"
        print(line)

    # Instructions
    # Addressing modes. (Comment taken from my old NES CPU) 
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
    
    
    def undefined_instruction(self):
        print("UNDEFINED INSTRUCTION!!!")
        print(f"{hex(self.pc)}: {hex(self.memory.read(self.pc))}")
        exit()

    def implicit(self, func):
        self.logInstruction("", func.__name__, [self.memory.read(self.pc)])
        
        return func()

    def accumulator(self, bytesToRead, cycles, func):
        self.logInstruction("A", func.__name__, [self.memory.read(self.pc)])
        
        func(self.regA, addr="A")
        return (bytesToRead, cycles)

    def immediate(self, bytesToRead, cycles, func):
        value = self.memory.read(self.pc + 1)
        
        self.logInstruction(f"#${hex(value).split('0x')[1].zfill(2)}", func.__name__, [self.memory.read(self.pc), value])
        
        func(value)
        
        return (bytesToRead, cycles)
    
    def absolute(self, bytesToRead, cycles, func):
        addressLow = self.memory.read(self.pc+1)
        addressHigh = self.memory.read(self.pc+2) 
        valueAddress = (addressHigh << 8) | addressLow
        value = self.memory.read(valueAddress)
        
        if self.logsEnabled:
            equalString = f"= {hex(value).split('0x')[1].zfill(2)}"
            if func.__name__ in ["JMP", "JSR"]:
                equalString = ""
            self.logInstruction(f"${hex(valueAddress).split('0x')[1].zfill(4)} {equalString}", func.__name__, [self.memory.read(self.pc), addressLow, addressHigh])
        
        func(value, addr=valueAddress)
    
        return (bytesToRead, cycles)
    
    def absoluteX(self, bytesToRead, cycles, func):
        lowByte = self.memory.read(self.pc+1)
        highByte = self.memory.read(self.pc+2)
        
        address = (highByte << 8) | lowByte
        valueAddress = (address + self.regX ) % 0x10000
        value = self.memory.read(valueAddress)
        
        self.logInstruction(f"${hex(address).split('0x')[1].zfill(4)},X @ {hex(valueAddress).split('0x')[1].zfill(4)} = {hex(value).split('0x')[1].zfill(2)}", func.__name__, [self.memory.read(self.pc), lowByte, highByte])
        
        func(value, addr=valueAddress)
    
        return (bytesToRead, cycles)
    
    def absoluteY(self, bytesToRead, cycles, func):
        lowByte = self.memory.read(self.pc + 1)
        highByte = self.memory.read(self.pc + 2)
        
        address = ((highByte << 8) | lowByte)
        valueAddress = (address + self.regY) % 0x10000
        
        value = self.memory.read(valueAddress)
        
        self.logInstruction(f"${hex(address).split('0x')[1].zfill(4)},Y @ {hex(valueAddress).split('0x')[1].zfill(4)} = {hex(value).split('0x')[1].zfill(2)}", func.__name__, [self.memory.read(self.pc), lowByte, highByte])
        
        func(value, addr=valueAddress)
    
        return (bytesToRead, cycles)
    
    def relative(self, bytesToRead, cycles, func):
        offset = self.memory.read(self.pc + 1) # to make signed subtract 128 * 2 if the highest power bit is on
        if (offset >> 7 == 1): offset -= 128 * 2
        
        self.logInstruction(f"${hex(offset + self.pc + 2).split('0x')[1].zfill(4)}", func.__name__, [self.memory.read(self.pc), self.memory.read(self.pc + 1)])
        
        addBytes, addCycles = func(offset)
        if addBytes == None: addBytes = 0
        if addCycles == None: addCycles = 0
        
        return (bytesToRead + addBytes, cycles + addCycles)

    def zeroPage(self, bytesToRead, cycles, func, illegal=False):
        # high byte is assumed to be 0x00, so the low byte (next byte) is the entire address
        address = self.memory.read(self.pc + 1)
        valueAtAddress = self.memory.read(address)
        
        self.logInstruction(f"${hex(address).split('0x')[1].zfill(2)} = {hex(valueAtAddress).split('0x')[1].zfill(2)}", func.__name__, [self.memory.read(self.pc), address], illegal=illegal)
        
        func(valueAtAddress, address)
        #func(address)
        
        return (bytesToRead, cycles)

    def zeroPageX(self, bytesToRead, cycles, func):
        # Zero Page but add X to the address
        zpOperand = self.memory.read(self.pc + 1)
        address = (zpOperand + self.regX) % 0x100 # Zero page, make sure the address stays in 1 byte
        valueAtAddress = self.memory.read(address)
        
        self.logInstruction(f"${hex(zpOperand).split('0x')[1].zfill(2)},X @ {hex(address).split('0x')[1].zfill(2)} = {hex(valueAtAddress).split('0x')[1].zfill(2)}", func.__name__, [self.memory.read(self.pc), zpOperand])
        
        func(valueAtAddress, address)
        
        return (bytesToRead, cycles)

    def zeroPageY(self, bytesToRead, cycles, func):
        # Zero Page but add Y to the address
        zpOperand = self.memory.read(self.pc + 1)
        address = (zpOperand + self.regY) % 0x100 # Zero page, make sure the address stays in 1 byte
        valueAtAddress = self.memory.read(address)
        
        self.logInstruction(f"${hex(zpOperand).split('0x')[1].zfill(2)},Y @ {hex(address).split('0x')[1].zfill(2)} = {hex(valueAtAddress).split('0x')[1].zfill(2)}", func.__name__, [self.memory.read(self.pc), zpOperand])
        
        func(valueAtAddress, address)
        
        return (bytesToRead, cycles)

    def indirect(self, bytesToRead, cycles, func): # This is only used for JMP so I can bs the structure!
        realLowByte = self.memory.read(self.pc+1)
        realHighByte = self.memory.read(self.pc+2)
        realAddressPointer = (realHighByte << 8) | realLowByte
     
        jumpAddressLowByte = self.memory.read(realAddressPointer)
        endOfPageBugOffset = -0x100 if (realAddressPointer & 0xFF) == 0xFF else 0 # -255 (one byte) and that one already being added which turns 0x3100 to 0x3000 instead

        jumpAddressHighByte = self.memory.read(realAddressPointer + 1 + endOfPageBugOffset) << 8
        jumpAddress = jumpAddressHighByte | jumpAddressLowByte
        
        self.logInstruction(f"(${hex(realAddressPointer).split('0x')[1].zfill(4)}) = {hex(jumpAddress).split('0x')[1].zfill(4)}", func.__name__, [self.memory.read(self.pc), realLowByte, realHighByte])
        
        func(None, addr=jumpAddress)
    
        return (bytesToRead, cycles)

    def indirectX(self, bytesToRead, cycles, func):
        # Zero page + X
        addressLocationInMemory = self.memory.read(self.pc + 1) + self.regX
        # Wrap around the zero page if we go out of it
        addressBottomByte = self.memory.read(addressLocationInMemory % 0x100) #0x00FF
        addressTopByte = self.memory.read((addressLocationInMemory + 1) % 0x100) #0xFF00
        address = (addressTopByte << 8) | addressBottomByte
        
        valueAtAddress = self.memory.read(address)

        afterMnemonic = f"(${hex(self.memory.read(self.pc+1)).split('0x')[1].zfill(2)},X) @ {hex(addressLocationInMemory % 0x100).split('0x')[1].zfill(2)}"
        afterMnemonic += f" = {hex(address).split('0x')[1].zfill(4)} = {hex(valueAtAddress).split('0x')[1].zfill(2)}"
        self.logInstruction(afterMnemonic, func.__name__, [self.memory.read(self.pc), self.memory.read(self.pc+1)])

        func(valueAtAddress, address)
        
        return (bytesToRead, cycles)

    def indirectY(self, bytesToRead, cycles, func):
        # Zero page, then add Y to the extracted address
        addressLocationInMemory = self.memory.read(self.pc + 1)
        # Wrap around the zero page if we go out of it
        addressBottomByte = self.memory.read((addressLocationInMemory + 0) % 0x100) #0x00FF
        addressTopByte = self.memory.read((addressLocationInMemory + 1) % 0x100) #0xFF00
        address = (addressTopByte << 8) | addressBottomByte
        addressWithY = (address + self.regY) % 0x10000 # Make sure it is only 2 bytes
        
        valueAtAddress = self.memory.read(addressWithY)

        afterMnemonic = f"(${hex(self.memory.read(self.pc+1)).split('0x')[1].zfill(2)}),Y = {hex(address).split('0x')[1].zfill(4)}"
        afterMnemonic += f" @ {hex(addressWithY).split('0x')[1].zfill(4)} = {hex(valueAtAddress).split('0x')[1].zfill(2)}"
        self.logInstruction(afterMnemonic, func.__name__, [self.memory.read(self.pc), self.memory.read(self.pc+1)])
        
        func(valueAtAddress, address)
        
        return (bytesToRead, cycles)

    def SEI(self):
        self.queuedChanges.append({
            "clocksUntil": 1,
            "varToChange": "InterruptFlag",
            "newValue": 1
        })
        
        return (1, 2)
    
    def SEC(self):
        self.carryFlag = 1
        return (1, 2)
    
    def SED(self):
        self.decimalFlag = 1
        return (1, 2)
    
    def CLD(self):
        self.decimalFlag = 0
        return (1, 2)
    
    def CLC(self):
        self.carryFlag = 0
        return (1, 2)
    
    def CLV(self):
        self.overflowFlag = 0
        return (1, 2)
    
    def LDX(self, value, addr=None):
        self.regX = value
        self.updateZeroFlag(value)
        self.updateNegativeFlag(value)
    
    def LDY(self, value, addr=None):
        self.regY = value
        self.updateZeroFlag(value)
        self.updateNegativeFlag(value)
    
    def LDA(self, value, addr=None):
        self.regA = value
        self.updateZeroFlag(value)
        self.updateNegativeFlag(value)

    def STX(self, value, addr=None):
        if addr != None: value = addr # Do this b/c zero page STX uses the address after it as the place to store
        self.memory.write(value, self.regX)
    
    def STY(self, value, addr=None):
        if addr != None: value = addr # Do this b/c zero page STY uses the address after it as the place to store
        self.memory.write(value, self.regY)

    def STA(self, value, addr=None):
        if addr != None: value = addr # Do this b/c zero page STA uses the address after it as the place to store
        self.memory.write(value, self.regA)

    def TXS(self):
        self.stackPointer = self.regX
        return (1, 2)

    def JMP(self, value, addr=None):
        self.pc = addr

    def JSR(self, value, addr=None):
        addressToWrite = self.pc + 2
        
        addressTopByte = (addressToWrite & 0xff00) >> 8
        addressBottomByte = (addressToWrite & 0x00ff) >> 0
        
        self.pushStack(addressTopByte)
        self.pushStack(addressBottomByte)
        
        self.pc = addr

    def RTS(self):
        addressBottomByte = self.pullStack() #0x00FF
        addressTopByte = self.pullStack() #0xFF00
        address = (addressTopByte << 8) | addressBottomByte
        
        self.pc = address
        return (1, 6)

    def RTI(self):
        # Pull Flags
        flagByte = self.pullStack()
        self.negativeFlag = (flagByte & 0b10000000) >> 7
        self.overflowFlag = (flagByte & 0b01000000) >> 6
        self.decimalFlag = (flagByte & 0b00001000) >> 3
        self.interruptDisableFlag = (flagByte & 0b00000100) >> 2
        self.zeroFlag = (flagByte & 0b00000010) >> 1
        self.carryFlag = (flagByte & 0b00000001) >> 0
        
        # Pull PC
        addressBottomByte = self.pullStack() #0x00FF
        addressTopByte = self.pullStack() #0xFF00
        address = (addressTopByte << 8) | addressBottomByte
        self.pc = address
        return (0, 6) # set bytes (the first item in the tuple) as 0 so we don't inc our PC and use that instruction immediately 

    """
    def BRK(self):
        # Write the address to stack
        addressToWrite = self.pc + 2
        addressTopByte = (addressToWrite & 0xff00) >> 8
        addressBottomByte = (addressToWrite & 0x00ff) >> 0
        self.pushStack(addressTopByte)
        self.pushStack(addressBottomByte)
        
        # Write Flags to one byte NV11DIZC
        flagByte = (0b00110000 | 
                    (self.negativeFlag << 7) | 
                    (self.overflowFlag << 6) | 
                    (self.decimalFlag << 3) | 
                    (self.interruptDisableFlag << 2) | 
                    (self.zeroFlag << 1) | 
                    self.carryFlag)
  
        self.pushStack(flagByte)
        self.pc = 0xfffe
        
        self.interruptDisableFlag = 1
        
        return (2, 7)
    """

    def BPL(self, offset):
        return self.BranchWithCondition(self.negativeFlag, 0, offset)
    
    def BMI(self, offset):
        return self.BranchWithCondition(self.negativeFlag, 1, offset)

    def BCS(self, offset):
        return self.BranchWithCondition(self.carryFlag, 1, offset)
    
    def BCC(self, offset):
        return self.BranchWithCondition(self.carryFlag, 0, offset)
    
    def BEQ(self, offset):
        return self.BranchWithCondition(self.zeroFlag, 1, offset)

    def BNE(self, offset):
        return self.BranchWithCondition(self.zeroFlag, 0, offset)

    def BVS(self, offset):
        return self.BranchWithCondition(self.overflowFlag, 1, offset)
    
    def BVC(self, offset):
        return self.BranchWithCondition(self.overflowFlag, 0, offset)

    def BranchWithCondition(self, checkValue, branchIfValue, offset):
        if checkValue == branchIfValue: return (offset, 1)
        else: return (0, 0)

    def CPX(self, value, addr=None):
        subtractResult = self.regX - value
        if subtractResult < 0: subtractResult += 128 * 2 # Make it so it is negative in twos complement
        
        self.carryFlag = (self.regX >= value)
        self.zeroFlag = (self.regX == value)
        self.updateNegativeFlag(subtractResult)
    
    def CPY(self, value, addr=None):
        subtractResult = self.regY - value
        if subtractResult < 0: subtractResult += 128 * 2 # Make it so it is negative in twos complement
        
        self.carryFlag = 1 if (self.regY >= value) else 0
        self.zeroFlag = 1 if (self.regY == value) else 0
        self.updateNegativeFlag(subtractResult)

    def CMP(self, value, addr=None):
        subtractResult = self.regA - value
        if subtractResult < 0: subtractResult += 128 * 2 # Make it so it is negative in twos complement
        
        self.carryFlag = 1 if (self.regA >= value) else 0
        self.zeroFlag = 1 if (self.regA == value) else 0
        self.updateNegativeFlag(subtractResult)

    def BIT(self, value, addr=None):
        result = self.regA & value
        
        self.updateZeroFlag(result)
        self.updateOverflowFlag(value)
        self.updateNegativeFlag(value)

    def AND(self, value, addr=None):
        result = self.regA & value
        self.regA = result
        
        self.updateZeroFlag(result)
        self.updateNegativeFlag(result)

    def ORA(self, value, addr=None):
        result = self.regA | value
        self.regA = result
        
        self.updateZeroFlag(result)
        self.updateNegativeFlag(result)
        
    def EOR(self, value, addr=None):
        result = self.regA ^ value
        self.regA = result
        
        self.updateZeroFlag(result)
        self.updateNegativeFlag(result)

    def ADC(self, value, addr=None):
        initRegA = self.regA + 0
        result = self.regA + value + self.carryFlag
        resultFixed = result % 0x100
        self.regA = resultFixed
        
        self.carryFlag = 1 if result > 0xff else 0
        self.updateZeroFlag(resultFixed)
        # The result's sign is different than the value AND reg A meaning "signed overflow (or underflow) occurred." (https://www.nesdev.org/wiki/Instruction_reference#ADC)
        self.overflowFlag = 1 if (result & 0x80 != initRegA & 0x80) and (result & 0x80 != value & 0x80) else 0
        self.updateNegativeFlag(resultFixed)

    def SBC(self, value, addr=None):
        initRegA = self.regA + 0
        
        # A = A - memory - ~C, or equivalently: A = A + ~memory + C
        invertedValue = ~value + 256
        invertedCarry = 0 if self.carryFlag == 1 else 1
        
        #result = self.regA + invertedValue + self.carryFlag
        result = self.regA - value - invertedCarry
        resultFixed = result % 0x100
        self.regA = resultFixed
        
        self.carryFlag = 0 if result < 0x00 else 1 # Same as ~(result < 0x00)
        self.updateZeroFlag(resultFixed)
        # If result's sign is different from A's and the same as memory's, signed overflow (or underflow) occurred
        self.overflowFlag = 1 if (result & 0x80 != initRegA & 0x80) and (result & 0x80 == value & 0x80) else 0
        self.updateNegativeFlag(resultFixed)

    def INY(self):
        newValue = (self.regY + 1) % 0x100 # Clamp to 1 byte range
        self.regY = newValue

        self.updateZeroFlag(newValue)
        self.updateNegativeFlag(newValue)
        
        return (1, 2)
    
    def INX(self):
        newValue = (self.regX + 1) % 0x100 # Clamp to 1 byte range
        self.regX = newValue

        self.updateZeroFlag(newValue)
        self.updateNegativeFlag(newValue)
        
        return (1, 2)
    
    def DEY(self):
        newValue = (self.regY - 1) % 0x100 # Clamp to 1 byte range
        self.regY = newValue

        self.updateZeroFlag(newValue)
        self.updateNegativeFlag(newValue)
        
        return (1, 2)
    
    def DEX(self):
        newValue = (self.regX - 1) % 0x100 # Clamp to 1 byte range
        self.regX = newValue

        self.updateZeroFlag(newValue)
        self.updateNegativeFlag(newValue)
        
        return (1, 2)

    def INC(self, value, addr=None):
        newValue = (self.memory.read(addr) + 1) % 0x100
        self.memory.write(addr, newValue)
        
        self.updateZeroFlag(newValue)
        self.updateNegativeFlag(newValue)

    def DEC(self, value, addr=None):
        newValue = (self.memory.read(addr) - 1) % 0x100
        self.memory.write(addr, newValue)
        
        self.updateZeroFlag(newValue)
        self.updateNegativeFlag(newValue)
        

    def TAY(self):
        self.regY = self.regA
        
        self.updateZeroFlag(self.regY)
        self.updateNegativeFlag(self.regY)
        return (1, 2)
    
    def TAX(self):
        self.regX = self.regA
        
        self.updateZeroFlag(self.regX)
        self.updateNegativeFlag(self.regX)
        return (1, 2)
    
    def TYA(self):
        self.regA = self.regY
        
        self.updateZeroFlag(self.regA)
        self.updateNegativeFlag(self.regA)
        return (1, 2)
    
    def TXA(self):
        self.regA = self.regX
        
        self.updateZeroFlag(self.regA)
        self.updateNegativeFlag(self.regA)
        return (1, 2)

    def TSX(self):
        self.regX = self.stackPointer
        
        self.updateZeroFlag(self.regX)
        self.updateNegativeFlag(self.regX)
        return (1, 2)

    def LSR(self, value, addr=None):
        result = (value >> 1) % 0x100
        
        if addr == "A":
            self.regA = result
        elif addr != None:
            self.memory.write(addr, result)
        
        self.carryFlag = (value & 0b00000001)
        self.updateZeroFlag(result)
        self.updateNegativeFlag(result)

    def ASL(self, value, addr=None):
        result = (value << 1) % 0x100
        
        if addr == "A":
            self.regA = result
        elif addr != None:
            self.memory.write(addr, result)

        self.carryFlag = (value & 0b10000000) >> 7
        self.updateZeroFlag(result)
        self.updateNegativeFlag(result)

    def ROR(self, value, addr=None):
        result = (value >> 1) % 0x100
        result |= (self.carryFlag << 7)

        if addr == "A":
            self.regA = result
        elif addr != None:
            self.memory.write(addr, result)
        
        self.carryFlag = (value & 0b00000001)
        self.updateZeroFlag(result)
        self.updateNegativeFlag(result)
    
    def ROL(self, value, addr=None):
        result = (value << 1) % 0x100
        result |= self.carryFlag # Carry is put into bit 0

        if addr == "A":
            self.regA = result
        elif addr != None:
            self.memory.write(addr, result)
        
        self.carryFlag = (value & 0b10000000) >> 7
        self.updateZeroFlag(result)
        self.updateNegativeFlag(result)

    
    def PHP(self):
        # NV11DIZC
        flagByte = (0b00110000 | 
                    (self.negativeFlag << 7) | 
                    (self.overflowFlag << 6) | 
                    (self.decimalFlag << 3) | 
                    (self.interruptDisableFlag << 2) | 
                    (self.zeroFlag << 1) | 
                    self.carryFlag)
  
        self.pushStack(flagByte)
        
        return (1, 3)
    
    def PLP(self):
        flagByte = self.pullStack()
        self.negativeFlag = (flagByte & 0b10000000) >> 7
        self.overflowFlag = (flagByte & 0b01000000) >> 6
        self.decimalFlag = (flagByte & 0b00001000) >> 3
        
        newInterruptFlag = (flagByte & 0b00000100) >> 2
        self.queuedChanges.append({
            "clocksUntil": 1,
            "varToChange": "InterruptFlag",
            "newValue": newInterruptFlag
        })
        
        self.zeroFlag = (flagByte & 0b00000010) >> 1
        self.carryFlag = (flagByte & 0b00000001) >> 0
        return (1, 4)
    
    def PHA(self):
        self.pushStack(self.regA)
        return (1, 3)

    def PLA(self):
        stackValue = self.pullStack()
        self.regA = stackValue
        
        self.updateZeroFlag(stackValue)
        self.updateNegativeFlag(stackValue)
        return (1, 4)


    def NOP(self, value=None, addr=None):
        return (1, 2)
    
    def ILLEGAL_OPCODE(self, bytesToRead, cycles):
        return (bytesToRead, cycles)
    
    
    def RLA(self, value, addr=None):
        ROL_Value = (value << 1) % 0x100
        ROL_Value |= self.carryFlag
        self.carryFlag = (value & 0b10000000)
        self.memory.write(addr, ROL_Value)
        
        AND_Value = self.regA & ROL_Value
        self.regA = AND_Value
        self.updateZeroFlag(AND_Value)
        self.updateNegativeFlag(AND_Value)
    
    def SRE(self, value, addr=None):
        LSR_Value = (value >> 1) % 0x100
        self.carryFlag = (value & 0b00000001)
        self.memory.write(addr, LSR_Value)
        
        EOR_Value = self.regA ^ LSR_Value
        self.regA = EOR_Value
        self.updateZeroFlag(EOR_Value)
        self.updateNegativeFlag(EOR_Value)
    
    def LAX(self, value, addr=None):
        self.regA = value
        self.regX = value
        
        self.updateZeroFlag(value)
        self.updateNegativeFlag(value)
    
    def SAX(self, value, addr=None):
        value = self.regA & self.regX
        self.memory.write(addr, value)

    def DCP(self, value, addr=None): # DEC + CMP
        # DEC
        DEC_Value = (self.memory.read(addr) - 1) % 0x100
        self.memory.write(addr, DEC_Value)

        # CMP
        subtractResult = self.regA - value
        if subtractResult < 0: subtractResult += 128 * 2 # Make it so it is negative in twos complement
        
        self.carryFlag = (self.regA >= value)
        self.zeroFlag = (self.regA == value)
        self.updateNegativeFlag(subtractResult)