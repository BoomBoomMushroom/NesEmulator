from __future__ import annotations
import os
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"
import pygame
import sys
import time

# ripped somewhat from https://github.com/Circuitbreaker08/Party-Gaming/blob/main/main.py
class Screen():
    def __init__(self) -> None:
        pygame.init()
        pygame.event.set_allowed([pygame.QUIT, pygame.KEYDOWN, pygame.KEYUP])
        pygame.font.init()
        self.fontSize = 32
        self.font = pygame.font.SysFont("Retro Gaming", 32)
        
        self.isPaused = False
        
        self.queuedDraw = [
            [self.font.render("STATUS:", False, (255,255,255)), (512,self.fontSize*0)],
            [self.font.render("PC:", False, (255,255,255)), (512,self.fontSize*1)],
            [self.font.render("A:", False, (255,255,255)), (512,self.fontSize*2)],
            [self.font.render("X:", False, (255,255,255)), (512,self.fontSize*3)],
            [self.font.render("Y:", False, (255,255,255)), (512,self.fontSize*4)],
            [self.font.render("SP:", False, (255,255,255)), (512,self.fontSize*5)],
            [self.font.render("-", False, (128,128,128)), (512 + self.fontSize*7,0)],
        ]
        
        # Flags text
        flagOnColor: tuple[int, int, int] = (20,255,20)
        flagOffColor: tuple[int, int, int] = (255,20,20)
        
        self.negativeTextOn = [self.font.render("N", False, flagOnColor), (512 + self.fontSize*5,0)]
        self.negativeTextOff = [self.font.render("N", False, flagOffColor), (512 + self.fontSize*5,0)]
        self.negativePrev = None
        
        self.overflowTextOn = [self.font.render("V", False, flagOnColor), (512 + self.fontSize*6,0)]
        self.overflowTextOff = [self.font.render("V", False, flagOffColor), (512 + self.fontSize*6,0)]
        self.overflowPrev = None
        
        self.breakTextOn = [self.font.render("B", False, flagOnColor), (512 + self.fontSize*8,0)]
        self.breakTextOff = [self.font.render("B", False, flagOffColor), (512 + self.fontSize*8,0)]
        self.breakPrev = None
        
        self.decimalTextOn = [self.font.render("D", False, flagOnColor), (512 + self.fontSize*9,0)]
        self.decimalTextOff = [self.font.render("D", False, flagOffColor), (512 + self.fontSize*9,0)]
        self.decimalPrev = None
        
        self.interruptTextOn = [self.font.render("I", False, flagOnColor), (512 + self.fontSize*10,0)]
        self.interruptTextOff = [self.font.render("I", False, flagOffColor), (512 + self.fontSize*10,0)]
        self.interruptPrev = None
        
        self.zeroTextOn = [self.font.render("Z", False, flagOnColor), (512 + self.fontSize*11,0)]
        self.zeroTextOff = [self.font.render("Z", False, flagOffColor), (512 + self.fontSize*11,0)]
        self.zeroPrev = None
        
        self.carryTextOn = [self.font.render("C", False, flagOnColor), (512 + self.fontSize*12,0)]
        self.carryTextOff = [self.font.render("C", False, flagOffColor), (512 + self.fontSize*12,0)]
        self.carryPrev = None
        
        self.backgroundColor = (20, 20, 255)
        
        self.lastFrame = time.time_ns()
        
        # NES resolution (256x224)
        # i'll scale it upto (512 x 512) for now
        self.screen = pygame.display.set_mode((1024, 512))
        self.screen.fill(self.backgroundColor)
        
        # set NES Screen to black
        #pygame.draw.rect(self.screen, (0,0,0), pygame.Rect(0,0, 512, 512))
        
        self.clock = pygame.time.Clock()
    
    def drawStatusRegister(self, n, v, b, d, i, z, c):
        if n != self.negativePrev: self.queuedDraw.append(self.negativeTextOn if n else self.negativeTextOff)
        if v != self.overflowPrev: self.queuedDraw.append(self.overflowTextOn if v else self.overflowTextOff)
        if b != self.breakPrev: self.queuedDraw.append(self.breakTextOn if b else self.breakTextOff)
        if d != self.decimalPrev: self.queuedDraw.append(self.decimalTextOn if d else self.decimalTextOff)
        if i != self.interruptPrev: self.queuedDraw.append(self.interruptTextOn if i else self.interruptTextOff)
        if z != self.zeroPrev: self.queuedDraw.append(self.zeroTextOn if z else self.zeroTextOff)
        if c != self.carryPrev: self.queuedDraw.append(self.carryTextOn if c else self.carryTextOff)
        
        self.negativePrev = n
        self.overflowPrev = v
        self.breakPrev = b
        self.decimalPrev = d
        self.interruptPrev = i
        self.zeroPrev = z
        self.carryPrev = c
    
    def drawRegisters(self, programCounter, accumulator, x, y, stackPointer):
        self.queuedDraw.append( [self.font.render(programCounter, False, (255,255,255)), (512 + self.fontSize*2, self.fontSize*1)] )
        self.queuedDraw.append( [self.font.render(accumulator, False, (255,255,255)), (512 + self.fontSize*2, self.fontSize*2)] )
        self.queuedDraw.append( [self.font.render(x, False, (255,255,255)), (512 + self.fontSize*2, self.fontSize*3)] )
        self.queuedDraw.append( [self.font.render(y, False, (255,255,255)), (512 + self.fontSize*2, self.fontSize*4)] )
        self.queuedDraw.append( [self.font.render(stackPointer, False, (255,255,255)), (512 + self.fontSize*2, self.fontSize*5)] )
    
    
    def ns_to_ss_ms(self, ns):
        # Constants for conversion
        NS_PER_SECOND = 1_000_000_000
        NS_PER_MILLISECOND = 1_000_000
        
        # Calculate seconds and milliseconds
        seconds = ns // NS_PER_SECOND
        milliseconds = (ns % NS_PER_SECOND) // NS_PER_MILLISECOND
        return f"{seconds:02}:{milliseconds:03}"
    
    def updateScreen(self, screenFromNES: WriteableScreen):
        #now = time.time_ns()
        #FPS = round(1/(((now-self.lastFrame)//1_000_000)*0.001))
        #print(f"Time to generate frame: {self.ns_to_ss_ms(now-self.lastFrame)} ~ FPS: {FPS}")
        
        #sys.exit()
        
        # Draw NES screen
        for x in range(len(screenFromNES.pixels)):
            column = screenFromNES.pixels[x]
            for y in range(len(column)):
                pixelColor = column[y]
                self.screen.set_at((x,y), pixelColor)
        
        self.lastFrame = time.time_ns()
    
    def tick(self):
        keys = pygame.key.get_pressed()
        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT:
                self.quit()
                return
            elif event.type == pygame.KEYUP:
                if event.key == pygame.K_SPACE: self.isPaused = self.isPaused != True

        for queued in self.queuedDraw:
            positionedRect: pygame.Rect = queued[0].get_rect(topleft=queued[1])
            pygame.draw.rect(self.screen, self.backgroundColor, positionedRect)
            self.screen.blit(queued[0], queued[1])
        self.queuedDraw = []

        pygame.display.flip()
        self.clock.tick(60) # Come back to this and see if a system needs to replace this (NES works at 60 fps always)

    def quit(self):
        pygame.quit()
        sys.exit()


class WriteableScreen():
    def __init__(self, size: tuple[int,int] = (256,240)) -> None:
        self.pixels: list[ list[ tuple[int,int,int] ] ] = [] # 2D array of colors pixels[x][y] = COLOR
        for x in range(size[0]):
            self.pixels.append([])
            for y in range(size[1]):
                self.pixels[x].append( (0,0,0) ) # just black as the default color

    def setPixel(self, x: int, y: int, color: tuple[int,int,int] = (0,0,0)):
        try:
            self.pixels[x][y] = color
        except IndexError:
            pass


if __name__ == "__main__":
    screen = Screen()
    while True:
        screen.tick()