// This program tests for static evaluation of the
// logical not operator.

// It should function as an echo.

forever
	x = input

	if !(2 == 2)
		x = x * 2

	if !(2 > 9)
		output x
