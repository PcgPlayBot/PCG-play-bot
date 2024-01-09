const TIERS = ["S", "M", "A", "B", "C"];
const POKE_BALLS_LIST = [
    "master_ball", "nest_ball", "types_ball", "stats_ball", "timers_ball", "ultra_ball", "friend_ball",
    "repeat_ball", "great_ball", "cherish_ball", "stone_ball", "clone_ball", "level_ball", "poke_ball"
]


const Capture = ({catchConfig, setCatchConfig}) => {

    const language = useLanguage()
    const captureText = language.CAPTURE

    const [showDivStates, setShowDivStates] = React.useState(
        TIERS.reduce((acc, tier) => {
            acc[tier] = false;
            return acc;
        }, {})
    );

    const handleToggleShow = (tier) => {
        setShowDivStates((prevShowStates) => ({
            ...prevShowStates,
            [tier]: !prevShowStates[tier]
        }));
    };

    const handleSetBall = (tier, ball) => {

        const isBallInList = catchConfig[tier].includes(ball)

        const updatedList = isBallInList
            ? catchConfig[tier].filter((item) => item !== ball)
            : catchConfig[tier].concat(ball);

        setCatchConfig({
            ...catchConfig,
            [tier]: updatedList.sort()
        });
    };

    return TIERS.map(tier => {

        return (
            <div className={"category-container"} key={tier}>

                <div className={"category-title-container"}>
                    <span className={"category-title"}>{captureText[tier].LABEL}</span>
                    <div className={"tooltip-container"} tooltip={captureText[tier].HELP}/>
                    <button className={"show-hide-button"} onClick={() => handleToggleShow(tier)}>
                        <div className={`triangle ${showDivStates[tier] ? "collapse" : "expand"}`}/>
                    </button>
                </div>

                <CollapsibleDiv showDiv={showDivStates[tier]}>

                    <div className={`collapsible-content-container capture-content-container capture-${tier}`}>

                        <div>

                            <div className={"capture-item-container"}>

                                <div className={"capture-label-title"}/>

                                <label className={"capture-checkbox-label label-text"}>
                                    <span>{captureText.NEW}</span>
                                    <div className={"tooltip-container"} tooltip={captureText.NEW_HELP}/>
                                </label>

                                <label className={"capture-checkbox-label label-text"}>
                                    <span>{captureText.REPEATED}</span>
                                    <div className={"tooltip-container"} tooltip={captureText.REPEATED_HELP}/>
                                </label>

                            </div>

                            {POKE_BALLS_LIST.map(itemName => (

                                <div key={itemName} className={"capture-item-container"}>

                                    <label className={"label-title capture-label-title"}>
                                        <span>{reformatBallName(itemName)}</span>
                                        {captureText.POKEBALLS_HELP[itemName] != null &&
                                        <div className={"tooltip-container"}
                                             tooltip={captureText.POKEBALLS_HELP[itemName]}/>
                                        }
                                    </label>

                                    <label className={"capture-checkbox-label"}>
                                        <input
                                            type="checkbox"
                                            checked={catchConfig[`uncapt_${tier}`].includes(itemName) && itemName !== "nest_ball"}
                                            onChange={() => handleSetBall(`uncapt_${tier}`, itemName)}
                                            disabled={itemName === "nest_ball" || itemName === "repeat_ball"}
                                        />
                                    </label>

                                    <label className={"capture-checkbox-label"}>
                                        <input
                                            type="checkbox"
                                            checked={catchConfig[tier].includes(itemName) && itemName !== "nest_ball"}
                                            onChange={() => handleSetBall(tier, itemName)}
                                            disabled={itemName === "nest_ball"}
                                        />
                                    </label>

                                </div>

                            ))}

                        </div>

                        <div>
                            <span className={"priority-text"}>&darr; {captureText.PRIORITY} &darr;</span>
                        </div>

                    </div>

                </CollapsibleDiv>

            </div>
        );
    })
};
