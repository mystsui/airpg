ACTIONS = {
    # NEUTRAL actions
    "idle": {
        "time": 10,
        "type": "idle",
        "stamina_cost": 0,
        "result": None,
    },
    "reset": {
        "time": 1000,
        "type": "reset",
        "stamina_cost": 0,
        "result": None,
    },
    "recover": {
        "time": 2000,
        "type": "recover",
        "stamina_cost": 0,
        "result": None,
    },
    "off_balance": {
        "time": 800,
        "type": "off_balance",
        "stamina_cost": 0,
        "result": None,
    },

    # MOVEMENT actions
    "move_forward": {
        "time": 700,
        "type": "move_forward",
        "stamina_cost": 4,
        "result": None,
    },
    "move_backward": {
        "time": 700,
        "type": "move_backward",
        "stamina_cost": 4,
        "result": None,
    },
    "turn_around": {
        "time": 400,
        "type": "turn_around",
        "stamina_cost": 2,
        "result": None,
    },

    # DEFENSE actions
    "try_block": {
        "time": 200,
        "type": "try_block",
        "stamina_cost": 3,
        "result": None,
    },
    "blocking": {
        "time": 400,
        "type": "blocking",
        "stamina_cost": 1,
        "result": None,
    },
    "keep_blocking": {
        "time": 1,
        "type": "keep_blocking",
        "stamina_cost": 1,
        "result": None,
    },

    # EVASION actions
    "try_evade": {
        "time": 300,
        "type": "try_evade",
        "stamina_cost": 3,
        "result": None,
    },
    "evading": {
        "time": 10,
        "type": "evading",
        "stamina_cost": 1,
        "result": None,
    },

    # ATTACK actions
    "try_attack": {
        "time": 400,
        "type": "try_attack",
        "stamina_cost": 10,
        "result": None, # concealed or revealed
    },
    "release_attack": {
        "time": 300,
        "type": "release_attack",
        "stamina_cost": 0,
        "result": None, # hit, missed, blocked, evaded, breached
    },
    "stop_attack": {
        "time": 150,
        "type": "stop_attack",
        "stamina_cost": 2,
        "result": None,
    }
}