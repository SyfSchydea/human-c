// This program tests for static evaluation of the
// logical or operator.

// The file should output each value in the inbox,
// multiplied by 10.

forever
	x = input

	if 0 == 1 || 1 == 0
		x = x * 3

	if 0 == 1 || 0 == 0
		x = x * 2

	if 0 == 0 || 0 == 1
		x = x * 5

	if 0 == 0 || 0 == 0
		output x
