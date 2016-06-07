#/usr/bin/env python

#Import Modules
import os, pygame, copy
import math, random
from pygame.locals import *
import engine

# --------------------------------------------------------
class BoardBase(engine.Actor):
    colors = [ (169,15,14), (94,179,20), (40,169,218), (112,0,252), (231,201,27)]        

    ''' Base logic for boards '''
    def __init__(self,engine,tilesdim):
        super(BoardBase,self).__init__(engine)
        self.dim = tilesdim
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
                pygame.draw.rect( scr, BoardBase.colors[c], r)
                r.x += r.width + px
            r.y += r.height + py

    def randomize(self):
        for x in range(self.dim[0]):
            for y in range(self.dim[1]):
                self.grid[y][x] = random.randint(0,len(BoardBase.colors)-1)

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
                self.grid[y][x] = random.randint(0,len(BoardBase.colors)-1)

    def changeTo(self,t):
        None

# --------------------------------------------------------
class Player(engine.Actor):
    '''A player has the input game logic'''
    def __init__(self,engine,board):
        super(Player,self).__init__(engine)
        self.board = board

    def draw(self):
        None

    def mouseUp(self,pos):
        None

# --------------------------------------------------------
# Entry point, only when executed, not imported
# --------------------------------------------------------
if __name__ == '__main__':
    # Initialize engine and actors
    pygame.init()
    eng = engine.Engine( "colors!", (640,480) )
    board = BoardSquares(eng)
    player = Player(eng, board)
    eng.addActor( board )
    eng.addActor( player )
    #pygame.mouse.set_visible(0)
    
    # Main loop
    eng.run()

    # Finishing 
    eng.destroy()
    pygame.quit()    