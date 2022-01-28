// This file should test while loops.

// The file should read each input and output each
// number down to 1 for each positive input.
// Zero and negative inputs will be ignored.

init one @ 1

forever
	x = input

	while x > 0
		output x
		x -= one
