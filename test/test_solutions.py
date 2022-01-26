#!/usr/bin/env python3

from common_test import AbstractTests

class TestYear1(AbstractTests.TestValidProgram):
	source_path = "solutions/y1-mail-room.hc"

	def test_solution(self):
		inboxes = [
			[1, 2, 3],
			[0, 0, 0],
			[-999, 0, 999],
			[4, 8, 15],
			[16, 23, 42]
		]

		self.run_tests((l, l) for l in inboxes)

class TestYear2(AbstractTests.TestValidProgram):
	source_path = "solutions/y2-busy-mail-room.hc"

	def test_solution(self):
		inboxes = [
			[1, 2, 3],
			[],
			[*"BOOTSEQUENCE"],
			[*"LOADPROGRAM"],
			[*"AUTOEXEC"],
		]

		self.run_tests((l, l) for l in inboxes)

class TestYear3(AbstractTests.TestValidProgram):
	source_path = "solutions/y3-copy-floor.hc"

	initial_memory = [
		"U", "J", "X",
		"G", "B", "E",
	]

	def test_solution(self):
		self.run_program([], [*"BUG"])

class TestYear4(AbstractTests.TestValidProgram):
	source_path = "solutions/y4-scrambler-handler.hc"
	floor_size = 3

	def test_solution(self):
		self.run_tests([
			([1, 9, "P", "G", 2, 8], [9, 1, "G", "P", 8, 2]),
			([4, 9, "K", "X", 1, 8], [9, 4, "X", "K", 8, 1]),
			([2, 7, "Q", "Q", 1, 6], [7, 2, "Q", "Q", 6, 1]),
			([4, 5, "I", "T", 2, 6], [5, 4, "T", "I", 6, 2]),
			([1, 7, "B", "V", 1, 7], [7, 1, "V", "B", 7, 1]),
		])

class TestYear6(AbstractTests.TestValidProgram):
	source_path = "solutions/y6-rainy-summer.hc"
	floor_size = 3

	def test_solution(self):
		self.run_tests([
			([2, 2, 4, 0, -6, 9, 9, -5], [4,   4,  3,  4]),
			([8, 0, 1, 4, -4, 1, 0, -7], [8,   5, -3, -7]),
			([3, 5, 4, 0, -2, 3, 4, -2], [8,   4,  1,  2]),
			([6, 7, 9, 9, -7, 2, 6, -3], [13, 18, -5,  3]),
		])

class TestYear7(AbstractTests.TestValidProgram):
	source_path = "solutions/y7-zero-exterminator.hc"
	floor_size = 9

	def test_solution(self):
		self.run_tests([
			([8, 0, -1, "F", 0, 0,  3, 0], [8, -1, "F",  3]),
			([5, 0,  2, "E", 0, 0, -2, 0], [5,  2, "E", -2]),
			([8, 0,  0, "E", 0, 0,  4, 0], [8, "E", 4]),
			([5, 0,  5, "E", 0, 0,  0, 0], [5,  5, "E"]),
			([3, 0,  0, "D", 0, 0,  0, 0], [3, "D"]),
		])

	# The game's inboxes for this test are incredibly
	# formulaic, and allow for solutions which do not
	# work for arbitrary inboxes.
	# This function checks that the compiled solution
	# works for more complex inboxes.
	def test_extended(self):
		self.run_tests([
			([], []),
			([0, 0, 0, 0], []),
			([1, 2, 3, 4], [1, 2, 3, 4]),
			([0, 0,  2, "E", 0, 0, -2, 0], [2, "E", -2]),
			([5, 9,  2, "E", 0, 0, -2, 0], [5,  9,  2,  "E", -2]),
			([5, 0,  2,  0,  0, 0, -2, 0], [5,  2, -2]),
			([5, 0,  2, "E", 9, 0, -2, 0], [5,  2, "E",  9, -2]),
			([5, 0,  2, "E", 0, 9, -2, 0], [5,  2, "E",  9, -2]),
			([5, 0,  2, "E", 0, 0, -2, 9], [5,  2, "E", -2,  9]),
		])

class TestYear8(AbstractTests.TestValidProgram):
	source_path = "solutions/y8-tripler-room.hc"
	floor_size = 3

	def test_solution(self):
		self.run_tests([
			([6, -6, 3, 0], [18, -18,  9, 0]),
			([6, -1, 7, 0], [18,  -3, 21, 0]),
			([5, -3, 7, 0], [15,  -9, 21, 0]),
		])

	def test_extended(self):
		self.run_tests([
			([], []),
			([111, 222, 333], [333, 666, 999]),
			([-1, 0, 1], [-3, 0, 3]),
		])

class TestYear9(AbstractTests.TestValidProgram):
	source_path = "solutions/y9-zero-preservation-initiative.hc"
	floor_size = 9

	def test_solution(self):
		self.run_tests([
			([8, 0, -1, "F", 0, 0,  3, 0], [0] * 4),
			([5, 0,  2, "E", 0, 0, -2, 0], [0] * 4),
			([8, 0,  0, "E", 0, 0,  4, 0], [0] * 5),
			([5, 0,  5, "E", 0, 0,  0, 0], [0] * 5),
			([3, 0,  0, "D", 0, 0,  0, 0], [0] * 6),
		])

	def test_extended(self):
		self.run_tests([
			([], []),
			([0, 0, 0, 0], [0] * 4),
			([1, 2, 3, 4], []),
			([0, 0,  2, "E", 0, 0, -2, 0], [0] * 5),
			([5, 9,  2, "E", 0, 0, -2, 0], [0] * 3),
			([5, 0,  2,  0,  0, 0, -2, 0], [0] * 5),
			([5, 0,  2, "E", 9, 0, -2, 0], [0] * 3),
			([5, 0,  2, "E", 0, 9, -2, 0], [0] * 3),
			([5, 0,  2, "E", 0, 0, -2, 9], [0] * 3),
		])

class TestYear10(AbstractTests.TestValidProgram):
	source_path = "solutions/y10-octoplier-suite.hc"
	floor_size = 5

	def test_solution(self):
		self.run_tests([
			([3, -2, 6, 0], [24, -16, 48, 0]),
			([5, -2, 6, 0], [40, -16, 48, 0]),
			([6, -4, 1, 0], [48, -32,  8, 0]),
			([6, -4, 6, 0], [48, -32, 48, 0]),
		])

	def test_extended(self):
		self.run_tests([
			([], []),
			([0] * 4, [0] * 4),
			([-1, 0, 1], [-8, 0, 8]),
			([ 31,  81, 118,  37], [ 248,  648,  944,  296]),
			([-36, -48, -28, -89], [-288, -384, -224, -712]),
			([  8, -81, -53, -24], [  64, -648, -424, -192]),
		])

class TestYear11(AbstractTests.TestValidProgram):
	source_path = "solutions/y11-sub-hallway.hc"
	floor_size = 3

	def test_solution(self):
		self.run_tests([
			([3, 8, 7, 4, -8, -8, 4, -8], [5, -5, -3, 3, 0, 0, -12, 12]),
			([3, 6, 6, 3, -8, -8, 3, -8], [3, -3, -3, 3, 0, 0, -11, 11]),
			([1, 8, 6, 3, -2, -2, 8, -5], [7, -7, -3, 3, 0, 0, -13, 13]),
		])

	def test_extended(self):
		self.run_tests([
			([], []),
			([0, 5, 99, 0], [5, -5, -99, 99]),
			([5, 3, 8, -9, 4, 5, -6, -6], [-2, 2, -17, 17, 1, -1, 0, 0]),
		])

class TestYear12(AbstractTests.TestValidProgram):
	source_path = "solutions/y12-tetracontiplier.hc"
	floor_size = 5

	def test_solution(self):
		self.run_tests([
			([3, -7, 5, 0], [120, -280, 200, 0]),
			([1, -1, 5, 0], [ 40,  -40, 200, 0]),
			([5, -2, 7, 0], [200,  -80, 280, 0]),
		])

	def test_extended(self):
		self.run_tests([
			([], []),
			([0] * 4, [0] * 4),
			([ 22,  17,  23,   9], [ 880,  680,  920,  360]),
			([-19, -17,  -1, -12], [-760, -680,  -40, -480]),
			([  0,  10, -15,  16], [   0,  400, -600,  640]),
		])

class TestYear13(AbstractTests.TestValidProgram):
	source_path = "solutions/y13-equalization-room.hc"
	floor_size = 3

	def test_solution(self):
		self.run_tests([
			([4, 6, 6, 6,  6,  5, -7, -7], [   6,    -7]),
			([4, 5, 6, 6,  1,  4, -1, -1], [   6,    -1]),
			([3, 3, 8, 8,  2, -2, -5, -5], [3, 8,    -5]),
			([9, 1, 3, 3, -5, -5,  9,  9], [   3, -5, 9]),
		])

	def test_extended(self):
		self.run_tests([
			([                              ], [              ]),
			([12, 12,  7,  1                ], [12            ]),
			([12, 13,  6,  9,  1, 16, 13,  8], [              ]),
			([ 7,  7, 12, 12, 14, 14, 14, 14], [ 7, 12, 14, 14]),
			([ 6,  6, 15, 10,  7,  7,  5,  2], [ 6,      7    ]),
			([ 0, 14, 12,  0,  0,  0        ], [         0    ]),
			([ 8, -8, -1,  1                ], [              ]),
		])

class TestYear14(AbstractTests.TestValidProgram):
	source_path = "solutions/y14-maximization-room.hc"
	floor_size = 3

	def test_solution(self):
		self.run_tests([
			([7, 7, -8, -9, 8, 8,  0,  8], [7, -8, 8,  8]),
			([3, 6, -4, -4, 9, 9, -6, -2], [6, -4, 9, -2]),
			([5, 2, -5, -4, 1, 1, -2,  3], [5, -4, 1,  3]),
			([8, 1, -5, -6, 3, 3,  6,  4], [8, -5, 3,  6]),
		])

	def test_extended(self):
		self.run_tests([
			([], []),
			([ 4, 13], [13]),
			([ 4,  9,  3,  8], [9, 8]),
			([14, 11,  3, 13, 20, 19], [14, 13, 20]),
			([ 3,  3,  0,  9, 18, 15, 10,  8], [ 3,  9, 18, 10]),
			([14,  4, 11,  4, 12, 13,  7, 12], [14, 11, 13, 12]),
		])

class TestYear16(AbstractTests.TestValidProgram):
	source_path = "solutions/y16-absolute-positivity.hc"
	floor_size = 3

	def test_solution(self):
		self.run_tests([
			([4, -3,  6, 0, -8,  7, 1], [4, 3, 6, 0, 8, 7, 1]),
			([3, -9,  1, 0, -7,  6, 2], [3, 9, 1, 0, 7, 6, 2]),
			([1, -2, -9, 0, -9,  5, 9], [1, 2, 9, 0, 9, 5, 9]),
			([9, -2,  4, 0, -6, -8, 1], [9, 2, 4, 0, 6, 8, 1]),
		])

	def test_extended(self):
		self.run_tests([
			([], []),
			([8], [8]),
			([14,  11], [14, 11]),
			([ 3, -12, -11], [3, 12, 11]),
			([ 2, -12,   8,  13], [2, 12, 8, 13]),
			([-2, -10,  -3,  -9, -11], [2, 10, 3, 9, 11]),
			([ 9,   7,  -1,  13,  -1, -13], [9, 7, 1, 13, 1, 13]),
			([-1,  10,   3,  10,  10,   5, -12], [1, 10, 3, 10, 10, 5, 12]),
			([ 0,   0,   0, -13,   0,   0,   0], [0,  0, 0, 13,  0, 0,  0]),
		])

class TestYear17(AbstractTests.TestValidProgram):
	source_path = "solutions/y17-exclusive-lounge.hc"

	initial_memory = [
		None, None,
		None, None,
		0,    1,
	]

	def test_solution(self):
		self.run_tests([
			([-6,  1, -8,  2, -1,  5,  1, -4], [1, 1, 1, 1]),
			([ 7, -5, -1, -1,  7, -2,  1,  7], [1, 0, 1, 0]),
			([ 7,  2, -9, -4,  9,  9, -1, -2], [0, 0, 0, 0]),
			([ 5,  3,  4, -4, -9,  6, -9, -7], [0, 1, 1, 0]),
		])

if __name__ == "__main__":
	unittest.main()
