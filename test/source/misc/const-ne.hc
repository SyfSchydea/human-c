// This file contains a not equal operator with constant
// operands. It should result in the if statement to get
// skipped over every time.

// This file should consume all of the input, and output
// nothing.

forever
	x = input
	if 1 != 1
		output x
