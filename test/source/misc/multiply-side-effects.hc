// This tests that the multiplication of two dynamic
// values does not have side effects on its operands.

// Should take pairs of inputs, output their product,
// then echo the original values.

init 0 @ 15

forever
	x = input
	y = input
	output x * y
	output x
	output y
