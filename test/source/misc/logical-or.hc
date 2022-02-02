// This file tests compilation of logical or.

// This file should read two values at a time from
// the inbox, and write them to the outbox only if
// at least one is positive.

forever
	x = input
	y = input

	if y > 0 || x > 0
		output x
		output y
