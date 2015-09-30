# Learners
`learners.py` contains four learners. The first is the `BaseLearner` which contains the core functionality of a learner. `QLearn` and `SARSA` are separate implementations of learners. `SARSA` assumes that exploration remains on whereas `QLearn` optimizes for offline us (exploration turned off after training). 
