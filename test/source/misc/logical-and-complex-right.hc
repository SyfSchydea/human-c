// This program aims to test for evaluation of the
// logical and operator using a more complex right
// operand which requires additional statements to
// be injected during compilation.

// This file should read values from the inbox and
// output it if and only if it is non-negative and
// the following two inputs sum to 0. Those inputs
// shouldn't be consumed if the original input was
// negative.

forever
	x = input

	if x >= 0 && input + input == 0
		output x
