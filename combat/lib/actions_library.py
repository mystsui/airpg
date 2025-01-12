ACTIONS = {
    "idle": { # idle can be chosen by the combatant when they want to do nothing. It is a way to time actions.
        "time": 30,
        "type": "idle",
        "stamina_cost": 0,
    },
    "reset": { # reset is an automatic action when the attack, blocking, or evading action ends. It is the action for the combatant to regain balance. It acts as a delay that the opponent can exploit.
        "time": 60,
        "type": "reset",
        "stamina_cost": 0,
    },
    "recover": { # recover can be chosen to regain stamina.
        "time": 100,
        "type": "recover",
        "stamina_cost": 0,
    },
    "attack": {
        "time": 300,
        "type": "attack",
        "stamina_cost": 10,
    },
    "move_forward": { # move_forward can be chosen to move towards the opponent. the distance that the combatant can move is dependent upon the combatant's mobility.
        "time": 100,
        "type": "move_forward",
        "stamina_cost": 4,
    },
    "move_backward": { # move_backward can be chosen to move away from the opponent. the distance that the combatant can move is dependent upon the combatant's mobility.
        "time": 100,
        "type": "move_backward",
        "stamina_cost": 4,
    },
    "try_evade": { # try_evade can be chosen to evade an attack. the success of the evade is dependent upon the combatant's timing of the attack. It is the preparation for the evading action.
        "time": 100,
        "type": "try_evade",
        "stamina_cost": 4,
    },
    "evading": { # evading is an automatic action when the try__evade action ends. the "time" for it is the duration of the evading action. Any attack during this period will miss. 1 is the starting value but it will be dependent upon the combatant's evading ability.
        "time": 1,
        "type": "evading",
        "stamina_cost": 1,
    },
    "try_block": { # try_block can be chosen to block an attack. the success of the block is dependent upon the combatant's timing of the attack. It is the preparation for the blocking action.
        "time": 100,
        "type": "try_block",
        "stamina_cost": 4,
    },
    "blocking": { # blocking is an automatic action when the try_block action ends. the "time" for it is the duration of the blocking action. Any attack during this period will be blocked. 1 is the starting value but it will be dependent upon the combatant's blocking ability.
        "time": 1,
        "type": "blocking",
        "stamina_cost": 1,
    },
    "off_balance": { # off_balance is an automatic action when the combatant's attack is blocked or evaded by the opponent. It is the time that the combatant is vulnerable to attacks.
        "time": 100,
        "type": "off_balance",
        "stamina_cost": 0,
    },
}