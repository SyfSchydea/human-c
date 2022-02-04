// This file tests for invalid character literals.
// The lexer rule matches single quotes around any
// character, but it should report an error if the
// character is not an uppercase letter.

init '_' @ 0

output '_'
