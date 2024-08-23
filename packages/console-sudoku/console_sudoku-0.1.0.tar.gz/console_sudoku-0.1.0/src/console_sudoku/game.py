from copy import deepcopy
from datetime import datetime
from typing import List
from math import sqrt
import random

def run():
    r = SudokuRunner()
    r.run_game()

class SudokuSolver:

    # cell_options param might look like ["W", "L", "F", "S", "T", "R", "N", "G", "P"]
    # The size of the grid will always be the length of cell_options  
    def __init__(self, cell_options:List[str]) -> None:
        self.options: List[str] = cell_options
        self.first = True
        self.chunk_size = int(sqrt(len(cell_options)))

    
    # Takes a sudoku grid with some values filled in (2D array) and returns a solution grid 
    # with all cells filled in (also a 2D array).  Empty cell values are None.
    def solve(self, grid:List[List[str]]) -> List[List[str]]:
        
        # Creates the sets for each row, col and chunk
        # only runs once the first time the function is called
        if self.first:
            self.first = False
            
            # dicts that will store the sets
            self.rows = {}
            self.cols = {}
            self.chunks = {}
            self.val = []
            self.val_num = []
            not_found = deepcopy(self.options)

            # list that will store the indexes of all the empty spaces
            self.empty = []

            # add all the sets for each row and col
            # also gets each index for the empty spaces
            for row in range(len(grid)):
                my_set_1 = set(grid[row])
                my_set_1.discard(None)
                self.rows[row] = my_set_1
                
                my_set = set()
                for col in range (len(grid[row])):
                    my_set.add(grid[col][row])
                    
                    # gets the index for the empty spaces and adds it to the list
                    if grid[row][col] == None:
                        self.empty.append([row, col])


                    elif grid[row][col] in not_found:
                        self.val.append(grid[row][col])
                        self.val_num.append(1)
                        not_found.remove(grid[row][col])
                    
                    else:
                        index = self.val.index(grid[row][col])
                        self.val_num[index] += 1

                my_set.discard(None)
                self.cols[row] = my_set

            chunk_num = 0

            # gets the sets for each chunk and adds them to the dict
            for row in range(0, len(grid), int(self.chunk_size)):
                for col in range(0, len(grid[row]), int(self.chunk_size)):
                    my_set = set()
                    for i in range(int(self.chunk_size)):
                        for j in range (int(self.chunk_size)):
                            my_set.add(grid[i + row][j + col])
                    my_set.discard(None)
                    self.chunks[chunk_num] = my_set
                    chunk_num += 1

        # base case, will return grid if there are no empty spaces left
        if len(self.empty) == 0:
            return grid
        

        # recursive case, will run if there are still empty spaces in the grid:

        # get the best order to replace the empty squares in
        # will find the index which has the least num of possible answers, and starts fillng it in
        self.best_order()

        min_val = min(self.empty_vals)

        index = self.empty_vals.index(min_val)

        my_index = self.empty_indexes[index]

        # get the row and col indexes of the current space
        row: int = my_index[0]
        col: int = my_index[1]

        # checking to see if the current index is empty
        # gets all the possible options to put in the empty space
        options: set = self.empty_options[index]
            
        # if we don't have any possible options, we return None
        if len(options) == 0:
            return None

        my_chunk = self.get_chunk(row, col)

        # run through all the possible options
        for option in options:

            # set the grid val to the possible option
            grid[row][col] = option
            self.rows[row].add(option)
            self.cols[col].add(option)
            self.chunks[my_chunk].add(option)
                
            # recursive call
            self.empty_indexes.pop(index)
            self.empty_vals.pop(index)
            self.empty.remove(my_index)
            my_solve: List[List[str]] = self.solve(grid)

            # checks to see if the option will allow us to complete the board or will it fail
            # if it fails then we reset and continue iterating through the possible options
            if (my_solve == None):
                grid[row][col] = None
                self.rows[row].discard(option)
                self.cols[col].discard(option)
                self.chunks[my_chunk].discard(option)
                self.empty.append(my_index)
                self.empty_indexes.append(my_index)
                self.empty_vals.append(min_val)
                continue
                            
            # if the option did allow us to complete the board, it will return the completed board
            return my_solve

        # if none of the options led to a completed board, or if there were no options then we return None
        return None

    # Takes an index in the sudoku array and get all the values that you can set the index to
    # Will return a list of chars that you can set the index to that are allowed via the constraints of the game of sudoku
    def valid_options(self, row: int, col: int) -> set:

        # create a set with all the possible values that the board could have
        return_set = set(self.options)
        

        # remove all the values that are present in the row, col, and chunk and return the final set
        return_set = return_set.difference(self.rows[row])
        return_set = return_set.difference(self.cols[col])
        return_set = return_set.difference(self.chunks[self.get_chunk(row, col)])
        
        return return_set

    # Takes in an 2D list that represents the sudoku board and finds
    # the most optimal order to find those values
    def best_order(self):
        
        # create lists to store values in
        self.empty_indexes = []
        self.empty_vals = []
        self.empty_options = []

        # iterate through grid to find all spaces with none
        for index in self.empty:

            # save the index of the current space
            row = index[0]
            col = index[1]
            # find the number of valid options to fill the space with
            options = self.valid_options(row, col)
            #options = self.sort_set(options_set)

            self.empty_indexes.append(index)
            self.empty_vals.append(len(options))
            self.empty_options.append(options)

        # return our list of indexes that are sorted from least to greatest num options
        return self.empty_indexes


    # gets the chunk number of the row and col
    def get_chunk(self, row, col) -> int:
        chunk_start_x = int((col // self.chunk_size) * self.chunk_size)
        chunk_start_y = int((row // self.chunk_size) * self.chunk_size)

        return int(chunk_start_y) + int(chunk_start_x / self.chunk_size)


class SudokuGenerator:

    def __init__(self, chars: list, difficulty: int):
        self.possible_chars = chars
        self.size = len(chars)
        self.difficulty = difficulty


    # returns a tuple of (PUZZLE, ANSWER_KEY)
    def generate_puzzle(self):

        # generate empty puzzle
        temp_puzzle = [[None for x in range(self.size)] for y in range(self.size)]
        
        # generate one row of the puzzle from the provided chars
        row_n = deepcopy(self.possible_chars)
        random.shuffle(row_n)

        # choose which row the puzzle will be populated with the generated list above
        n = random.randint(0, self.size-1)
        temp_puzzle[n] = row_n

        # generate the full puzzle
        Answer_Generator: SudokuSolver = SudokuSolver(self.possible_chars)
        answer = Answer_Generator.solve(temp_puzzle)

        # replace desired amount of cells with value None
        # num replaced will depend on the difficulty desired
        # formula to determine num replaced: size * difficulty * 1.375
        desired_empty = ((0.17 * (self.size * self.size)) * self.difficulty) // 1

        curr_empty = 0
        empty_cells = set()
        final_puzzle = deepcopy(answer)

        while curr_empty != desired_empty:
            new_empty = (random.randint(0, self.size - 1), random.randint(0, self.size - 1))

            if new_empty in empty_cells:
                while new_empty in empty_cells:
                    new_empty = (random.randint(0, self.size - 1), random.randint(0, self.size - 1))

            empty_cells.add(new_empty)
            final_puzzle[new_empty[0]][new_empty[1]] = " "

            curr_empty += 1

        return (final_puzzle, answer)


    # prints out the puzzle in an easy to read format
    @staticmethod
    def print_puzzle(size, puzzle: list):

        for row in puzzle:
            print("\033[37m-" * ((size * 4) + 1))

            #for i in range(self.size):
            #    print("|   ", end="")
            #print("|")
            for val in row:
                if val == None:
                    print("\033[37m|   ", end="")
                
                else:
                    print("\033[37m| ", end="")
                    print(val, end="")
                    print(" ", end="")
                    #print("| " + str(val) + " ", end="")

            print("\033[37m|")

        print("\033[37m-" * ((size * 4) + 1))


class SudokuRunner:

    def __init__(self):
        self.possible_sizes = [4, 9, 16]
        self.size = 9
        self.possible_chars = [ '1', '2', '3', '4',
                                '5', '6', '7', '8',
                                '9', 'A', 'B', 'C',
                                'D', 'E', 'F', 'G', 'H' ]
    
    def start_game(self):
        print("Lets play Sudoku!")
        print(" ")
        print("Choose the size of your puzzle. The size of the puzzle is the length of one row. Default size is 9.")
        print("Possible sizes: 4, 9, 16")
        print(" ")
        char_size = input("Enter the desired size of the puzzle: ")

        try:
            char_size = int(char_size)

        except:
            char_size = 9

        if char_size not in self.possible_sizes:
            char_size = 9

        self.size = char_size
        print(" ")
        print("Puzzle size will be " + str(char_size))

        print(" ")
        print("The difficulty of the puzzle ranges from 1-5, where 1 is the easiest and 5 is the most difficult. Default difficulty is 3")
        difficulty = input("Enter the desired difficulty of the puzzle: ")

        try:
            difficulty = int(difficulty)
        
        except:
            difficulty = 3
        
        if difficulty < 1:
            difficulty = 1

        if difficulty > 5:
            difficulty = 5

        print(" ")
        print("Puzzle difficulty will be " + str(difficulty))

        chars = self.possible_chars[0: char_size]

        self.generator = SudokuGenerator(chars, difficulty)

        puzzles = self.generator.generate_puzzle()

        unsolved_puzzle = puzzles[0]

        SudokuGenerator.print_puzzle(self.size, unsolved_puzzle)

        print("To check answer, copy paste the puzzle into a app like notebook and paste in the completed or partially completed puzzle")
        print("To see solution, type 'solution'")
        print("To give up, type 'end'")

        print("Enter the your solution here: ")


        return puzzles

    def run_game(self, first_time = True):

        if first_time:
            self.puzzles = self.start_game()

        player_solution = []

        print("Enter solution here: ")
        for i in range((self.size * 2) + 1):
            
            curr_line = input()
            if curr_line == "end":
                print("Game Over.")
                quit()
            
            if curr_line == "solution":
                SudokuGenerator.print_puzzle(self.size, self.puzzles[1])
                print("Game Over.")
                quit()
            
            if len(curr_line) != (self.size * 4) + 1:
                print("INVALID INPUT\n")
                self.run_game(False)

            if curr_line[0] == "-" or curr_line[0] == " ":
                continue

            proper_vals = []
            curr_index = 0
            for char in curr_line:
                try:
                    if curr_line[curr_index: curr_index + 3] == '   ':
                        proper_vals.append(None)

                    elif char in self.possible_chars:
                        proper_vals += char

                except:
                    if char in self.possible_chars:
                        proper_vals += char
                
                curr_index += 1
            player_solution.append(proper_vals)

        print("-------------------------------------------------------------------------")
        finished = self.check_solution(player_solution, self.puzzles[1])

        if finished:
            print("You did it!")
            quit()
    
        else:
            self.run_game(False)

        #print(player_solution)

    def check_solution(self, attempt, key):
        num_correct = 0
        curr_row = -1
        for row in attempt:
            if len(row) == 0:
                continue
            curr_row += 1
            curr_col = 0
            for val in row:
                if val == None:
                    curr_col += 1
                    continue
                else:
                    if val == key[curr_row][curr_col]:
                        attempt[curr_row][curr_col] = "\033[32m" + str(val)
                        curr_col += 1
                        num_correct += 1
                        continue

                    else:
                        attempt[curr_row][curr_col] = "\033[31m" + str(val)
        
        SudokuGenerator.print_puzzle(self.size, attempt)

        return (num_correct == self.size * self.size)

