#/usr/bin/env python

#Import Modules
import os, pygame, copy
import math, random
from pygame.locals import *

if not pygame.font : print "Warning, pygame 'font' module disabled!"
if not pygame.mixer: print "Warning, pygame 'sound' module disabled!"

# -------------------------------------------------------
def clamp(x,m,M):
    '''Clamping a number between min m and max M'''
    if   x < m : return m
    elif x > M : return M
    return x
    
ENGINE = None # Global GAME variable

# -------------------------------------------------------
class Actor(object):
    '''Base Actor class'''
    def __init__(self,engine):
        self.engine = engine
    
    def update(self, dt): 
        None
    
    def draw(self): 
        None

    def destroy(self):
        None

# --------------------------------------------------------
class BoardBase(Actor):
    ''' Base logic for boards '''
    def __init__(self,engine,tilesdim):
        super(BoardBase,self).__init__(engine)
        self.dim = tilesdim
        self.colors=[ (100,100,100), (169,15,14), (94,179,20), (40,169,218), (112,0,252), (231,201,27)]        
        self.font = engine.loadFont("type_writer.ttf",18)
        self.texts = [self.font.render(str(i+1),1,(255,255,255)) for i in range(5)]

# --------------------------------------------------------
class BoardSquares(BoardBase):
    '''Contains the board logic. SQUARES'''
    def __init__(self,engine,tilesdim=(8,9)):
        super(BoardSquares,self).__init__(engine,tilesdim)
        self.grid = [[0 for x in range(self.dim[0])] for y in range(self.dim[1])]                
        self.randomize()

    def update(self, dt):
        super(BoardSquares,self).update(dt)

    def draw(self):    
        super(BoardSquares,self).draw()
        sx, sy = 10, 10
        px, py = 5, 5
        r = Rect( sx, sy, 32, 32)        
        scr = self.engine.SCREEN
        for j in range(self.dim[1]):
            r.x = sx
            for i in range(self.dim[0]):
                c = self.grid[j][i]
                pygame.draw.rect( scr, self.colors[c], r)
                r.x += r.width + px
            r.y += r.height + py

    def randomize(self):
        for x in range(self.dim[0]):
            for y in range(self.dim[1]):
                self.grid[y][x] = random.randint(1,5)

    def changeTo(self,t):
        None

# --------------------------------------------------------
class BoardTriangles(BoardBase):
    '''Contains the board logic. TRIANGLES'''
    def __init__(self,engine,tilesdim=(7,7)):
        super(BoardTriangles,self).__init__(engine,tilesdim)        
        self.grid = [[0 for x in range(self.dim[0])] for y in range(self.dim[1])]        
        self.randomize()

    def update(self, dt):
        super(BoardSquares,self).update(dt)

    def draw(self):    
        super(BoardSquares,self).draw()

    def randomize(self):
        for x in range(self.dim[0]):
            for y in range(self.dim[1]):
                self.grid[y][x] = random.randint(1,5)

    def changeTo(self,t):
        None

# --------------------------------------------------------
class Player(Actor):
    '''A player has the input game logic'''
    def __init__(self,engine,board):
        super(Player,self).__init__(engine)
        self.board = board
        self.keys = [K_1, K_2, K_3, K_4, K_5]

    def update(self, dt):
        for k in self.keys:
            if self.engine.KEYPRESSED[k]:
                self.board.changeTo( k-K_1+1 )

    def draw(self):
        None

# --------------------------------------------------------
class Engine:
    '''Main Engine class'''
    def __init__(self,name,resolution):
        '''Builds the Engine'''
        self.clock = pygame.time.Clock()
        self.SCREENRECT = Rect(0, 0, resolution[0], resolution[1])
        self.IMAGECACHE, self.SOUNDCACHE, self.FONTCACHE = {}, {}, {}
        self.KEYPRESSED = None
        bestdepth = pygame.display.mode_ok(self.SCREENRECT.size, pygame.DOUBLEBUF, 32)
        self.SCREEN = pygame.display.set_mode(self.SCREENRECT.size, pygame.DOUBLEBUF, bestdepth)
        self.name = name
        pygame.display.set_caption(name)
        self.atfps, self.nextSound = 0.0, 0.0        
        self.actors = []

    def addActor(self,a):
        '''Registers an actor in the game. an actor must be subclass of Actor'''
        self.actors.append(a)

    def destroy(self):        
        '''Deinit the engine'''
        for a in self.actors:
            a.destroy()
        self.actors = []

    def loadFont(self,fontname,size):
        '''Loads and caches a font handle'''
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
        '''Loads and caches a sound handle'''
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
        '''Loads and caches an image handle'''
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
        '''Plays a sound by name'''
        if self.nextSound <= 0.0: # avoiding two very consecutive sounds
            sound = self.loadSound(name)
            sound.set_volume(vol)
            sound.play()
            self.nextSound = 0.1

    def draw(self):
        '''Draws and flip buffers'''
        for a in self.actors:
            a.draw()        
        pygame.display.flip()
                   
    def update(self,dt):
        '''Updates the engine state'''
        # Update fps stats
        self.atfps += dt
        self.nextSound -= dt
        if self.atfps > 3.0:
            pygame.display.set_caption(self.name + " fps: " + str(int(self.clock.get_fps())))
            self.atfps = 0.0     
        for a in self.actors:
            a.update(dt)

# --------------------------------------------------------
# Entry point
# --------------------------------------------------------
def main():
    global ENGINE
    # Initialize
    pygame.init()
    ENGINE = Engine( "colors!", (640,480) )
    board = BoardSquares(ENGINE)
    player = Player(ENGINE, board)
    ENGINE.addActor( board )
    ENGINE.addActor( player )
    
    #pygame.mouse.set_visible(0)
 
    # Main Loop
    nextkey = 0.0
    finished = False
    while not finished:
        # Clock
        ENGINE.clock.tick(60)
        dt = ENGINE.clock.get_time()/1000.0
        
        # Input
        for event in pygame.event.get():
            if event.type == QUIT:
                finished = True
                break        
        ENGINE.KEYPRESSED = pygame.key.get_pressed()
        finished = finished or ENGINE.KEYPRESSED[K_ESCAPE]
        nextkey -= dt
        
        # Update
        ENGINE.update(dt)

        # Draw
        ENGINE.draw()

    ENGINE.destroy()
    pygame.quit()

# Execute the game when this py is exec, not imported
if __name__ == '__main__':
    main()    