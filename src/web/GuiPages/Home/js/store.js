// Redux Actions
const ACTIONS = {
    SET_LANGUAGE: "SET_LANGUAGE",
    SET_CONNECTION_STATUS: "SET_CONNECTION_STATUS",
    SET_BOT_STATUS: "SET_BOT_STATUS",
    SET_USERNAME: "SET_USERNAME",
    SET_JOINED_CHAT: "SET_JOINED_CHAT",
    SET_LAST_SPAWN: "SET_LAST_SPAWN",
    SET_POKEMON_DATA: "SET_POKEMON_DATA",
    RESET_POKEMON_DATA: "RESET_POKEMON_DATA",
}

const setLanguage = (language) => ({
    type: ACTIONS.SET_LANGUAGE,
    payload: language,
});

const setConnectionStatus = (status) => ({
    type: ACTIONS.SET_CONNECTION_STATUS,
    payload: status,
});

const setBotStatus = (status) => ({
    type: ACTIONS.SET_BOT_STATUS,
    payload: status,
});

const setUsername = (username) => ({
    type: ACTIONS.SET_USERNAME,
    payload: username,
});

const setJoinedChat = (joinedChat) => ({
    type: ACTIONS.SET_JOINED_CHAT,
    payload: joinedChat,
});

const setLastSpawn = (spawnData) => ({
    type: ACTIONS.SET_LAST_SPAWN,
    payload: spawnData,
});

const setPokemonData = (pokemonData) => ({
    type: ACTIONS.SET_POKEMON_DATA,
    payload: pokemonData,
});

const resetPokemonData = () => ({
    type: ACTIONS.RESET_POKEMON_DATA,
});


// Initial state
const initialState = {
    connectionStatus: "STARTING",
    botStatus: "ACTIVE",
    language: "pt-br",
    username: "",
    joinedChat: "",
    lastSpawn: {
        "name": "",
        "datetime": undefined,
    },
    pokemonData: {
        captured: {
            "total_count": 0,
            "unique_count": 0,
            "shiny_count": 0,
        },
        pokedex: {
            "total_count": 0,
            "total_progress": 0,
            "spawn_count": 0,
            "spawn_progress": 0,
        },
        inventory: {
            "cash": 0,
            "items": [],
        },
        missions: {
            "end_date": "",
            "missions": [],
        },
    }
}


// Redux reducer
const counterReducer = (state = initialState, action) => {

    switch (action.type) {

        case ACTIONS.SET_CONNECTION_STATUS:
            return {...state, connectionStatus: action.payload}

        case ACTIONS.SET_BOT_STATUS:
            return {...state, botStatus: action.payload}

        case ACTIONS.SET_LANGUAGE:
            return {...state, language: action.payload}

        case ACTIONS.SET_USERNAME:
            return {...state, username: action.payload}

        case ACTIONS.SET_JOINED_CHAT:
            return {...state, joinedChat: action.payload}

        case ACTIONS.SET_LAST_SPAWN:
            return {...state, lastSpawn: action.payload}

        case ACTIONS.SET_POKEMON_DATA:
            return {...state, pokemonData: action.payload}

        case ACTIONS.RESET_POKEMON_DATA:
            return {
                ...state,
                lastSpawn: initialState.lastSpawn,
                pokemonData: initialState.pokemonData,
            }

        default:
            return state;
    }
};


const store = Redux.createStore(counterReducer);
