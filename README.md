# Learners
`learners.py` contains four learners. The first is the `BaseLearner` which contains the core functionality of a learner.
The learners are the building blocks of game-playing agents.

## QLearn and SARSA 
`QLearn` and `SARSA` are separate implementations of learners. 
`SARSA` assumes that exploration remains on whereas `QLearn` optimizes for offline us (exploration turned off after training). 

## HistoryManager
`learners.py` provides a learner that has a memory, called `HistoryManager`.
It is a learner that makes decisions based on information 'now' (at time step `t`) or 'the past' (time step `t-x` where history_levels >= `x` > 0.
The history manager rewards the decider for selecting which sub-learner to use as well as the sub learners themselves.

## MetaLearner
The meta learner learns from two different sublearners of any kind. The meta learner learns to select the sublearner that yields the highest reward and trains all sublearners simultaneously (this doesn't apply to `HistoryManagers`, since their learning is based on decisions and not the game itself).

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

## extending the provided agents for other games

The provided agents already do a lot of the heavy lifting in a generalized context. `Agent:get_fov(fov)` might need to be replaced, along with the `Agent:decide(learner)` method. The `decide` method is responsible for updating the selected action in non-chosen learners and the `get_fov` method generates a tuple based on the game state.



