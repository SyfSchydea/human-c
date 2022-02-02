// This file tests expansion of nested subtraction
// operators.

forever
	x = input
	y = input
	z = input

	// x - y + z
	output x - (y - z)

	// x - y - z
	output x - (y + z)

	// x + y - z
	output x + (y - z)
