// This program tests use of the equality operator
// != to act as a logical xor operator.

// This file should read two values at a time from
// the inbox, and write them to the outbox only if
// exactly one of them is positive.

forever
	x = input
	y = input

	if y > 0 != x > 0
		output x
		output y
