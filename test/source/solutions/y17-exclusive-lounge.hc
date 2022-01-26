// Year 17 - Exclusive Lounge

// For each TWO things in the
// INBOX:

// Send a 0 to the OUTBOX if they
// have the same sign. (Both
// positive or both negative.)

// Send a 1 to the OUTBOX if
// their signs are different.
// Repeat until the INBOX is
// empty.

init zero @ 4
init one @ 5

forever
	if input < 0
		if input < 0
			output zero
		else
			output one
	else
		if input < 0
			output one
		else
			output zero
