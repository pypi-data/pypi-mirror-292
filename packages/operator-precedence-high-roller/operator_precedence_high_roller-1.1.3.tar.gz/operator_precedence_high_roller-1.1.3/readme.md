# Operator Precedence High Roller Package

This is a package for a discord bot. I call it High Roller as a play on its original use for TTRPG rolling, as well as a joking reference to gambling. Also recently I added a !gamble command to make the joke more literal.

Commands -

! is the general character to put before a discord message to be read by the bot.

Command => '!' [EXPR]
Command => '!gamble'
Command => [BET]
Command => '!' [RECALL]

EXPR => [EXPR] '+' [EXPR]
EXPR => [EXPR] '-' [EXPR]
EXPR => [EXPR] '\*' [EXPR]
EXPR => [EXPR] '/' [EXPR]
EXPR => '(' [EXPR] ')'
EXPR => [NUM]
EXPR => [ROLL]

ROLL => 'd' [NUM]
ROLL => 'e' [NUM]

NUM => [0..9]+

BET => 'odds'
BET => 'evens'

RECALL => 'h'
RECALL => 'h' '(' [NUM] ',' [ROLL] ')'

Version history -
1.1.1 - doesn't actually work
1.1.2 - everything except RECALL commands works
1.1.3 - now everything works like it should
