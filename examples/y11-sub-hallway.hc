// Year 11 - Sub Hallway

// For each two things in the
// INBOX, first subtract the 1st
// from the 2nd and put the
// result in the OUTBOX. And
// THEN, subtract the 2nd from
// the 1st and put the result in
// the OUTBOX. Repeat.

forever
	x = input
	y = input
	output y - x
	output x - y
