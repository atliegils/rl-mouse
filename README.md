# Toolkit for Evaluating Agents and Learners

## Getting started with exercise 1

TEAL allows you to evaluate agents in a game where the player controls a mouse in a grid-world. The score increases when the mouse walks into cheese (respawning the cheese elsewhere) and it decreases when the mouse walks into a trap. If the mouse walks into a trap, the mouse and items respawn at random locations.

The mouse game contains the actions 'left', 'right', 'forward' and the special action '?'. The '?' action selects a random action and should not be necessary to complete exercise 1.

## Installation

TEAL requires Python 2.7+. Clone or download the git repository. In order to use the plotter, `bokeh` needs to be installed. The plotter can be disabled with the `--no_plot` switch (useful if you are unable to install `bokeh`). 

## Students (crafting a solution)

The solution to an exercise consists of two methods that need to be implemented.
These are the `get_agent`, and `train` methods. See solutions/example.py.

### `get_agent`
The `get_agent` method takes an `Environment` as a parameter and should return an `Agent` (any subclass of `Agent` is fine). The returned `Agent` instance should be configured for the provided `Environment`, and will be passed as a parameter into the `train` method.

### `train`
The `train` method takes an `agent` as a parameter and performs any necessary actions to train the agent to solve the given task. Once training is completed, exploration is turned off.

## Evaluating solutions' learning rates
It's important to note that due to the stochastic policies of learners, a solution can yield different evaluation results between runs.

`usage: python2 teal.py <solution_name> [--grid_size N] [--max_epochs N]`

### Comparing two solutions (obsolete)
_Note: not ready_
Two solutions can be evaluated and plotted on the same chart for comparison. Usage instructions follow.
`usage: python2 teal.py <solution_name> [-c OTHER_SOLUTION] [-g GRID_SIZE] [-f FOV] ...`
                       

# Documentation
Information about the reinforcement learners and the processes related to getting them to do things can be found below.

# Learners
`learners.py` contains five learners. The first is the `BaseLearner` which contains the core functionality of a learner.
The learners are the building blocks of game-playing agents.

## QLearn and SARSA 
`QLearn` and `SARSA` are separate implementations of learners. 
`SARSA` assumes that exploration remains on whereas `QLearn` optimizes for offline use (exploration turned off after training). 

### QPLearn
This is a QLearning agent that always selects based on the probability of each action -- it's therefore not guaranteed to follow its own policy optimally. It uses a simple weighted-selection.

## HistoryManager
`learners.py` provides a learner that has a memory, called `HistoryManager`.
It is a learner that makes decisions based on information 'now' (at time step `t`) or 'the past' (time step `t-x` where `history_levels >= x > 0`.
The history manager rewards the decider for selecting which sub-learner to use as well as the sub learners themselves.
_Note: The HistoryManager has not been maintained actively for a long time and might not work properly, use at your own risk!_

## MetaLearner
The meta learner learns from two different sublearners of any kind. The meta learner learns to select the sublearner that yields the highest reward and trains all sublearners simultaneously (this doesn't apply to `HistoryManagers`, since their learning is based on decisions and not the game itself).

The meta learner can be configured to take either the state space for the left or the right learner for its own state space with the `side` property. There seems to be a trend for one-sided learners being slightly wores than double-sided learners.

# Agents

Although learners are generic, agents need to be specifically tailored to the game they are designed to play.
In brief, an agent will access the game's internals and manage learners. 
Agents should implement the `perform` method, which does the following:

1. Get the state of the game
2. Simplify the state, or put it into context
3. Set the learner state to the game state
4. Record a decision from the learner
5. Play the recorded decision
6. Check if the recorded action was good or bad (e.g. 'the score went up' is good)
7. Apply rewards to the learners based on the actions
8. Return the result of step (6.)

## Provided agents

Some of the provided agents are listed below.

### MouseAgent

This agent supplies the state of the cells in a forward 'cone' to the learner. This is the 'default' agent for the Mouse game.

### OmniscientMouseAgent

This agent supplies the state of every cell to the learner.

### DeterministicMouseAgent

Instead of acting as an interface between the game and a learner, it acts as an interface between the game and a policy.

### RadiusMouseAgent

This agent has a limited field of view extending out to a radius from it's position.

### TraceMouseAgent

The `TraceMouseAgent` is just an example of how to easily add debugging information for learners.

### WrapperMouseAgent

The `WrapperMouseAgent` just wraps a learner in an MouseAgent but with different default parameters to the `perform` function. The perform method will modify the state based on a method that can be overwritten, `modify_state`. This can be useful if the default state space needs to be transformed.

# Other components

## Renderer
 
The renderer can be found in `render.py` and uses _pygame_ to render on the screen. Currently the `render` method takes a collection of items and a score. It renders the first three items a specific color and the score in the corner.
 
The renderer exists only for visualization and debugging purposes, and is not actually necessary. It can be disabled by providing `do_render=False` in the `Environment`'s constructor.

## Task + Environment

In this package, one environment is implemented -- a game with three difficulty levels (essentially making it three different games).

The game consists of a mouse (the player, white), cheese (yellow) and a trap (red).
The aim of the game is to accumulate as much cheese as possible and avoid touching traps.
The world loops around itself.

If the difficulty is set to 0, there is no trap. At 1, the trap exists but is immobile. At 2, the trap randomly moves towards the player (acts like a cat).

A basic implementation of Pong is also included.

# Extending the provided agents for other games

The provided agents already do a lot of the heavy lifting in a generalized context. `Agent:get_fov(fov)` might need to be replaced, along with the `Agent:decide(learner)` method. The `decide` method is responsible for updating the selected action in non-chosen learners and the `get_fov` method generates a tuple based on the game state. See `agent.py`.

