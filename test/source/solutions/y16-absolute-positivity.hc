// Year 16 - Absolute Positivity

// Send each thing from the
// INBOX to the OUTBOX. But, if
// a number is negative, first
// remove its negative sign.

forever
	x = input
	if x < 0
		x = -x
	output x
