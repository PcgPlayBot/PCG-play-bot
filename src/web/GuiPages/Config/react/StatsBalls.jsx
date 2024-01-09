const STATS_BALLS_VALIDATOR = {
    "heavy_ball": {min: 100},
    "feather_ball": {min: 0, max: 150},
    "heal_ball": {min: 100},
    "fast_ball": {min: 100}
};


const StatsBalls = ({statsBallsConfig, setStatsBallsConfig}) => {

    const language = useLanguage()
    const statsBallsText = language.STATS_BALLS

    const [showStatsBallDiv, setShowStatsBallDiv] = React.useState(false);

    const [isValueValid, setIsValueValid] = React.useState(
        Object.keys(STATS_BALLS_VALIDATOR).reduce((acc, ball) => {
            acc[ball] = true;
            return acc;
        }, {})
    );

    React.useEffect(() => {

        setIsValueValid((prevShowStates) => {

            return Object.keys(STATS_BALLS_VALIDATOR).reduce((newStates, itemName) => {

                const {min, max} = STATS_BALLS_VALIDATOR[itemName];
                const value = statsBallsConfig[itemName];
                newStates[itemName] = (min == null || value >= min) && (max == null || value <= max);

                return newStates;

            }, {...prevShowStates});
        });
    }, [statsBallsConfig]);

    const handleInputChange = (itemName, value) => {

        const numberValue = value === "" ? undefined : Number(value);

        setStatsBallsConfig({
            ...statsBallsConfig,
            [itemName]: numberValue
        });
    };

    return (
        <div className={"category-container"}>

            <div className={"category-title-container"}>
                <span className={"category-title"}>{statsBallsText.LABEL}</span>
                <div className={"tooltip-container"} tooltip={statsBallsText.HELP}/>
                <button className={"show-hide-button"} onClick={() => setShowStatsBallDiv(!showStatsBallDiv)}>
                    <div className={`triangle ${showStatsBallDiv ? "collapse" : "expand"}`}/>
                </button>
            </div>

            <CollapsibleDiv showDiv={showStatsBallDiv}>

                <div className={"collapsible-content-container stats-content-container"}>

                    {Object.keys(STATS_BALLS_VALIDATOR).map(itemName => (

                        <div key={itemName} className={"stats-item-container"}>

                            <label className={"label-title stats-label-title"}>
                                <span>{reformatBallName(itemName)}</span>
                            </label>

                            <label className={"stats-label"}>

                                <span className={"label-text"}>{statsBallsText.POKEBALLS_LABELS[itemName]}</span>

                                <input
                                    className={`input-text stats-input ${!isValueValid[itemName] && "invalid-input"}`}
                                    type={"number"}
                                    min={STATS_BALLS_VALIDATOR[itemName].min}
                                    max={STATS_BALLS_VALIDATOR[itemName].max}
                                    value={statsBallsConfig[itemName]}
                                    onChange={(e) => handleInputChange(itemName, e.target.value)}
                                />
                            </label>

                        </div>

                    ))}

                </div>

            </CollapsibleDiv>
        </div>
    );
};
