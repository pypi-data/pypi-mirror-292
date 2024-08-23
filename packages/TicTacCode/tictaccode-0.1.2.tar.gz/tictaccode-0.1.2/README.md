# Tic-Tac-Toe Library Documentation
## Installation
To install the Tic-Tac-Toe Library, use pip:

```Bash
pip install TicTacCode
```

## Usage - Functions
### Import
Import the Board class for creating a Tic-Tac-Toe board:

```Python
from TicTacCode.Board import Board
```

### Creating a Board
To create a new Tic-Tac-Toe board, use the **Board()** function with two arguments:

turn: A boolean indicating whose turn it is. True for X, False for O.

boardString (optional): A string representing the initial board state. If left empty, the starting position will be default.

Example:
```Python
from TicTacCode.Board import Board

# Create a new board with X to start
board = Board(True)

# Create a board with a specific initial state
board = Board(False, "X--/-O-/--X")
```

#### Board Representation
The boardString argument is a string of length 11, representing a 3x3 board. Each character represents a cell:

"X": A Cell X Occupies<br>
"O": A Cell O Occupies<br>
"-": Empty Cell<br>

At the end of each row, a forward-slash (/) would be added.

Example:<br>
X--/-O-/--X<br>
represents a board with:

| X |   |   |
|---|---|---|
|   | O |   |
|   |   | X |
### Printing The Board
To print the board that you just created, DO NOT use a print function! Instead, use the internal **printBoard()** function:

Example:
```python
from TicTacCode.Board import Board

#Creates New Board
board = Board(True, "XO-/OOX/-X-")

#Printing the Board (Incorrect)
print(board) #Output: <__main__.Board object at 0x000001E0B12F0B30>

#Printing the Board (Correct)
board.printBoard() 
"""
Output:
XO-
OOX
-X-
"""
```
### Printing the Board Sting (FEN)
To print the Board string, use the following function:<br>
The board string is also called FEN, the function **printFen()** prints the Fen:

Example:
```python
from TicTacCode.Board import Board

#Creates New Board
board = Board(True, "XO-/OOX/-X-")

#Printing the Fen
board.printFen() #Output: XO-/OOX/-X-
```
### Clear Entire Board and Clear Fen Board.
There needs to be a way to clear the board. But there isn't just one way, there's two!<br>
One is the **clearEntireBoard()** function. This clears the entire board.<br>
Another is the **clearFenBoard()** function. This resets the board to the original FEN you put in the **Board()** function.

Example:
```python
from TicTacCode.Board import Board

#Creates Two New Boards
entire = Board(True, "XO-/OOX/-X-")
fen = Board(True, "XO-/OOX/-X-")

#Clear Boards
entire.clearEntireBoard()
fen.clearFenBoard()

#Print Boards
entire.printFen() #Output: ---/---/---
fen.printFen() #Output: XO-/OOX/-X-
```
### Making A Move
A game of Tic-Tac-Toe without making moves is pointless, so we also have a **move()** function.<br>
The **move()** function has only one parameter, the 'moveNotation'.

The 'moveNotation' consists of 2 characters, 
the first one would be what symbol (X or O) 
to place on what square (1-9).<br>
An example would be X5, which means to place X on the 5th square.

The function would give errors if the following conditions are not met:
1. The 'moveNotation' must be 2 characters long.
2. The 'moveNotation' must be a string.
3. The first character of the 'moveNotation' must be 'X' or 'O'.
4. The second character of the 'moveNotation' must be an integer from 1 to 9. (Including 1 and 9)
5. The first character of the 'moveNotation' must be according to the turn, so if it is X to move, the move 'O9' would be invalid.
6. The second character of the 'moveNotation' must be an unoccupied square, so if the 5th square is occupied, the move 'X5' would be invalid.
7. The board must not be a terminal state (not a "game-over" state).

Example:
```python
from TicTacCode.Board import Board

#Creates New Board
board = Board(True)

#Makes Move
board.move('X5') #Putting X on the 5th square.

#Prints the Board FEN
board.printFen() #Output: ---/-X-/---
```
### Calculating Terminal State
> To every thing there is a season, and a time to every purpose under the heaven:<br>
> <div style="text-align: right;">-<em>King James Version</em>, Ecclesiastes 3:1</div>
There is a season to play the game. And there is also a season to end the game.
The function **terminalState()** determines if the game has reached an ending position.

The function outputs a boolean (True or False).  
If the game has ended, it will output True. If not, it would output False.

Example:
```python
from TicTacCode.Board import Board

#Creates New Board
board = Board(True, 'XXO/O-O/XX-')

#Makes Move
board.move('X5') #Putting X on the 5th square.

#Checks If Terminal State
print(board.terminalState()) #Output: True
```
### Getting The Result
Upon finishing a game, you would like to see the result, right?
How do we do it programmatically?

There is a function called **winner()**, which gets the winner.<br>
If the game is ongoing, it would return None. But if the game has ended, it would output one of three strings:
'X' for X winning, 'O' for O winning, and 'Draw' for a tie game.

Example:
```python
from TicTacCode.Board import Board

#Creates New Board
board = Board(True, 'XXO/O-O/XX-')

#Makes Move
board.move('X5') #Putting X on the 5th square.

#Checks If Terminal State
print(board.terminalState()) #Output: True

#Get Winner
print(board.winner()) #Output: X
```
### Getting the Legal Moves
It would be great if you could know the legal moves before moving.
Don't worry, I got that covered! With the **legalMoves()** function, you could get the legal moves in the current position.

There is one parameter for the function: 'side'. Just like the **Board()** function, you need to enter True or False for X or O.
The function would then get the possible moves that side could make and output a list of move notations. 
The function will throw an error if it is a terminal state.

Example:
```python
from TicTacCode.Board import Board

#Creates New Board
board = Board(True, 'XXO/O-O/XX-')

#Gets Legal Moves
print(board.legalMoves(True)) #Output: ['X5', 'X9']
```
### Undoing the Last Move
Regretting life choices for losing a game of Tic-Tac-Toe? I got the solution!<br>
The **undoMove()** solves your problems, you could undo the move you just made to make another one.

Example:
```python
from TicTacCode.Board import Board

#Creates New Board
board = Board(True, 'XXO/O-O/XX-')

#Makes Move
board.move('X9')

#Prints Fen
board.printFen() #Output: XXO/O-O/XXX

#Undo Move
board.undoMove()

#Prints Fen
board.printFen() #Output: XXO/O-O/XX-

#Makes Another Move
board.move('X5')

#Prints Fen
board.printFen() #Output: XXO/OXO/XX-
```
### Occupied
The **occupied()** function takes in a square number (1-9, including 1 and 9), and checks if the square is occupied. It returns True if the square is occupied. If not, it will return False.
```python
from TicTacCode.Board import Board

#Creates New Board
board = Board(True)

#Checks if the 5th Square is Occupied
print(board.occupied(5)) #Output: False
```
### Find Piece Positions
The **findPiecePositions()** function gets the squares each player occupies.
It has one parameter: 'piece'. You could input 'X', 'O', or '-' to get the squares the selected piece occupies. Note that '-' stands for unoccupied squares.

Example:
```python
from TicTacCode.Board import Board

#Creates New Board
board = Board(True, 'XXO/O-O/XX-')

#Gets Squares Occupied by X
print(board.findPiecePositions('X')) #Output: [1, 2, 7, 8]
```
### Get Row & Get Column
The **getRow()** and **getColumn()** gets the respective row or column you put in. There is a parameter to put in the row/column number and the output will be the contents of that row/column.

Example:
```python
from TicTacCode.Board import Board

#Creates New Board
board = Board(True, 'XXO/O-O/XX-')

#Get 1st Row
print(board.getRow(1)) #Output: ['X', 'X', 'O']

#Get 2nd Column
print(board.getColumn(2)) #Output: ['X', '-', 'X']
```
### Calculating the Position
This is a neat algorithm that I made that gets the best move in the position. Use the **calculatePosition()** function to calculate the best move in the position.<br>
This outputs a tuple with 2 items, the first one being the evaluation and the second one being the best move.<br>
Note that the evaluation would be either 1 -- representing that X is winning, 0 -- representing no advantage for either side, or -1 -- representing that O is winning.

Example:
```python
from TicTacCode.Board import Board

#Creates New Board
board = Board(True)

#Get Board Evaluation
print(board.calculatePosition()) #Output: (0, 'X1')
```
### Getting the Best Continuation
This neat algorithm is made by repeatedly calling the internal **__minimax()** function on the new board. Use the **bestContinuation()** function to calculate the best continuation.  
This outputs a list of moveNotations, which is the best moves for each side.

Example:
```python
from TicTacCode.Board import Board

#Creates New Board
board = Board(True)

#Get Best Continuation
print(board.bestContinuation())
#Output: ['X1', 'O5', 'X2', 'O3', 'X7', 'O4', 'X6', 'O8', 'X9']
```
## Usage - Variables
### MoveStack
This variable records all moves played.

Example:
```python
from TicTacCode.Board import Board

#Creates New Board
board = Board(True)

#Moves
board.move('X5')
board.move('O3')
board.move('X4')
board.move('O6')
board.move('X9')
board.move('O1')
board.move('X2')
board.move('O8')
board.move('X7')

#Get moveStack
print(board.moveStack)
#Output: ['X5', 'O3', 'X4', 'O6', 'X9', 'O1', 'X2', 'O8', 'X7']
```
### Mover
This variable contains the player that is currently allowed to make a move, True for X, False for O; None for none.

Example:
```python
from TicTacCode.Board import Board

#Creates New Board
board = Board(True)

#Move
board.move('X5')

#Get Mover
print(board.mover) #Output: False
```
### Fen
This variable contains the current FEN position.

Example:
```python
from TicTacCode.Board import Board

#Creates New Board
board = Board(True)

#Move
board.move('X5')

#Get Fen
print(board.fen) #Output: ---/-X-/---
```

## Updated Since: <br>
### Version 0.1.2; August 23, 2024
## Change Log
V0.0.2 - Fixed the issue with the **calculatePosition()** function.  
Allowed user to enter "pass" to pass the move to the opponent in the **move()** function.  
Added the **saveGame()** function.

V0.0.3 - Deleted the **saveGame()** function altogether.

V0.0.4 - Deleted the **datetime** library to not cause errors.

V0.1.0 - Updated Documentation.

V0.1.1 - Added the **bestContinuation()** function.  
Fixed the issue with the internal **__minimax()** function.

V0.1.2 - Troubleshooted the issues with the **fen** variable.  
Updated Documentation.