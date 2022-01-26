// This file tests unary minus. This should expand
// from `-x` to `0 - x`, and then be treated as if
// it were a standard subtraction. This file tests
// both standard and constant compilation of unary
// minus.

// The file should echo first the negative of each
// value in the inbox, then the original value.

// eg. an inbox of 2, -3 should yield an outbox of
// -2, 2, 3, -3

forever
	x = input
	output -x
	if 2 > -2
		output x
