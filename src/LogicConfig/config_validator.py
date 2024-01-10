from assets.const.pokemon_data import POKE_BALLS_LIST


without_repeat_balls_list = [ball for ball in POKE_BALLS_LIST if ball != "repeat_ball"]

uncapt_M_default_balls = [ball for ball in without_repeat_balls_list if ball != "master_ball"]
M_default_balls = [ball for ball in POKE_BALLS_LIST if ball != "master_ball"]

uncapt_A_default_balls = uncapt_M_default_balls
A_default_balls = M_default_balls

uncapt_B_default_balls = [ball for ball in uncapt_A_default_balls
                          if ball not in ["types_ball", "stats_ball", "ultra_ball"]]
B_default_balls = [ball for ball in A_default_balls if ball not in ["types_ball", "stats_ball", "ultra_ball"]]

uncapt_C_default_balls = ["stone_ball", "poke_ball"]
C_default_balls = ["stone_ball", "poke_ball"]


config_validator = {
    # A config object to validate config.json. We opted for a python dict so we do not have to load a json file here

    "language": {
        "default": "pt-br",
        "validator": {"type": "str", "accepted_values": ["pt-br", "es-la", "en-us"]}
    },
    "channel": {
        "default": "deemonrider",
        "validator": {"type": "str"}
    },
    "shop": {
        "poke_ball": {
            "buy_on_missing": {
                "default": True,
                "validator": {"type": "bool"}
            },
            "buy_one": {
                "default": 300,
                "validator": {"type": "int", "min": 300}
            },
            "buy_ten": {
                "default": 3000,
                "validator": {"type": "int", "min": 3000}
            },
        },
        "great_ball": {
            "buy_on_missing": {
                "default": True,
                "validator": {"type": "bool"}
            },
            "buy_one": {
                "default": 600,
                "validator": {"type": "int", "min": 600}
            },
            "buy_ten": {
                "default": 6000,
                "validator": {"type": "int", "min": 6000}
            },
        },
        "ultra_ball": {
            "buy_on_missing": {
                "default": True,
                "validator": {"type": "bool"}
            },
            "buy_one": {
                "default": 1000,
                "validator": {"type": "int", "min": 1000}
            },
            "buy_ten": {
                "default": 10000,
                "validator": {"type": "int", "min": 10000}
            },
        },
    },
    "catch": {
        "uncapt_S": {
            "default": without_repeat_balls_list,
            "validator": {"type": "str_list", "accepted_values": without_repeat_balls_list}
        },
        "S": {
            "default": POKE_BALLS_LIST,
            "validator": {"type": "str_list", "accepted_values": POKE_BALLS_LIST}
        },
        "uncapt_M": {
            "default": uncapt_M_default_balls,
            "validator": {"type": "str_list", "accepted_values": without_repeat_balls_list}
        },
        "M": {
            "default": M_default_balls,
            "validator": {"type": "str_list", "accepted_values": POKE_BALLS_LIST}
        },
        "uncapt_A": {
            "default": uncapt_A_default_balls,
            "validator": {"type": "str_list", "accepted_values": without_repeat_balls_list}
        },
        "A": {
            "default": A_default_balls,
            "validator": {"type": "str_list", "accepted_values": POKE_BALLS_LIST}
        },
        "uncapt_B": {
            "default": uncapt_B_default_balls,
            "validator": {"type": "str_list", "accepted_values": without_repeat_balls_list}
        },
        "B": {
            "default": B_default_balls,
            "validator": {"type": "str_list", "accepted_values": POKE_BALLS_LIST}
        },
        "uncapt_C": {
            "default": uncapt_C_default_balls,
            "validator": {"type": "str_list", "accepted_values": without_repeat_balls_list}
        },
        "C": {
            "default": C_default_balls,
            "validator": {"type": "str_list", "accepted_values": POKE_BALLS_LIST}
        },
    },
    "stats_balls": {
        "heavy_ball": {
            "default": 200,
            "validator": {"type": "int", "min": 100}
        },
        "feather_ball": {
            "default": 50,
            "validator": {"type": "int", "min": 0, "max": 100}
        },
        "heal_ball": {
            "default": 150,
            "validator": {"type": "int", "min": 100}
        },
        "fast_ball": {
            "default": 150,
            "validator": {"type": "int", "min": 100}
        }
    }
}
