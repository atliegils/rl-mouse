import learners
import agent

# select the agent here
def get_agent(game):
    """Modify this method to create the appropriate agent"""
    actions = ['left', 'forward', 'right']
    player = agent.DeterministicAgent(game, actions)
    w = game._cw
    h = game._ch
    for tx in range(w):
        for ty in range(h):
            for cx in range(w):
                for cy in range(h):
                    player.policy[(cx,cy,tx,ty)] = get_policy(cx,cy,tx,ty,w,h)

    return player

def get_policy(cx,cy,tx,ty,w,h):
    """Get the policy for the situation where the cheese is at [cx,cy],
    the trap is at [tx,ty], and the grid has width w and height h (all
    relative to the mouse)."""

    # put your own code for the policy here

    return 'forward'


# train the agent before evaluation, but not in this exercise
def train(player):
    return

# control over rewards for (finding cheese, entering a trap, walking)
# by default the rewards are scaled by [1, -1, -1]
def reward_profile(player):
    """The reward profile can be adjusted by changing the line below
    Hint: Flat learners sometimes require a little extra push --
    by punishing the learner every step it learns not to walk in circles"""
    player.adjust_rewards(2,3,1)

