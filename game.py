import pygame
import sys
import random

pygame.init()  # initializing pygame modules



InitialCellSize = 50  # starting cell size
Dragging = False    
ZoomStep = 1.07   
MaxCellSize = 75        
MinCellSize = 20

# shift in origin after dragging
OriginShiftX = 0     
OriginShiftY = 0

YellowCells = set()   # tracks position of my yellow cells 

Click = True
Stop = True
FPS = 10
Step = False
s=0



w = int(input("Width: "))
h = int(input("Height: "))

# Assigining coords for Random start
def RandomStart():
    StartCoords = set() 
    for i in range(20):
        
        # this allocates yellow cells randomly around the centre
        x = random.randint(w//(2*InitialCellSize)-4, w//(2*InitialCellSize)+4) 
        y = random.randint(h//(2*InitialCellSize)-4, h//(2*InitialCellSize)+4)
        StartCoords.add((x, y))
    return StartCoords




screen = pygame.display.set_mode((w, h)) 
clock = pygame.time.Clock()
mouse_pos = [] # keeps track of coords where i am left clicking


# this fuction run two for loops in  3*3 matrix with cell in consideration at the centre and returns 
# the number of its yellow neighbours
def neighbours(cell,Ycells):
    count = 0 
    x,y =cell
    x=int(x)
    y=int(y)
    for X in range(x-1,x+2):
        for Y in range(y-1,y+2):
            if (X,Y) != (x,y):
                if (X,Y) in Ycells:
                    count = count + 1
    return count 


# this function is for checking the possibility of a dead cell becoming alive if it has
# 3 neighbours... it calculates the neighbours of a dead cells which are neighbouring to 
# the alive cells and returns the set of cells to be made alive   
def new_cell(cell,Ycells):
    NewCells=set()
    x,y =cell
    x=int(x)
    y=int(y)
    for X in range(x-1,x+2):
        for Y in range(y-1,y+2):
            if (X,Y) not in Ycells:
                n=neighbours((X,Y),Ycells)
                if n==3:
                    NewCells.add((X,Y)) 
    return NewCells

# game loop
while True:
    for event in pygame.event.get():      
        # handling quitting of game
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        if event.type == pygame.KEYDOWN:
            # pausing and unpausing using spacebar
            if event.key == pygame.K_SPACE:
                if not Stop:
                    Stop = True
                else:
                    Stop=False
            # if r is pressed new cells are randomly initialized        
            if event.key == pygame.K_r:
                for x, y in RandomStart():
                    YellowCells.add((x, y))
            # reset everything if q is pressed
            if event.key == pygame.K_q:
                YellowCells = set()
                Stop = True
            # converts the continuous state into step and step into continuous
            if event.key == pygame.K_c:
                if not Step:
                    Step = True
                else:
                    Step = False
            # reset the step count by setting s=0 on pressing arrow key
            if event.key == pygame.K_RIGHT:
                s=0


        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Left mouse button
                Dragging = True

            # zooming in logic - increase the cell size till max cell size 
            # Also shifting the origin on zooming in   
            elif event.button == 4:  # Mouse wheel up
                NewCellSize = int(InitialCellSize * ZoomStep)
                if NewCellSize <= MaxCellSize:
                    MouseX, MouseY = event.pos
                    OriginShiftX = (OriginShiftX - MouseX) * ZoomStep + MouseX
                    OriginShiftY = (OriginShiftY - MouseY) * ZoomStep + MouseY
                    InitialCellSize = NewCellSize
            
            # zooming out logic
            elif event.button == 5:  # Mouse wheel down
                NewCellSize = int(InitialCellSize / ZoomStep)
                if NewCellSize >= MinCellSize:
                    MouseX, MouseY = event.pos
                    OriginShiftX = (OriginShiftX - MouseX) / ZoomStep + MouseX
                    OriginShiftY = (OriginShiftY - MouseY) / ZoomStep + MouseY
                    InitialCellSize = NewCellSize

        if event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:  # Left mouse button
                # adding a yellow cell on clicking 
                # logic - keeping track of where clicked and checking its collision with rectangle and adding that rectangle's coords to Yellowcells set 
                if Click:
                    MX, MY=pygame.mouse.get_pos()
                    mouse_pos.append((MX,MY))
                
                Click = True    
                Dragging = False  
        if event.type == pygame.MOUSEMOTION:
            
            if Dragging:
                Click =False  # this ensures that a cell is not added while dragging
                dx, dy = event.rel  # gives relative change in position of mouse after its motion 
                OriginShiftX -= dx
                OriginShiftY -= dy

    screen.fill((128, 128, 128)) 

    StartX = int(-OriginShiftX % InitialCellSize)
    StartY = int(-OriginShiftY % InitialCellSize)

    for x in range(StartX, w, InitialCellSize):
        for y in range(StartY, h, InitialCellSize):
            # this coords are in terms of cell count and are more useful and easy to keep track of
            LogicalX = (x + OriginShiftX) // InitialCellSize 
            LogicalY = (y + OriginShiftY) // InitialCellSize 

            Cell = pygame.Rect(x, y, InitialCellSize, InitialCellSize)
            # checking clicking on a rectangle 
            if len(mouse_pos) !=0:
                if Cell.collidepoint(mouse_pos[-1]):
                    mouse_pos.pop() 
                    YellowCells.add((LogicalX,LogicalY))
            # drawing yellow cells
            if (LogicalX, LogicalY) in YellowCells:
                if Stop:
                    pygame.draw.rect(screen, (255, 0, 0), Cell)
                else:
                    pygame.draw.rect(screen, (255, 255, 0), Cell)                    
            pygame.draw.rect(screen, (0, 0, 0), Cell, 1)
    
    pygame.display.flip()
    

    # this takes care of the game rules
    # i am making a set of which coords to add and which to remove.  
    if not Step:
        FPS = 5 # so that changes are at visible speed
        if not Stop:
            ToRemove = set()
            ToAdd = set()
            for cell in list(YellowCells):
                n = neighbours(cell, YellowCells)
                if n < 2 or n > 3:
                    ToRemove.add(cell)
                ToAdd.update(new_cell(cell, YellowCells))
            
            YellowCells.difference_update(ToRemove)
            YellowCells.update(ToAdd)
    else:
        FPS = 120
        if not Stop:
            if not s:
                ToRemove = set()
                ToAdd = set()
                for cell in list(YellowCells):
                    n = neighbours(cell, YellowCells)
                    if n < 2 or n > 3:
                        ToRemove.add(cell)
                    ToAdd.update(new_cell(cell, YellowCells))
                
                YellowCells.difference_update(ToRemove)
                YellowCells.update(ToAdd)
                s=s+1

   
    clock.tick(FPS)
