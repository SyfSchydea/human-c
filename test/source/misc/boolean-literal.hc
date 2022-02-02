// This file tests use of boolean literal keywords

// The file should act as an echo.

forever
	x = input

	if false
		x = 0

	if false || false
		x *= 2

	if false && true
		x *= 3

	if true
		output x
