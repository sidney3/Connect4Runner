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
|Player | 1          | Enumeration      |

Note: the side `Player1` always goes first.

## Messages

### MessageHeader

Each message sent will have a message header at its start. This consists of

### GameStart

| Field | Type | Description |
|:------|:-----|:------------|
| Type  | uint8 | Always 0. See MessageTypes Appendix |
| YourPlayer | Player | Your (as the recipient) assigned player |
| TimePerMove | uint32_t | Milliseconds that each side will get per move |
| NumMovesMade | uint8 | The total number of moves made so far in the game. This should be used to decode the next row... |
| MovesMade | uint8[] | A list of moves that have been made. Each integer n denotes the side to move placing a piece on the nth column, 0 indexed |


### MakeMove

| Field | Type | Description |
|:------|:-----|:-------|
| Type  | uint8 | Always 1. See MessageTypes Appendix |
| Row | uint8 | The row on which to place a piece   |

Note: this is a bidirectional message. The engine runner will send this to engines, and engines will have to send it back to describe what move they would like to make. 

## Notes on the protocol

### TimeRemaining

If an engine fails to respond with its move within `TimePerMove`, the game is forfeited.

### IllegalMessages

The engine runner has no tolerance for illegal messages / moves. For simplicity, any illegal move or unparseable message will immediately lead to a forfeit of the game.

## Appendix

### Player

| Value | Meaning |
|:------|:-----|
| '1'   | Player1 |
| '2'   | Player2 |

Note: for readability this is the ascii '1'.

### MessageTypes

We use the following integers to denote each message type

| MessageType | Integer |
|:------------|:------|
| StartGame   | 0     |
| MakeMove    | 1     |
