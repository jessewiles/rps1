# Rock, Paper, Scissors

This repo contains code for a quick implementation of a rock, paper, scissors console game.

## Usage

To try, run the following:

```
$ docker run -it -v $(pwd ):/src  python:3 python /src/main.py

Welcome to Rock, Paper, Scissors! What would you like to do?
1) Start a new game.
2) View old games.
3) Quit.

>>> 2

------ 2022-09-02T09:51:04.603669-04:00 ------

SCORE:
    blaise: 3
    CPU: 5

------ 2022-09-02T09:52:32.097583-04:00 ------

SCORE:
    billy: 1
    CPU: 2

------ 2022-09-02T14:43:37.855570-04:00 ------

SCORE:
    todd: 0
    jeff: 2

------ 2022-09-02T14:44:05.741183-04:00 ------

SCORE:
    christy: 1
    max: 1


Welcome to Rock, Paper, Scissors! What would you like to do?
1) Start a new game.
2) View old games.
3) Quit.

>>> 1
Enter a name for player 1: marie
Enter a name for player 2 or press Enter to play against the computer:

marie, enter one of the following:
1) rock
2) paper
3) scissors
>>>
rock beats scissors. CPU wins!

SCORE:
    marie: 0
    CPU: 1


What would you like to do now?
1) Start a new game.
2) Play this game again.
3) Quit.
>>> 3

Would you like to save this game? (y\n)
>>> y
Bye.
```
