from console_sudoku import sudoku_generator
from sudoku_generator import SudokuGenerator
from math import sqrt


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


r = SudokuRunner()
r.run_game()