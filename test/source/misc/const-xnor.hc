// This program tests for static evaluation of the
// == operator being used as a logical xnor.

// The file should read each value from the inbox,
// and output double the value.

forever
	x = input

	if (0 == 1) == (1 == 0)
		x = x * 2

	if (0 == 1) == (0 == 0)
		x = x * 3

	if (0 == 0) == (1 == 0)
		x = x * 5

	if (0 == 0) == (0 == 0)
		output x
