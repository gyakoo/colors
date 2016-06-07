#/usr/bin/env python

#Import Modules
import os, pygame, copy
import math, random
from pygame.locals import *
import engine

# --------------------------------------------------------
class BoardBase(engine.Actor):
    ''' Base logic for boards '''

    colors = [ (169,15,14), (94,179,20), (40,169,218), (112,0,252), (231,201,27)]        
    inputButtons = [ Rect(0,0,0,0), Rect(0,0,0,0), Rect(0,0,0,0), Rect(0,0,0,0), Rect(0,0,0,0) ]
    resetButton = Rect(0,0,0,0)

    def __init__(self,engine,tilesdim):
        super(BoardBase,self).__init__(engine)
        self.dim = tilesdim
        self.font = engine.loadFont("type_writer.ttf",18)
        self.txtStart = self.font.render("Reset",1,(255,255,255))
        self.inputPos = (0,0)
        self.inputSize = (48,48)
        self.inputPadX = 13

    def draw(self):        
        scr = self.engine.SCREEN
        r = Rect( self.inputPos, self.inputSize )
        i = 0
        for c in BoardBase.colors:
            BoardBase.inputButtons[i] = copy.copy(r)
            pygame.draw.rect( scr, c, r)
            r.x += r.width + self.inputPadX
            i += 1
        pos = (self.inputPos[0], self.inputPos[1]+self.inputSize[1]+self.inputPadX*2)
        scr.blit(self.txtStart, pos)
        BoardBase.resetButton = Rect(pos,self.txtStart.get_rect().size)
    
    @staticmethod
    def inColorButton(pos):
        for i in range(0,len(BoardBase.inputButtons)):
            if BoardBase.inputButtons[i].collidepoint(pos):
                return i
        return -1

    @staticmethod
    def inResetButton(pos):
        return BoardBase.resetButton.collidepoint(pos)

    def changeTo(self,t):
        None

    def randomize(self):
        None

    def reset(self):
        self.randomize()

    def finished(self):
        None

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
        sx, sy = 10, 10 # start pos
        px, py = 5, 5 # padding
        r = Rect( sx, sy, 32, 32)        
        scr = self.engine.SCREEN
        for j in range(self.dim[1]):
            r.x = sx
            for i in range(self.dim[0]):
                c = self.grid[j][i]
                pygame.draw.rect( scr, BoardBase.colors[c], r)
                r.x += r.width + px
            r.y += r.height + py

        # preparing input pad pos/size
        w = (r.x-sx)/len(BoardBase.colors)
        self.inputPadX = 8
        w -= self.inputPadX
        self.inputSize = ( w, w )
        self.inputPos = (sx, r.y+32)
        super(BoardSquares,self).draw()
        
    def randomize(self):
        for x in range(self.dim[0]):
            for y in range(self.dim[1]):
                self.grid[y][x] = random.randint(0,len(BoardBase.colors)-1)

    def changeTo(self,t):
        x, y = 0, 0
        cc = self.grid[0][0]
        self.floodFill(cc,t,x,y)

    # recursive, not so fast but ok so far
    def floodFill(self,cc,t,x,y):
        if x+1 < self.dim[0]:
            nc = self.grid[y][x+1]
            if nc==cc or nc==t:
                self.floodFill(cc,t,x+1,y)

        if y+1 < self.dim[1]:
            nc = self.grid[y+1][x]
            if nc==cc or nc==t:
                self.floodFill(cc,t,x,y+1)

        if self.grid[y][x]==cc:
            self.grid[y][x]=t

    def finished(self):
        cc = self.grid[0][0]
        for row in self.grid:
            for c in row:
                if c!=cc:
                    return False
        return True

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

# --------------------------------------------------------
class Player(engine.Actor):
    '''A player has the input game logic'''
    def __init__(self,engine,board):
        super(Player,self).__init__(engine)
        self.board = board
        self.clicks = 0

    def mouseUp(self,pos):
        b = BoardBase.inColorButton(pos)
        if b>=0:
            if self.board.finished():
                print "Completed!"
            else:
                self.board.changeTo(b)
                self.clicks += 1
                print self.clicks, " clicks"
                if self.board.finished():
                    self.mouseUp(pos)

        elif BoardBase.inResetButton(pos):
            self.reset()

    def reset(self):
        self.board.reset()
        self.clicks = 0
        

# --------------------------------------------------------
# Entry point, only when executed, not imported
# --------------------------------------------------------
if __name__ == '__main__':
    # Initialize engine and actors
    pygame.init()
    eng = engine.Engine( "colors!", (316,480) )
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