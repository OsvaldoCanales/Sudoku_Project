#GUI.py

#Import pygame library
import pygame

#Import time library
import time
from solver import valid, find_empty

#Initialise the pygame font
pygame.font.init()

#Class manages the overall state and behavior of the Sudoku grid
class Grid:
    #Initalize board 
    board = [
        [7, 8, 0, 4, 0, 0, 1, 2, 0],
        [6, 0, 0, 0, 7, 5, 0, 0, 9],
        [0, 0, 0, 6, 0, 1, 0, 7, 8],
        [0, 0, 7, 0, 4, 0, 2, 6, 0],
        [0, 0, 1, 0, 5, 0, 9, 3, 0],
        [9, 0, 4, 0, 6, 0, 0, 0, 5],
        [0, 7, 0, 3, 0, 0, 0, 1, 2],
        [1, 2, 0, 0, 0, 7, 4, 0, 0],
        [0, 4, 9, 2, 0, 6, 0, 0, 7]
    ]
    
    #Constructor with the specified number of rows, columns, width, height and a Pygame window
    #Creates a 2D list of 'Cube' objects, representing the Sudoku grid
    def __init__(self, rows, cols, width, height, win):
        self.rows = rows
        self.cols = cols

        #For each row and column, it creates a 'Cube' object using the cube class
        #Essentially a grid of 'Cube' objects with the initial values from the Sudoku board
        self.cubes = [[Cube(self.board[i][j], i, j, width, height) for j in range(cols)] for i in range(rows)]

        self.width = width
        self.height = height
        #Current state of the Sudoku grid
        self.model = None 
        #Updates model with current values in the 'self.cubes' grid
        self.update_model()
        self.selected = None
        self.win = win 

    #Represents the current state of the Sudoku grid based on the values in the 'Cube'objects
    def update_model(self):
        self.model = [[self.cubes[i][j].value for j in range(self.cols)] for i in range(self.rows)]

    #Used to place a value in the selected cell
    def place(self, val):
        row, col = self.selected
        if self.cubes[row][col].value == 0:
            self.cubes[row][col].set(val)
            self.update_model()

            #Checks to see if placement is valid and then attempts to solve the puzzle
            #Returns true if valid
            if valid(self.model, val, (row, col)) and self.solve():
                return True
            #Reverts the changes and returns False if not valid
            else:
                self.cubes[row][col].set(0)
                self.cubes[row][col].set_temp(0)
                self.update_model()
                return False
    
    #Temporarily set a value in the selected cell without making it permanent
    def sketch(self, val):
        row, col = self.selected
        self.cubes[row][col].set_temp(val)

    #Drawing the Sudoku grid lines and cubes
    def draw(self):
        #Draw Grid Lines
        gap = self.width / 9
        for i in range(self.rows+1):
            if i % 3 == 0 and i != 0:
                thick = 4
            else:
                thick = 1 
            pygame.draw.line(self.win, (0,0,0), (0, i*gap), (self.width, i * gap), thick)
            pygame.draw.line(self.win, (0, 0, 0), (i *gap, 0), (i * gap, self.height), thick)

        #Draw cubes
        for i in range(self.rows):
            for j in range(self.cols):
                self.cubes[i][j].draw(self.win)

    #Select a specific cell in the Sudoku grid
    def select(self, row, col):
        #Reset all other
        for i in range(self.rows):
            for j in range(self.cols):
                self.cubes[i][j].selected = False

        #Sets the selected cube to True which highlights the selected cell
        #Updates the 'self.selected' to store the coordinates of the selected cell
        self.cubes[row][col].selected = True
        self.selected = (row, col)

    #Clears the temporary value in the currently selected cell if the cell's value is already 0
    def clear(self):
        row, col = self.selected
        if self.cubes[row][col].value == 0:
            self.cubes[row][col].set_temp(0)

    #Represent mouse click position
    def click(self, pos):
        """
        :param: pos
        :return: (row, col)
        """
        #Check to see if position is within bounds of the Sudoku grid
        #Return a tuple '(row, col)
        if pos[0] < self.width and pos[1] < self.height:
            gap = self.width / 9
            x = pos[0] // gap
            y = pos[1] // gap
            return (int(y), int(x))
        #If the click is outside the grid
        else:
            return None
        
    #Checks whether the Sudoku puzzle is completed
    #Returns 'False' if it finds any cell with a value of 0
    def is_finished(self):
        for i in range(self.rows):
            for j in range(self.cols):
                if self.cubes[i][j].value == 0:
                    return False
        return True
    
    #Recurive backtracking algorithm to solve the puzzle
    def solve(self):

        #Find the first empty cell 
        find = find_empty(self.model)
        if not find:
            return True
        else:
            row, col = find

        #Attempt to fill the empty cell from 1 - 9
        for i in range(1, 10):
            if valid(self.model, i, (row, col)):
                self.model[row][col] = i

                #Recursive call 
                if self.solve():
                    return True

                #If False is returned then backtract by resetting current cell to 0
                self.model[row][col] = 0

        return False
    
    #Graphical updates using Pygame to visualize the solving process
    def solve_gui(self):
        self.update_model()
        find = find_empty(self.model)
        if not find:
            return True
        else:
            row, col = find

        for i in range(1, 10):
            if valid(self.model, i, (row, col)):
                #Update the 'self.cubes' grid
                self.model[row][col] = i
                self.cubes[row][col].set(i)
                #Draw changes
                self.cubes[row][col].draw_change(self.win, True)
                self.update_model()
                pygame.display.update()
                #Delay to make the solving process visible
                pygame.time.delay(100)

                if self.solve_gui():
                    return True
                
                self.model[row][col] = 0
                self.cubes[row][col].set(0)
                self.update_model()
                self.cubes[row][col].draw_change(self.win, False)
                pygame.display.update()
                pygame.time.delay(100)

        return False

#Class represents the individual cells within the grid
class Cube:
    rows = 9
    cols = 9

    #initialize a Cube object with the specificed attributes
    def __init__(self, value, row, col, width, height):
        self.value = value
        #Temporary value used for sketching before making it permanent
        self.temp = 0
        self.row = row
        self.col = col
        self.width = width
        self.height = height
        self.selected = False

    #Responsible for drawing the cube on the Pygame window
    def draw(self, win):
        fnt = pygame.font.SysFont("comicsans", 40)

        #Calculates the width of each gap between cubes
        gap = self.width / 9
        #Calculates the x-coordinate of the top-left corner of cube
        x = self.col * gap
        #Calculates the y-coordinate of the top-left corner of cube
        y = self.row * gap

        #If cube has temporary value not 0 and is 0 (indicates empty cell)
        #Renders the temporary value as text
        if self.temp != 0 and self.value == 0:
            text = fnt.render(str(self.temp), 1, (128, 128, 128))
            win.blit(text, (x+5, y +5))

        #If the cube has an actual value that is not equal to 0
        elif not(self.value == 0):
            text = fnt.render(str(self.value), 1, (0, 0, 0))
            win.blit(text, (x + gap/2 - text.get_width()/2, y + (gap/2 - text.get_height()/2)))

        #If cube is selected then draw a red rect around it
        if self.selected:
            pygame.draw.rect(win, (255,0,0), (x, y, gap, gap), 3)

    #Draw changes in the cube during the solution process
    def draw_change(self, win, g = True):
        fnt = pygame.font.SysFont("comicsans", 40)

        gap = self.width / 9 
        x = self.col * gap
        y = self.row * gap 

        #Clear the existing content of the cube by drawing a white rect
        pygame.draw.rect(win, (255, 255, 255), (x, y, gap, gap), 0)
        #Renders and displays the new value
        text = fnt.render(str(self.value), 1, (0,0,0))
        win.blit(text, (x + (gap / 2 - text.get_width() / 2 ), y + ( gap / 2 - text.get_height() / 2 )))
        #If true, then green rect to indicate change is valid
        if g: 
            pygame.draw.rect(win, (0, 255, 0), (x, y, gap, gap), 3)
        #Red rect to indicate invalid change
        else:
            pygame.draw.rect(win, (255, 0, 0), (x, y, gap, gap), 3)

    #Sets the permanent value of the cube
    def set(self, val):
        self.value = val

    #Sets the temporary value of the cube 
    def set_temp(self, val):
        self.temp = val


#Updates the Pygame window
def redraw_window(win, board, time, strikes):
    #First fill in the window with white
    win.fill((255, 255, 255))
    #Draw time
    fnt = pygame.font.SysFont("comicsans", 25)
    text = fnt.render("Time: " + format_time(time), 1, (0,0,0))
    win.blit(text, (540 - 160, 560))
    #Draw Strikes
    text = fnt.render("X" * strikes, 1, (255, 0, 0))
    win.blit(text, (20, 560))
    #Draw grid and board
    board.draw()

#Utility function that calculates the time
def format_time(secs):
    sec = secs % 60 
    minute = secs // 60 
    hour = minute // 60 

    mat = " " + str(minute) + ":" + str(sec)
    return mat

#function to display instructions
def display_instructions(win):
    fnt = pygame.font.SysFont("comicsans", 20)
    text1 = fnt.render("Welcome to Sudoku!",0, (0,0,0))
    text2 = fnt.render("Use numbers 1-9 to fill the grid", 0, (0,0,0))
    text3 = fnt.render("Entering a number will display a sketch",0,(0,0,0))
    text7 = fnt.render("press ENTER to place the number", 0, (0,0,0))
    text4 = fnt.render("Enter DELETE to clear a cell",0,(0,0,0))
    text5 = fnt.render("Press SPACE to start the game",0,(0,0,0))
    text6 = fnt.render("Good luck!", 0, (0,0,0))

    win.fill((255,255,255))
    win.blit(text1, (20, 50))
    win.blit(text2, (20, 100))
    win.blit(text3, (20, 150))
    win.blit(text7, (20, 200))
    win.blit(text4, (20, 250))
    win.blit(text5, (20, 300))
    win.blit(text6, (20, 350))
    pygame.display.update()

#Initalize the Pygame Window
def main():
    win = pygame.display.set_mode((540,600))
    pygame.display.set_caption("Sudoku By Oz")
    board = Grid(9, 9, 540, 540, win)
    key = None
    run = True
    start = time.time()
    strikes = 0 

    display_instructions(win)
    start_game = False

    #Instrunction window till user starts the game
    while not start_game:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                start_game = True

    #Run the game till user exits or completes the puzzle
    while run:

        play_time = round(time.time() - start)

        #Handle user input (key presses and mouse clicks)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_1:
                    key = 1
                if event.key == pygame.K_2:
                    key = 2
                if event.key == pygame.K_3:
                    key = 3
                if event.key == pygame.K_4:
                    key = 4
                if event.key == pygame.K_5:
                    key = 5
                if event.key == pygame.K_6:
                    key = 6
                if event.key == pygame.K_7:
                    key = 7
                if event.key == pygame.K_8:
                    key = 8
                if event.key == pygame.K_9:
                    key = 9
                if event.key == pygame.K_KP1:
                    key = 1
                if event.key == pygame.K_KP2:
                    key = 2
                if event.key == pygame.K_KP3:
                    key = 3
                if event.key == pygame.K_KP4:
                    key = 4
                if event.key == pygame.K_KP5:
                    key = 5
                if event.key == pygame.K_KP6:
                    key = 6
                if event.key == pygame.K_KP7:
                    key = 7
                if event.key == pygame.K_KP8:
                    key = 8
                if event.key == pygame.K_KP9:
                    key = 9
                if event.key == pygame.K_DELETE:
                    board.clear()
                    key = None

                #User enters spacebar to solve the board 
                if event.key == pygame.K_SPACE:
                    print("Space Pressed")
                    board.solve_gui()

                #User enters return to place value
                if event.key == pygame.K_RETURN:
                    i, j = board.selected
                    if board.cubes[i][j].temp != 0:
                        if board.place(board.cubes[i][j].temp):
                            print("Success")
                        #Invalid user input 
                        else:
                            print("Wrong")
                            strikes += 1 
                        key = None

                        if board.is_finished():
                            print("Game Over")

                #User clicks on mouse on the board
            if event.type == pygame.MOUSEBUTTONDOWN:
                pos = pygame.mouse.get_pos()
                clicked = board.click(pos)
                if clicked:
                    board.select(clicked[0], clicked[1])
                    key = None
        if board.selected and key != None:
            board.sketch(key)

        redraw_window(win, board, play_time, strikes)
        pygame.display.update()

main()
pygame.quit()