// Year 14 - Maximization Room

// Grab TWO things from the
// INBOX, and put only the
// BIGGER of the two in the
// OUTBOX. If they are equal, just
// pick either one. Repeat!

forever
	x = input
	y = input

	if y >= x
		output y
	else
		output x
