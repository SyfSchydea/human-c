// This file tests compilation of logical not.

// This file should read two values at a time from
// the inbox, and output them only if they are not
// equal.

forever
	x = input
	y = input

	if !(y == x)
		output x
		output y
