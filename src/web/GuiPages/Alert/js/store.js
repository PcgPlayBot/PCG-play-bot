// Redux Actions
const ACTIONS = {
    SET_LANGUAGE: "SET_LANGUAGE",
}

const setLanguage = (language) => ({
    type: ACTIONS.SET_LANGUAGE,
    payload: language,
});

// Initial state
const initialState = {
    language: "pt-br",
}


// Redux reducer
const counterReducer = (state = initialState, action) => {

    switch (action.type) {

        case ACTIONS.SET_LANGUAGE:
            return {...state, language: action.payload}

        default:
            return state;
    }
};


const store = Redux.createStore(counterReducer);
