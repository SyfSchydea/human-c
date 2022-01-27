// Year 19 - Countdown

// For each number in the INBOX,
// send that number to the
// OUTBOX, followed by all
// numbers down to (or up to)
// zero. It's a countdown!

forever
	x = input
	output x

	while x != 0
		if x > 0
			x -= 1
		else
			x += 1

		output x
