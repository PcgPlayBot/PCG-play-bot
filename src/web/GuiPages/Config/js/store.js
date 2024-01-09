// Redux Actions
const ACTIONS = {
    SET_CONFIG: "SET_CONFIG",
}

const setConfig = (config) => ({
    type: ACTIONS.SET_CONFIG,
    payload: config,
});


// Initial state
const initialState = {
    config: {
        "language": "pt-br",
        "channel": "",
        "shop": {
            "poke_ball": {
                "buy_on_missing": true,
                "buy_one": 300,
                "buy_ten": 3000
            },
            "great_ball": {
                "buy_on_missing": true,
                "buy_one": 600,
                "buy_ten": 6000
            },
            "ultra_ball": {
                "buy_on_missing": true,
                "buy_one": 1000,
                "buy_ten": 10000
            }
        },
        "catch": {
            "uncapt_S": [],
            "S": [],
            "uncapt_M": [],
            "M": [],
            "uncapt_A": [],
            "A": [],
            "uncapt_B": [],
            "B": [],
            "uncapt_C": [],
            "C": []
        },
        "stats_balls": {
            "heavy_ball": 150,
            "feather_ball": 75,
            "heal_ball": 150,
            "fast_ball": 150
        }
    }
}


// Redux reducer
const counterReducer = (state = initialState, action) => {

    switch (action.type) {

        case ACTIONS.SET_CONFIG:
            return {
                ...state,
                config: {
                    ...action.payload,
                    "catch": Object.entries(action.payload.catch).reduce((acc, [tier, list]) => {
                        acc[tier] = list.sort();
                        return acc;
                    }, {})
                }
            }

        default:
            return state;
    }
};


const store = Redux.createStore(counterReducer);
