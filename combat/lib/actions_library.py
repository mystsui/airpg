ACTIONS = {
    # NEUTRAL actions
    "idle": {
        "time": 10,
        "type": "idle",
        "stamina_cost": 0,
        "result": None,
    },
    "reset": {
        "time": 20,
        "type": "reset",
        "stamina_cost": 0,
        "result": None,
    },
    "recover": {
        "time": 200,
        "type": "recover",
        "stamina_cost": 0,
        "result": None,
    },
    "off_balance": {
        "time": 30,
        "type": "off_balance",
        "stamina_cost": 0,
        "result": None,
    },

    # MOVEMENT actions
    "move_forward": {
        "time": 60,
        "type": "move_forward",
        "stamina_cost": 4,
        "result": None,
    },
    "move_backward": {
        "time": 60,
        "type": "move_backward",
        "stamina_cost": 4,
        "result": None,
    },
    "turn_around": {
        "time": 10,
        "type": "turn_around",
        "stamina_cost": 2,
        "result": None,
    },

    # DEFENSE actions
    "try_block": {
        "time": 20,
        "type": "try_block",
        "stamina_cost": 3,
        "result": None,
    },
    "blocking": {
        "time": 10,
        "type": "blocking",
        "stamina_cost": 1,
        "result": None,
    },
    "keep_blocking": {
        "time": 10,
        "type": "keep_blocking",
        "stamina_cost": 1,
        "result": None,
    },

    # EVASION actions
    "try_evade": {
        "time": 20,
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
        "time": 30,
        "type": "try_attack",
        "stamina_cost": 10,
        "result": None, # concealed or revealed
    },
    "release_attack": {
        "time": 20,
        "type": "release_attack",
        "stamina_cost": 0,
        "result": None, # hit, missed, blocked, evaded, breached
    },
    "stop_attack": {
        "time": 10,
        "type": "stop_attack",
        "stamina_cost": 2,
        "result": None,
    }
}