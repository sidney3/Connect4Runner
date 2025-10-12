# Connect4 Messaging Spec

The following describes the messaging conventions for connect4 we adopt

## Conventions

All encodings are done in little endian (host byte ordering). Basically, if you cast whatever bytes you receive to the target type, it should just work...

## DataTypes

We will use the following types:

| Name | Size (bytes) | Description |
|:-----|:-------------|-------------|
|uint8 | 1          | Unsigned integer |
|uint32| 4          | Unsigned integer |
|Color | 1          | Enumeration      |

Note: the side `Red` always goes first.

## Messages

### MessageHeader

Each message sent will have a message header at its start. This consists of

### GameStart

| Field | Type | Description |
|:------|:-----|:------------|
| Type  | uint8 | Always 0. See MessageTypes Appendix |
|:------|:-------|:--------------|
| YourColor | Color | Your (as the recipient) assigned color |
|:------|:-------|:--------------|
| TimePerSide | uint32_t | Milliseconds that each side will get |
|:------|:-------|:--------------|
| NumMovesMade | uint8 | The total number of moves made so far in the game. This should be used to decode the next row... |
|:-----|:--------|:-----------|
| MovesMade | uint8[] | A list of moves that have been made. Each integer n denotes the side to move placing a piece on the nth column, 0 indexed |
|:-----|:-------|:----------|

Total size = 6 + NumMovesMade 

Example message:

(MessageType = 0, NumMovesMade = 4, Moves = [0, 1, 2, 3])

This would represent a game where `Red` put a piece in the first column, `Yellow` put a piece in the second column, etc...

### MakeMove

| Field | Type | Description |
|:------|:-----|:------------|
| Type  | uint8 | Always 1. See MessageTypes Appendix |
|:------|:-------|:--------------|
| Row | uint8 | The row on which to place a piece   |
|:-----|:--------|:-----------|
| RedTimeRemaining | uint32 | The milliseconds that the red side has left |
|:----|:----|:---|
| YellowTimeRemaining | uint32 | The milliseconds that the yellow side has left |
|:----|:----|:---|

Total size = 10 bytes

Note: for simplicity, this is a bidirectional message. The engine runner will send this to engines, and engines will have to send it back to describe what move they would like to make. 

Only when the engine runner includes times remaining do they mean anything - the game runner will ignore whatever the engines put for "time remaining" and only look at the requested move. 

## Notes on the protocol

### TimeRemaining

The engine runner will keep a "clock" for each engine. Each `MakeMove` message will contain updates about this time remaining. If either side gets to 0 milliseconds remaining, they will lose. Each move, your time gets subtracted by the amount of time it takes you to respond to the runner's message. This gets instituted to prevent engines from thinking forever. 

### IllegalMessages

The engine runner has no tolerance for illegal messages / moves. For simplicity, any illegal move or unparseable message will immediately lead to a forfeit of the game.

## Appendix

### Color

| Value | Meaning |
|:------|:--------|
| 'R'   | Red     |
|:------|:--------|
| 'Y'   | Yellow  |
|:------|:--------|

### MessageTypes

We use the following integers to denote each message type

| MessageType | Integer |
|:------------|:--------|
| StartGame   | 0     |
|:------------|:------|
| MakeMove    | 1     |
|:------------|:------|
