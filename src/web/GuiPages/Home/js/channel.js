// Receive messages
const runSetConnectionStatus = (status) => {
    store.dispatch(setConnectionStatus(status));
};

const runSetBotStatus = (status) => {
    store.dispatch(setBotStatus(status));
};

const runSetLanguage = (language) => {
    store.dispatch(setLanguage(language));
};

const runSetUsername = (username) => {
    store.dispatch(setUsername(username));
};

const runSetJoinedChat = (joinedChat) => {
    store.dispatch(setJoinedChat(joinedChat));
};

const runSetLastSpawn = (spawnData) => {
    const parsedData = JSON.parse(spawnData)
    store.dispatch(setLastSpawn({
        "name": parsedData.name,
        "datetime": new Date(parsedData.datetime),
    }));
};

const runSetPokemonData = (pokemonData) => {
    const parsedData = JSON.parse(pokemonData)
    store.dispatch(setPokemonData({
        captured: {
            "total_count": parsedData.captured.total_count,
            "unique_count": parsedData.captured.unique_count,
            "shiny_count": parsedData.captured.shiny_count,
        },
        pokedex: {
            "total_count": parsedData.pokedex.total_count,
            "total_progress": parsedData.pokedex.total_progress,
            "spawn_count": parsedData.pokedex.spawn_count,
            "spawn_progress": parsedData.pokedex.spawn_progress,
        },
        inventory: {
            "cash": parsedData.inventory.cash,
            "items": parsedData.inventory.items,
        },
        missions: {
            "end_date": parsedData.missions.end_date,
            "missions": parsedData.missions.missions,
        },
    }));
};

const runResetPokemonData = () => {
    store.dispatch(resetPokemonData());
};


// Send messages
let backend_channel;
new QWebChannel(qt.webChannelTransport, function (channel) {
    backend_channel = channel.objects.backend_channel;
});


const handleChangeBotStatus = (newStatus) => backend_channel.change_bot_status(newStatus)
const handleRequestOpenConfig = () => backend_channel.request_open_config()
const handleRequestTwitchLogin = () => backend_channel.request_twitch_login()
const handleRequestTwitchLogout = () => backend_channel.request_twitch_logout()
const handleOpenLink = (link) => backend_channel.handle_open_link(link)
