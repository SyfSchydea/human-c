// This program tests for static evaluation of the
// less than operator.

// It should function as an echo program.

forever
	x = input

	if 5 < 2
		x = x * 2
	if 3 < 3
		x = x * 2

	if 3 < 7
		output x
