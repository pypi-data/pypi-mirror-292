from copy import deepcopy
from datetime import datetime
from typing import List
from math import sqrt
from copy import deepcopy
import random
from sudoku_solver import SudokuSolver

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


# g = Sudoku_Generator([1, 2, 3, 4, 5, 6, 7, 8, 9], 3)
# p = g.generate_puzzle()

# g.print_puzzle(p[0])
# print("_________________________________________")
# g.print_puzzle(p[1])