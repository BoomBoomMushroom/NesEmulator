from CPU_Ricoh2A03 import Ricoh2A03
from RAM import RAM
from PPU import PPU
from Cartridge import Cartridge

from Screen import Screen, WriteableScreen

#romPath = "SuperMarioBros.nes"
#romPath = "nestest.nes"
#romPath = "NESTestCart.nes"

#with open(romPath, "rb") as f:
#    romDataBinary = f.read()

class NES():
    def __init__(self) -> None:
        self.ram = RAM(self, 1024 * 64) # 64 KB of memory
        
        self.totalCycles = 0
        
        self.screen: WriteableScreen = WriteableScreen((256,256))
        self.cartridge: Cartridge = None
        self.ppu: PPU = PPU(self)
        self.cpu: Ricoh2A03 = Ricoh2A03(self)

    def reset(self):
        self.totalCycles = 0
        self.cpu.reset()
        #self.ppu.reset()

    def loadROM(self, romData):
        self.cpu.loadRom(romData)
        
        self.reset()

    def insertCartridge(self, cartridge: Cartridge):
        self.cartridge = cartridge
        self.cartridge.writePRGToRam(self.ram)
        self.cartridge.writeCHRToVram(self.ppu.vram)
        
        self.reset()

    def step(self):
        cpuResponse = -2
        ppuResponse = 0
        
        ppuResponse = self.ppu.step()
        if self.totalCycles % 3 == 0:
            cpuResponse = self.cpu.step()
        
        self.totalCycles += 1
        return (cpuResponse, ppuResponse, 0)

nestestCartridge = Cartridge("nestest.nes")

screen = Screen()
console = NES()
#console.loadROM(romDataBinary)
console.insertCartridge(nestestCartridge)

#console.cpu.disassembleInstructions(0xc004, 0xc0FF)

isPaused = True
unpausedForOneTick = False
owedOneFrameOfUpdate = False

def askToDumpCPUOutputLog():
    if input("Do you want to dump the CPU logs? (y/n) ") == "y":
        outputLog = console.cpu.outputLog
        print(f"\n{outputLog}\n")


def updateScreenPalettes():
    for i in range(0, 8):
        colors = console.ppu.getPaletteFromIndex(i, True)
        screen.updatePalettes([i], colors)

def updateScreen():
    global owedOneFrameOfUpdate
    if owedOneFrameOfUpdate == False:
        if isPaused: screen.tick()
        if console.ppu.frameComplete == False: return
    else: owedOneFrameOfUpdate = False
    
    screen.drawStatusRegister( console.cpu.negativeFlag, console.cpu.overflowFlag, console.cpu.breakFlag, console.cpu.decimalModeFlag, console.cpu.interruptDisableFlag, console.cpu.zeroFlag, console.cpu.carryFlag )
    screen.drawRegisters(
        f"${console.cpu.pc.getHex()}     ",
        f"${console.cpu.accumulatorRegister.getHex()}  [{console.cpu.accumulatorRegister.getWriteableInt()}]               ",
        f"${console.cpu.XRegister.getHex()}  [{console.cpu.XRegister.getWriteableInt()}]               ",
        f"${console.cpu.YRegister.getHex()}  [{console.cpu.YRegister.getWriteableInt()}]               ",
        f"$00{console.cpu.stackPointer.getHex()}" )
    updateScreenPalettes()
    
    if console.ppu.frameComplete: screen.updateScreen(console.screen)
    console.ppu.frameComplete = False
    screen.tick()

while True:
    if unpausedForOneTick: isPaused = False
    if screen.didQuit: break
    if isPaused:
        updateScreen()
        continue
    
    responses = console.step()
    if responses[0] == -1:
        # CPU ERROR
        with open("cpuOutputLog.txt", "w") as f: f.write(console.cpu.outputLog)
        askToDumpCPUOutputLog()
        break
    elif responses[0] == -2:
        # CPU didnt run. not it's clock cycle
        pass
    elif responses[0] == 0:
        # CPU ran
        if unpausedForOneTick:
            isPaused = True
            unpausedForOneTick = False
            owedOneFrameOfUpdate = True
    
    updateScreen()

if input("Dump CPU RAM? (y/n) ")=="y":
    print(console.ram.dumpRAM())