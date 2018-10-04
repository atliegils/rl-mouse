import agent


# select the agent here
def get_agent(game):
    """Modify this method to create the appropriate agent"""
    assert game.width == game.height, 'not a square grid'
    actions = ['left', 'forward', 'right']
    player = agent.DeterministicMouseAgent(game, actions)
    w = game.width
    h = game.height
    for tx in range(w):
        for ty in range(h):
            for cx in range(w):
                for cy in range(h):
                    player.policy[(cx, cy, tx, ty)] = define_policy(cx, cy, tx, ty, w, h)

    return player


def define_policy(cx, cy, tx, ty, w, h):
    """Defines the policy for the situation where the cheese is at [cx,cy],
    the trap is at [tx,ty], and the grid has width w and height h (all
    relative to the mouse)."""

    # put your own code for the policy here

    # Check if cheese is closer to the right
    # And if there is a trap up close
    prefer_right = tx == w - 1 or (cx <= w / 2 and tx != 1)
    trap_in_front = ty == 1 and tx == 0

    if cy != 0:
        # Cheese is not horizontally aligned with mouse
        if not trap_in_front:
            return 'forward'

    if prefer_right:
        return 'right'
    else:
        return 'left'


# train the agent before evaluation, but not in this exercise
def train(player):
    return
