from unittest import TestCase
from src.sudoku.sudoku_solver import SudokuSolver
import cProfile, pstats, io
from pstats import SortKey

class SudokuSolverTests(TestCase):
    def setUp(self) -> None:
        return super().setUp()

    def _assert_puzzle(self, result, answer):
        for i in range(len(answer)):
            for j in range(len(answer)):
                self.assertEqual(result[i][j],  answer[i][j])

    def test_easy_4x4(self):
        puzzle = [["A", "B", "C", "D"],
                 ["C", None, "A", "B"],
                 ["B", "A", "D", None],
                 ["D", None, "B", "A"]]

        answer = [["A", "B", "C", "D"],
                 ["C", "D", "A", "B"],
                 ["B", "A", "D", "C"],
                 ["D", "C", "B", "A"]]

        solver = SudokuSolver(["A", "B", "C", "D"])
        result = solver.solve(puzzle)
        self._assert_puzzle(result, answer)

    def test_hard_4x4(self):
        puzzle = [[None, "B", None, None],
                 ["C", None, None, "B"],
                 [None, "A", "D", None],
                 ["D", None, None, "A"]]

        answer = [["A", "B", "C", "D"],
                 ["C", "D", "A", "B"],
                 ["B", "A", "D", "C"],
                 ["D", "C", "B", "A"]]

        solver = SudokuSolver(["A", "B", "C", "D"])
        result = solver.solve(puzzle)
        self._assert_puzzle(result, answer)
    
    def test_easy_9x9(self):
        puzzle = [["N","F","G","R","P","W","L","T","S"],
             ["L","W","S","N","T","F","R","P","G"],
             ["P","T","R","S","G","L","F","N","W"],
             ["T","S","W","F","R","G","N","L","P"],
             ["R","G","P","L","N","S","T","W","F"],
             ["F","L","N","T","W","P","S","G","R"],
             ["G",None,None,None,"L","T","P",None,None],
             [None,None,None,"P",None,None,None,"F","L"],
             [None,"P","L",None,None,None,"W",None,"T"]]

        answer = [['N', 'F', 'G', 'R', 'P', 'W', 'L', 'T', 'S'], 
            ['L', 'W', 'S', 'N', 'T', 'F', 'R', 'P', 'G'], 
            ['P', 'T', 'R', 'S', 'G', 'L', 'F', 'N', 'W'], 
            ['T', 'S', 'W', 'F', 'R', 'G', 'N', 'L', 'P'], 
            ['R', 'G', 'P', 'L', 'N', 'S', 'T', 'W', 'F'], 
            ['F', 'L', 'N', 'T', 'W', 'P', 'S', 'G', 'R'], 
            ['G', 'R', 'F', 'W', 'L', 'T', 'P', 'S', 'N'], 
            ['W', 'N', 'T', 'P', 'S', 'R', 'G', 'F', 'L'], 
            ['S', 'P', 'L', 'G', 'F', 'N', 'W', 'R', 'T']]
        solver = SudokuSolver(["W", "L", "F", "S", "T", "R", "N", "G", "P"])
        result = solver.solve(puzzle)
        self._assert_puzzle(result, answer)

    def test_medium_9x9(self):
        puzzle = [["N",None,"G",None,None,None,"L","T",None],
             ["L","W",None,None,None,"F",None,None,None],
             [None,None,"R","S","G",None,None,None,"W"],
             ["T","S",None,"F",None,None,"N","L",None],
             [None,None,None,"L","N","S",None,None,None],
             [None,"L","N",None,None,"P",None,"G","R"],
             ["G",None,None,None,"L","T","P",None,None],
             [None,None,None,"P",None,None,None,"F","L"],
             [None,"P","L",None,None,None,"W",None,"T"]]

        answer = [['N', 'F', 'G', 'R', 'P', 'W', 'L', 'T', 'S'], 
            ['L', 'W', 'S', 'N', 'T', 'F', 'R', 'P', 'G'], 
            ['P', 'T', 'R', 'S', 'G', 'L', 'F', 'N', 'W'], 
            ['T', 'S', 'W', 'F', 'R', 'G', 'N', 'L', 'P'], 
            ['R', 'G', 'P', 'L', 'N', 'S', 'T', 'W', 'F'], 
            ['F', 'L', 'N', 'T', 'W', 'P', 'S', 'G', 'R'], 
            ['G', 'R', 'F', 'W', 'L', 'T', 'P', 'S', 'N'], 
            ['W', 'N', 'T', 'P', 'S', 'R', 'G', 'F', 'L'], 
            ['S', 'P', 'L', 'G', 'F', 'N', 'W', 'R', 'T']]

        solver = SudokuSolver(["W", "L", "F", "S", "T", "R", "N", "G", "P"])
        result = solver.solve(puzzle)
        self._assert_puzzle(result, answer)

    def test_hard_9x9(self):
        answer = [['W', 'G', 'N', 'F', 'T', 'S', 'P', 'R', 'L'], 
            ['F', 'R', 'S', 'W', 'L', 'P', 'T', 'N', 'G'], 
            ['L', 'P', 'T', 'G', 'N', 'R', 'F', 'S', 'W'], 
            ['S', 'T', 'F', 'R', 'P', 'L', 'W', 'G', 'N'], 
            ['R', 'W', 'G', 'N', 'F', 'T', 'S', 'L', 'P'], 
            ['P', 'N', 'L', 'S', 'G', 'W', 'R', 'F', 'T'], 
            ['T', 'F', 'P', 'L', 'S', 'G', 'N', 'W', 'R'], 
            ['N', 'L', 'R', 'T', 'W', 'F', 'G', 'P', 'S'], 
            ['G', 'S', 'W', 'P', 'R', 'N', 'L', 'T', 'F']]

        puzzle = [[None,None,"N","F",None,None,None,"R","L"],
            [None,"R","S",None,"L",None,None,None,"G"],
            [None,None,None,None,None,None,None,None,"W"],
            [None,"T","F","R",None,None,None,None,None],
            [None,None,"G",None,"F",None,"S",None,None],
            [None,None,None,None,None,"W","R","F",None],
            ["T",None,None,None,None,None,None,None,None],
            ["N",None,None,None,"W",None,"G","P",None],
            ["G","S",None,None,None,"N","L",None,None]]
        solver = SudokuSolver(["W", "L", "F", "S", "T", "R", "N", "G", "P"])
        result = solver.solve(puzzle)
        self._assert_puzzle(result, answer)

    def test_expert_9x9(self):
        answer = [['S', 'G', 'F', 'L', 'W', 'P', 'N', 'T', 'R'], 
            ['R', 'W', 'T', 'S', 'F', 'N', 'L', 'G', 'P'], 
            ['P', 'N', 'L', 'T', 'R', 'G', 'W', 'S', 'F'], 
            ['T', 'L', 'G', 'W', 'P', 'S', 'R', 'F', 'N'], 
            ['N', 'F', 'R', 'G', 'L', 'T', 'S', 'P', 'W'], 
            ['W', 'S', 'P', 'F', 'N', 'R', 'G', 'L', 'T'], 
            ['F', 'R', 'N', 'P', 'G', 'L', 'T', 'W', 'S'], 
            ['G', 'P', 'S', 'N', 'T', 'W', 'F', 'R', 'L'], 
            ['L', 'T', 'W', 'R', 'S', 'F', 'P', 'N', 'G']]

        puzzle = [["S","G","F",None,None,None,None,"T",None],
            [None,None,None,"S",None,None,None,None,None],
            [None,None,None,"T",None,"G","W",None,"F"],
            ["T","L",None,None,None,"S","R",None,None],
            [None,None,None,None,"L",None,None,None,None],
            [None,None,"P","F",None,None,None,"L","T"],
            ["F",None,"N","P",None,"L",None,None,None],
            [None,None,None,None,None,"W",None,None,None],
            [None,"T",None,None,None,None,"P","N","G"]]
        solver = SudokuSolver(["W", "L", "F", "S", "T", "R", "N", "G", "P"])
        result = solver.solve(puzzle)
        self._assert_puzzle(result, answer)

    def test_16x16(self):
        
        pr = cProfile.Profile()
        pr.enable()
        answer = [['6', '2', 'A', 'C', 'G', '9', '8', '7', '3', '4', 'D', 'B', 'E', '1', '5', 'F'], 
            ['5', 'G', 'B', '8', '2', 'C', '1', '4', 'E', '9', '7', 'F', 'D', 'A', '3', '6'], 
            ['9', 'D', 'F', '7', '6', 'B', 'E', '3', '2', 'A', '1', '5', '8', 'G', '4', 'C'], 
            ['3', 'E', '4', '1', 'D', '5', 'A', 'F', '6', 'C', 'G', '8', '7', '2', '9', 'B'], 
            ['B', '3', 'E', '5', '4', 'F', '7', '6', '8', 'G', '9', 'C', '1', 'D', 'A', '2'], 
            ['F', 'A', '8', 'D', 'B', '3', '9', '5', '7', '1', '6', '2', '4', 'C', 'E', 'G'], 
            ['G', '9', '2', '4', 'C', '1', 'D', 'A', '5', '3', 'F', 'E', '6', '7', 'B', '8'], 
            ['C', '1', '7', '6', '8', 'E', 'G', '2', 'D', 'B', '4', 'A', '5', '3', 'F', '9'], 
            ['E', '5', '6', 'B', '7', 'G', 'C', '9', 'F', '2', 'A', '1', '3', '4', '8', 'D'], 
            ['4', '7', 'G', 'F', 'A', '8', '6', 'E', 'B', '5', '3', 'D', 'C', '9', '2', '1'], 
            ['A', 'C', '1', '9', '3', 'D', '2', 'B', 'G', 'E', '8', '4', 'F', '5', '6', '7'], 
            ['D', '8', '3', '2', 'F', '4', '5', '1', '9', '6', 'C', '7', 'B', 'E', 'G', 'A'], 
            ['7', 'F', 'D', '3', '5', '2', 'B', 'C', 'A', '8', 'E', 'G', '9', '6', '1', '4'], 
            ['2', '6', '5', 'A', 'E', '7', '4', 'D', '1', 'F', 'B', '9', 'G', '8', 'C', '3'], 
            ['1', 'B', 'C', 'G', '9', 'A', '3', '8', '4', 'D', '5', '6', '2', 'F', '7', 'E'], 
            ['8', '4', '9', 'E', '1', '6', 'F', 'G', 'C', '7', '2', '3', 'A', 'B', 'D', '5']]
        puzzle = [["6", "2", "A", None, "G", None, None, None, None, "4", None, "B", None, None, None, None],
            [None, "G", "B", "8", None, None, None, None, None, None, None, "F", None, None, None, None],
            ["9", "D", "F", None, None, None, "E", "3", "2", None, None, None, None, None, "4", "C"],
            [None, None, "4", None, "D", "5", "A", "F", "6", None, "G", "8", "7", None, "9", None],
            ["B", None, None, "5", None, None, "7", None, None, "G", "9", None, "1", None, "A", None],
            [None, None, "8", None, "B", "3", "9", "5", "7", None, None, "2", "4", None, None, "G"],
            ["G", None, None, "4", None, "1", "D", None, None, None, None, None, "6", None, None, "8"],
            ["C", None, "7", "6", "8", None, "G", "2", None, "B", None, None, None, "3", None, None],
            ["E", None, None, None, None, None, None, "9", None, None, "A", None, None, None, "8", "D"],
            ["4", "7", "G", None, None, None, None, "E", "B", None, None, "D", None, "9", None, None],
            ["A", "C", "1", "9", None, None, "2", "B", "G", None, None, None, None, "5", "6", None],
            [None, None, None, "2", "F", "4", None, None, "9", "6", None, None, None, None, None, "A"],
            [None, None, None, "3", None, None, None, "C", None, "8", "E", "G", "9", None, None, None],
            [None, "6", None, None, None, "7", None, None, "1", None, None, "9", "G", None, "C", None],
            ["1", "B", None, None, None, "A", "3", "8", None, "D", "5", "6", "2", None, None, None],
            ["8", "4", "9", "E", "1", "6", None, None, None, None, "2", "3", None, "B", None, None]]

        solver = SudokuSolver(["A", "B", "C", "D", "E", "F", "G", "1", "2", "3", "4", "5", "6", "7", "8", "9"])
        result = solver.solve(puzzle)

        pr.disable()
        s = io.StringIO()
        sortby = SortKey.CUMULATIVE
        ps = pstats.Stats(pr, stream=s).sort_stats(sortby)
        ps.print_stats()
        print(s.getvalue())

        self._assert_puzzle(result, answer)
    
    # Want a challenge?  Uncomment this test out and see how your solutions works.  It can be solved
    # 2 = 10 minutes to complete for more efficient algorithms.
    def test_16x16_advanced(self):
         
         pr = cProfile.Profile()
         pr.enable()
         answer = [['5', 'B', 'C', '2', '7', '9', '1', '3', '4', '6', '8', 'E', 'A', 'D', 'F', 'G'], 
             ['4', 'G', '3', '9', '2', '5', 'F', '6', '7', 'A', 'C', 'D', '1', 'B', '8', 'E'], 
             ['F', '6', 'A', '7', 'D', 'B', 'E', '8', '2', 'G', '5', '1', '4', '3', '9', 'C'], 
             ['D', '1', 'E', '8', '4', 'A', 'C', 'G', 'B', '9', 'F', '3', '6', '7', '5', '2'], 
             ['A', 'C', 'B', '3', 'F', 'G', 'D', '1', '6', '2', '4', '9', '8', '5', 'E', '7'], 
             ['E', '9', 'G', '6', 'C', '2', 'B', 'A', 'D', '5', '7', '8', 'F', '1', '4', '3'], 
             ['8', '7', 'D', '5', '9', '4', '3', 'E', 'F', 'B', '1', 'G', '2', 'C', '6', 'A'], 
             ['1', '4', '2', 'F', '5', '6', '8', '7', '3', 'E', 'A', 'C', 'D', 'G', 'B', '9'], 
             ['G', 'E', '7', 'C', 'A', '3', '5', 'B', '1', '8', '2', '4', '9', '6', 'D', 'F'], 
             ['3', 'A', '9', 'D', '6', '1', 'G', '4', 'E', 'C', 'B', 'F', '5', '2', '7', '8'], 
             ['B', '8', '5', '4', 'E', '7', '2', 'F', 'G', 'D', '9', '6', '3', 'A', 'C', '1'], 
             ['2', 'F', '6', '1', '8', 'C', '9', 'D', '5', '7', '3', 'A', 'B', 'E', 'G', '4'], 
             ['6', '2', '1', 'B', 'G', 'E', '4', '9', '8', '3', 'D', '7', 'C', 'F', 'A', '5'], 
             ['7', '5', 'F', 'G', '1', '8', 'A', '2', 'C', '4', '6', 'B', 'E', '9', '3', 'D'], 
             ['9', 'D', '4', 'E', '3', 'F', '6', 'C', 'A', '1', 'G', '5', '7', '8', '2', 'B'], 
             ['C', '3', '8', 'A', 'B', 'D', '7', '5', '9', 'F', 'E', '2', 'G', '4', '1', '6']]
    
         puzzle = [["5", None, None, "2", "7", None, "1", None, None, "6", None, None, None, None, None, None],
             [None, "G", None, None, None, None, "F", "6", None, "A", None, None, None, "B", None, "E"],
             ["F", "6", None, None, "D", None, None, None, None, None, "5", None, None, "3", None, None],
             ["D", None, None, "8", None, "A", "C", None, None, "9", None, "3", None, None, "5", None],
             [None, None, "B", "3", "F", None, None, None, None, None, "4", None, "8", None, "E", "7"],
             ["E", None, None, None, "C", "2", "B", None, "D", None, None, None, "F", None, None, None],
             [None, "7", None, None, None, None, None, None, None, None, "1", None, None, "C", None, None],
             [None, "4", "2", None, "5", None, None, None, "3", "E", "A", "C", None, None, None, "9"],
             [None, "E", "7", "C", None, None, None, "B", None, None, None, None, None, "6", None, "F"],
             [None, "A", None, None, None, "1", "G", "4", None, None, None, None, None, "2", "7", None],
             ["B", None, "5", "4", "E", None, None, None, None, "D", None, "6", None, None, None, "1"],
             [None, "F", None, "1", "8", None, "9", None, None, "7", None, None, "B", None, None, "4"],
             [None, None, None, None, "G", None, "4", None, None, "3", None, "7", None, None, "A", None],
             [None, "5", None, None, None, "8", None, "2", "C", "4", None, None, "E", None, None, None],
             ["9", None, "4", None, None, None, None, "C", None, "1", None, "5", None, "8", None, None],
             [None, None, None, "A", "B", "D", "7", None, "9", None, None, None, None, "4", None, "6"]]
         solver = SudokuSolver(["A", "B", "C", "D", "E", "F", "G", "1", "2", "3", "4", "5", "6", "7", "8", "9"])
         result = solver.solve(puzzle)

         pr.disable()
         s = io.StringIO()
         sortby = SortKey.CUMULATIVE
         ps = pstats.Stats(pr, stream=s).sort_stats(sortby)
         ps.print_stats()
         print(s.getvalue())

         self._assert_puzzle(result, answer)
