#/usr/bin/env python

#Import Modules
import os, pygame, copy
import math, random
from pygame.locals import *

if not pygame.font : print "Warning, pygame 'font' module disabled!"
if not pygame.mixer: print "Warning, pygame 'sound' module disabled!"

# --------------------------------------------------------
# Clamping a number between min m and max M
# --------------------------------------------------------
def clamp(x,m,M):
    if   x < m : return m
    elif x > M : return M
    return x
    
ENGINE = None # Global GAME variable

# --------------------------------------------------------
# --------------------------------------------------------
class Board:
    def __init__(self,engine,scr,dim=(8,9)):
        self.screen = scr
        self.dim = dim
        self.matrix = [[0 for x in range(dim[0])] for y in range(dim[1])]
        self.colors=[ (100,100,100), (169,15,14), (94,179,20), (40,169,218), (112,0,252), (231,201,27)]
        self.randomize()
        self.tilesize = (32,32)
        self.padding = (5,5)
        r = self.screen.get_rect()
        w = self.tilesize[0]*self.dim[0] + self.padding[0]*(self.dim[0]-1)
        self.startdraw = ( r.width/2 - w/2, self.tilesize[1]+self.padding[1]) 
        self.font = engine.loadFont("type_writer.ttf",18)
        self.texts = [self.font.render(str(i+1),1,(255,255,255)) for i in range(5)]

    def update(self):
        None

    def draw(self):
        x,y = self.startdraw[0], self.startdraw[1]
        for row in self.matrix:
            x=self.startdraw[0]
            for tile in row:
                pygame.draw.rect( self.screen, self.colorOfTile(tile), Rect( (x,y), self.tilesize) )
                x+=self.tilesize[0]+self.padding[0]
            y+=self.tilesize[1]+self.padding[1]

        x, y = self.tilesize[0], self.tilesize[1]+self.padding[1]
        for i in range(5):
            r = Rect( (x,y), self.tilesize)
            self.screen.blit(self.texts[i], r)
            r=r.move(r.width,0)
            pygame.draw.rect( self.screen, self.colorOfTile(i+1), r )
            y += self.tilesize[1]+self.padding[1]

    def colorOfTile(self,t):
        return self.colors[t]

    def randomize(self):
        for x in range(self.dim[0]):
            for y in range(self.dim[1]):
                self.matrix[y][x] = random.randint(1,5)

    def changeTo(self,t):
        curT = self.matrix[0][0]
        x,y=0,0
        foundRight=False
        while True:
            if self.matrix[y][x] == curT:
                self.matrix[y][x] = t
                x+=1
            else:
                if foundRight:
                    break
                else:
                    foundRight=True
                    y+=1
                    x=0
            if x>=self.dim[0]:
                y += 1
            if y>=self.dim[1]:
                break

# --------------------------------------------------------
# --------------------------------------------------------
class Player:
    def __init__(self,engine,board):
        self.engine = engine
        self.board = board
        self.keys = [K_1, K_2, K_3, K_4, K_5]

    def update(self):
        for k in self.keys:
            if self.engine.KEYPRESSED[k]:
                self.board.changeTo( k-K_1+1 )

    def draw(self):
        None

# --------------------------------------------------------
# Main Engine class
# --------------------------------------------------------
class EngineClass:
    def __init__(self,name,resolution):
        self.clock = pygame.time.Clock()
        self.SCREENRECT = Rect(0, 0, resolution[0], resolution[1])
        self.IMAGECACHE, self.SOUNDCACHE, self.FONTCACHE = {}, {}, {}
        self.KEYPRESSED = None
        bestdepth = pygame.display.mode_ok(self.SCREENRECT.size, pygame.DOUBLEBUF, 32)
        self.SCREEN = pygame.display.set_mode(self.SCREENRECT.size, pygame.DOUBLEBUF, bestdepth)
        self.name = name
        pygame.display.set_caption(name)
        self.atfps, self.nextSound = 0.0, 0.0
        self.board = Board(self,self.SCREEN)
        self.player = Player(self, self.board)

    def loadFont(self,fontname,size):
        if not pygame.font: return None
        key = (fontname,size)
        font = None
        if not self.FONTCACHE.has_key(key):
            path = "data/"+fontname
            font = pygame.font.Font(path, size)
            if font: self.FONTCACHE[key] = font
        else:
            font = self.FONTCACHE[ key ]
        return font
        
    def loadSound(self,name):
        fullname = "data/"+name #os.path.join('data', name)
        sound = None
        if not self.SOUNDCACHE.has_key(name):            
            try: 
                sound = pygame.mixer.Sound(fullname+".wav")
            except pygame.error, message:
                print 'Cannot load sound:', name
            if sound:
                self.SOUNDCACHE[name] = sound
        else:
            sound = self.SOUNDCACHE[name]
        return sound
    
    def loadImage(self,file, rotation = 0, flipx = False, flipy = False):
        key = (file, rotation, flipx, flipy)
        if not self.IMAGECACHE.has_key(key):
            path = "data/"+file #os.path.join('data', file)
            ext = ["", ".png", ".bmp", ".gif"]
            for e in ext:
                if os.path.exists(path + e):
                    path = path + e
                    break
            if rotation or flipx or flipy:
                img = self.loadImage(file)
            else:
                img = pygame.image.load(path).convert_alpha()
            if rotation:
                img = pygame.transform.rotate(img, rotation)
            if flipx or flipy:
                img = pygame.transform.flip(img, flipx, flipy)
            self.IMAGECACHE[key] = img
        return self.IMAGECACHE[key]
        
    def playSound(self,name,vol=1.0):
        if self.nextSound <= 0.0: # avoiding two very consecutive sounds
            sound = self.loadSound(name)
            sound.set_volume(vol)
            sound.play()
            self.nextSound = 0.1
        
    def destroy(self):
        None

    def draw(self):
        self.board.draw()
        self.player.draw()
                   
    def update(self,dt):
        # Update fps stats
        self.atfps += dt
        self.nextSound -= dt
        if self.atfps > 3.0:
            pygame.display.set_caption(self.name + " fps: " + str(int(self.clock.get_fps())))
            self.atfps = 0.0     
        self.board.update()
        self.player.update()
# --------------------------------------------------------
# Entry point
# --------------------------------------------------------
def main():
    global ENGINE
    # Initialize
    pygame.init()
    ENGINE = EngineClass( "colors!", (640,480) )
    #pygame.mouse.set_visible(0)
 
    # Main Loop
    nextkey = 0.0
    finished = False
    while not finished:
        # -- CLOCK
        ENGINE.clock.tick(60)
        dt = ENGINE.clock.get_time()/1000.0
        
        # -- INPUT
        for event in pygame.event.get():
            if event.type == QUIT:
                finished = True
                break
        
        ENGINE.KEYPRESSED = pygame.key.get_pressed()
        finished = finished or ENGINE.KEYPRESSED[K_ESCAPE]
        nextkey -= dt
        
        # -- UPDATE
        ENGINE.update(dt)

        # -- DRAW
        ENGINE.draw()

        pygame.display.flip()

    ENGINE.destroy()
    pygame.quit()

# Game when this script is executed, not imported
if __name__ == '__main__':
    main()
    ENGINE.destroy()
    '''
    try:
        main()
    except Exception,e:
        ENGINE.destroy()
        pygame.quit()
        raise e
    '''