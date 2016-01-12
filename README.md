# Toolkit for Evaluating Agents and Learners

## Installation

TEAL requires Python 2.7+. Clone or download the git repository. In order to use the plotter, `bokeh` needs to be installed. The plotter can be disabled with the `--no_plot` switch (useful if you are unable to install `bokeh`). 

## Students (crafting a solution)

The solution to an exercise consists of three methods that need to be implemented.
These are the `get_agent`, `train` and `reward_profile` methods.

### `get_agent`
The `get_agent` method takes a `Game` as a parameter and should return an `Agent` (any subclass of `Agent` is fine). The returned `Agent` instance should be configured for the provided `Game`, and will be passed as a parameter into the `train` method.

### `train`
The `train` method takes an `agent` as a parameter and performs any necessary actions to train the agent to solve the given task. Once training is completed, exploration is turned off.

### `reward_profile`
The `reward_profile` method takes an `agent` as a parameter and adjusts the reward profile of that agent, generally with `adjust_rewards(args)`.
The reward profile is scaled by `[1, -1, -1]` during evaluations.

## Evaluating solutions
It's important to note that due to the stochastic policies of learners, a solution can yield different evaluation results between runs.

### Evaluating learning rate
In order to evaluate how fast a solution learns how to solve a given task environment, use the `--count_epochs` switch. This will train the agent and then evaluate it until end-conditions are met (max_epochs runs or early finish).

`usage: python2 bootstrapper.py <solution_name> --count_epochs [--max_epochs N] [--allow_early_finish] ...`

### Evaluating a single solution (obsolete)
To evaluate a single solution, run `bootstrapper.py` with the solution name as an argument and any optional arguments to configure the game. Usage instructions follow.

`usage: python2 bootstrapper.py <solution_name> [-g GRID_SIZE] [-f FOV] ...`

### Comparing two solutions (obsolete)
Two solutions can be evaluated and plotted on the same chart for comparison. Usage instructions follow.
`usage: python2 bootstrapper.py <solution_name> [-c OTHER_SOLUTION] [-g GRID_SIZE] [-f FOV] ...`
                       

# Documentation
Information about the reinforcement learners and the processes related to getting them to do things can be found below.

# Learners
`learners.py` contains five learners. The first is the `BaseLearner` which contains the core functionality of a learner.
The learners are the building blocks of game-playing agents.

## QLearn and SARSA 
`QLearn` and `SARSA` are separate implementations of learners. 
`SARSA` assumes that exploration remains on whereas `QLearn` optimizes for offline us (exploration turned off after training). 

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

# Other components

## Renderer
 
The renderer can be found in `render.py` and uses _pygame_ to render on the screen. Currently the `render` method takes a collection of items and a score. It renders the first three items a specific color and the score in the corner.
 
The renderer exists only for visualization and debugging purposes, and is not actually necessary. It can be disabled by providing `do_render=False` in the `Game()` constructor.

## Task + Environment

In this package, one game is implemented -- with three difficulty levels (essentially making it three different games).

The game consists of a mouse (the player, white), cheese (yellow) and a trap (red).
The aim of the game is to accumulate as much cheese as possible and avoid touching traps.
The world loops around itself.

If the difficulty is set to 0, there is no trap. At 1, the trap exists but is immobile. At 2, the trap randomly moves towards the player (acts like a cat).

A basic implementation of Pong is also included.

# Extending the provided agents for other games

The provided agents already do a lot of the heavy lifting in a generalized context. `Agent:get_fov(fov)` might need to be replaced, along with the `Agent:decide(learner)` method. The `decide` method is responsible for updating the selected action in non-chosen learners and the `get_fov` method generates a tuple based on the game state. See `agent.py`.

# Appendix
### The evaluation bootstrapper

#### Variables

##### Independent
- Grid size
- Field of view
- Alpha, Gamma (learning rate & discount factor)
- Reward profile

##### Dependent
- Learning time
- Target steps (dependent on grid size)
- Extra steps (dependent on agent)
- Other evaluation metrics (deaths, timeouts, performance...)

#### Arguments (for the evaluation software)
- Output file name
- Dephase (first train it to learn the opposite of the task)
- Solution (mandatory)
- Comparison solution
- Grid size
- Field of view base size
- Gamma (discount factor)
- Reward profile

