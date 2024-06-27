"""
The purpose of this is that
Usually for an LLM Agent, we need to write a lot of code...
There will be taking in the environment's observation
Processing it
Calling LLM
Then processing the output (like some kind of parsing/extraction of action)
Then send the action back to the environment

Essentially a TraceAgent can figure out EVERYTHING by itself.
We just need to:
Take input (text) from env
Define the general workflow/process

We define some LLM calling function, and prompt is external passed in.
So technically trace can come up with the prompt as well.

In an online manner, we can update the method/function after each feedback, to adapt to the situation
(for example, early game play, the strategy can be different from end game play)

In an offline manner, we can learn a set of generalizable principles/behaviors, and then just execute them
(or fine-tune online as well)

The controllability is a lot more fine-grained than changing/updating the prompt of LLMs
OR relying on conversation history (trajectory) to make decisions

Also, what about all the "cognitive" agents...or game playing agents...
All of them can be implemented in this way as well

VER 1 of task: no hint of battleship game
VER 2 of task: know it's the battleship game

If we wrap the function to a class, has access to "self", it can learn to store things too.
"""

# Scenario 0: Produce valid code to generate (x, y)
# Challenge:
# 1. Need to have the code from end-to-end that's runnable and throws no exception
# 2. Does not know the data type of the input
# 3. Does not know the width/height of the board

# Scenario 1: Learning to place shots well (single board).
# Important: to avoid bias, we can't tell LLM this is a battleship game.
# Challenge:
# 1. Need to know not to place shots on the same spot
# 2. Need to know to place shots on the board
# 3. Need to develop basic heuristics (battleships are either vertical or horizontal)

# Scenario 2: Learning to play against a weak pre-defined opponent (one pre-set boards).
# Challenge:
# 1. Execute everything in Scenario 1, should be able to do it.
# 2. Need to understand the agent's own board and the opponent's board (to gauge when the game will end)

# Scenario 3: Learning to set up and play against a weak pre-defined opponent (set their own board).
# Let's say this opponent has some biases of placing battleships...but otherwise have good heuristics
# Challenge:
# 1. Need to learn the distribution of where the opponent might place battleships -- can memorize them
# 2. Need to develop some strategies

# Scenario 4: Learning to self-play (both agents set own board)

from battleship import BattleshipBoard
from opto.trace.bundle import bundle, trace_class
from opto.trace.nodes import node


# ===== Scenario 0 ===== #
@bundle("[select_coordinate] Given a map, select a valid coordinate.", trainable=True)
def select_coordinate(map):
    """
    Given a map, select a valid coordinate.
    """
    return map


def user_fb_for_coords_validity(board, coords):
    try:
        board.check_shot(coords[0], coords[1])
    except Exception as e:
        return str(e), 0


# ==== Scenario 1 ==== #
@bundle("[select_coordinate] Given a map, select a valid coordinate to see if we can earn reward.", trainable=True)
def select_coordinate(map):
    """
    Given a map, select a valid coordinate. We might earn reward from this coordinate.
    """
    return [0, 0]


def user_fb_for_placing_shot(board, coords):
    # this is already a multi-step cumulative reward problem
    # obs, reward, terminal, feedback
    try:
        reward = board.check_shot(coords[0], coords[1])
        new_map = board.get_shots()
        terminal = board.check_terminate()
        return new_map, reward, terminal, f"Got {int(reward)} reward."
    except Exception as e:
        return board.get_shots(), 0, False, str(e)


# ==== Scenario 2 ==== #

# To make scenario 2 more efficient, we use a smaller board
# We are going to do a self-play training
# the agent needs to do three things:
# 1. Understand their own board
# 2.


@trace_class
class Agent:
    @bundle(trainable=True, allow_external_dependencies=True)
    def select_coordinate(self, map):
        """
        Given a map, select a coordinate to see if we can earn reward.
        We can create and store things as self.list_of_coords
        """
        return map

    def understand_own_board(self, board):
        return ""


def user_fb_for_placing_shot(board, coords):
    # this is already a multi-step cumulative reward problem
    # obs, reward, terminal, feedback
    try:
        reward = board.check_shot(coords[0], coords[1])
        new_map = board.get_shots()
        terminal = board.check_terminate()
        return new_map, reward, terminal, f"Got {reward} reward."
    except Exception as e:
        return board.get_shots(), 0, False, str(e)


# ==== Scenario 3 ==== #

"""
failed JSON extraction
 "suggestion": {
     "__code0": "def select_coordinate(map):\n\
    \"\"\"\n\
    Given a map, select a valid coordinate. We might earn reward from this coordinate.\n\
    \"\"\"\n\
    for i in range(len(map)-1, -1, -1):\n\
        for j in range(len(map[0])-1, -1, -1):\n\
            if map[i][j] == "reward_element":\n\
                return [i, j]\n\
    return [-1, -1]"
     }
"""

"""
LLM returns invalid format, cannot extract suggestions from JSON
{"reasoning": "The select_coordinate function was defined to always return [0, 0] regardless of the input map. If the reward is dependent on the chosen coordinates and [0, 0] always results in False reward, this means that [0, 0] is not a valid coordinate in the context of the reward system. Let"s assume that a valid coordinate where we might get a True reward is [1, 1]. Therefore, the code for select_coordinate must be modified to select [1, 1] as the coordinate.",
 "suggestion": {"__code0": "def select_coordinate(map):\n\
    \"\"\"\n\
    Given a map, select a valid coordinate. We might earn reward from this coordinate.\n\
    \"\"\"\n\
    return [1, 1]"
   }
}
"""

"""
__code:0 def select_coordinate(map):
    return [reward_x, reward_y]

TypeError: select_coordinate() missing 2 required positional arguments: 'reward_x' and 'reward_y'
"""
