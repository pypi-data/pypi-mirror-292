from copy import deepcopy
from datetime import datetime
from typing import List
from math import sqrt
from copy import deepcopy

class SudokuSolver:

    # Constructor
    # ************************
    # cell_options param might look like ["W", "L", "F", "S", "T", "R", "N", "G", "P"]
    # The size of the grid will always be the length of cell_options  
    def __init__(self, cell_options:List[str]) -> None:
        self.options: List[str] = cell_options
        self.first = True
        self.chunk_size = int(sqrt(len(cell_options)))

    
    # solve
    # *************************
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

    # valid_options
    # *************************
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

    # best_order
    # *************************
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


    # get_chunk
    # *************************
    # gets the chunk number of the row and col
    def get_chunk(self, row, col) -> int:
        chunk_start_x = int((col // self.chunk_size) * self.chunk_size)
        chunk_start_y = int((row // self.chunk_size) * self.chunk_size)

        return int(chunk_start_y) + int(chunk_start_x / self.chunk_size)


