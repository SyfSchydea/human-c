// Year 20 - Multiplication Workshop

// For each two things in the
// INBOX, multiply them, and
// OUTBOX the result. Don't
// worry about negative numbers
// for now.

init 0 @ 9

forever
	count = input
	x = input

	// Swap to ensure count <= x
	if count > x
		tmp = x
		x = count
		count = tmp

	product = 0
	while count > 0
		product += x
		count -= 1

	output product
