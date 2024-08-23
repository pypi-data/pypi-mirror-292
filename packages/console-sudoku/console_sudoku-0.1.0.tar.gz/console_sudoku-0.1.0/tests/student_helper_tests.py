from unittest import TestCase
from src.sudoku.sudoku_solver import SudokuSolver

class SudokuSolverStudentTests(TestCase):
    def setUp(self) -> None:
        return super().setUp()


    def _assert_puzzle(self, result, answer):
        for i in range(len(answer)):
            for j in range(len(answer)):
                self.assertEqual(result[i][j],  answer[i][j])

    def test_student_helper_function_case_1(self): 
        solver = SudokuSolver(["A", "B", "C", "D"])
        check = 0
        self.assertEquals(solver.get_chunk(1, 1), check)

    def test_hardest_sudoku(self):
        puzzle = [["8", None, None, None, None, None, None, None, None],
                  [None, None, "3", "6", None, None, None, None, None],
                  [None, "7", None, None, "9", None, "2", None, None],
                  [None, "5", None, None, None, "7", None, None, None],
                  [None, None, None, None, "4", "5", "7", None, None],
                  [None, None, None, "1", None, None, None, "3", None],
                  [None, None, "1", None, None, None, None, "6", "8"],
                  [None, None, "8", "5", None, None, None, "1", None],
                  [None, "9", None, None, None, None, "4", None, None]]


        answer = [["8", "1", "2", "7", "5", "3", "6", "4", "9"],
                  ["9", "4", "3", "6", "8", "2", "1", "7", "5"],
                  ["6", "7", "5", "4", "9", "1", "2", "8", "3"],
                  ["1", "5", "4", "2", "3", "7", "8", "9", "6"],
                  ["3", "6", "9", "8", "4", "5", "7", "2", "1"],
                  ["2", "8", "7", "1", "6", "9", "5", "3", "4"],
                  ["5", "2", "1", "9", "7", "4", "3", "6", "8"],
                  ["4", "3", "8", "5", "2", "6", "9", "1", "7"],
                  ["7", "9", "6", "3", "1", "8", "4", "5", "2"]]

        solver = SudokuSolver(["1", "2", "3", "4", "5", "6", "7", "8", "9"])
        result = solver.solve(puzzle)
        self._assert_puzzle(result, answer)