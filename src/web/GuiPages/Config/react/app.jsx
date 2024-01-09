const ConfigPage = () => {

    const language = useLanguage()

    const configStore = ReactRedux.useSelector(state => state.config);

    const [configState, setConfigState] = React.useState(configStore);
    const [configChanged, setConfigChanged] = React.useState(false);

    React.useEffect(() => {
        setConfigState(configStore)
    }, [configStore])

    React.useEffect(() => {
        setConfigChanged(JSON.stringify(configStore) !== JSON.stringify(configState))
    }, [configState, configStore])

    const handleSave = () => {
        handleSaveConfig(JSON.stringify(configState))
    }

    const handleChangeLanguage = (newValue) => {
        setConfigState(config => {
            return {...config, language: newValue}
        })
    }

    const handleChangeChannel = (newValue) => {
        setConfigState(config => {
            return {...config, channel: newValue}
        })
    }

    const handleChangeShopConfig = (newValue) => {
        setConfigState(config => {
            return {...config, shop: newValue}
        })
    }

    const handleChangeCatchConfig = (newValue) => {
        setConfigState(config => {
            return {...config, catch: newValue}
        })
    }

    const handleChangeStatsBallConfig = (newValue) => {
        setConfigState(config => {
            return {...config, stats_balls: newValue}
        })
    }

    return (
        <div id={"outer-container"}>

            <p id={"page-title"}>{language.PAGE_TITLE}</p>

            <button
                className={`save-button ${configChanged ? "able" : "disabled"}`}
                onClick={handleSave}
                title={language.SAVE_BUTTON}
                disabled={!configChanged}
            >
                <img
                    className={"save-button-image"}
                    src={"data:image/png;base64,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"}
                    alt={"Save"}
                />
            </button>

            <LanguageAndChannel
                languageConfig={configState.language} setLanguageConfig={handleChangeLanguage}
                channel={configState.channel} setChannel={handleChangeChannel}
            />

            <Shop
                shopConfig={configState.shop} setShopConfig={handleChangeShopConfig}
            />

            <Capture
                catchConfig={configState.catch} setCatchConfig={handleChangeCatchConfig}
            />

            <StatsBalls
                statsBallsConfig={configState.stats_balls} setStatsBallsConfig={handleChangeStatsBallConfig}
            />

        </div>
    );
};


function reformatBallName(name) {
    return name.charAt(0).toUpperCase() + name.slice(1).replace("_", " ");
}


ReactDOM.render(
    <ReactRedux.Provider store={store}>
        <ConfigPage/>
    </ReactRedux.Provider>,
    document.getElementById("root")
);
