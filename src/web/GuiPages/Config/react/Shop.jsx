const SHOP_VALIDATOR = {
    "poke_ball": {min_one: 300, min_ten: 3000},
    "great_ball": {min_one: 600, min_ten: 6000},
    "ultra_ball": {min_one: 1000, min_ten: 10000},
}


const Shop = ({shopConfig, setShopConfig}) => {

    const language = useLanguage()
    const shopText = language.SHOP

    const [showShopDiv, setShowSopDiv] = React.useState(false)

    const [isValueValid, setIsValueValid] = React.useState(
        Object.keys(SHOP_VALIDATOR).reduce((acc, ball) => {
            acc[ball] = {one: true, ten: true};
            return acc;
        }, {})
    );

    React.useEffect(() => {
        setIsValueValid((prevShowStates) => {
            return Object.keys(SHOP_VALIDATOR).reduce((newStates, itemName) => {
                const {min_one, min_ten} = SHOP_VALIDATOR[itemName];

                newStates[itemName] = {
                    one: shopConfig[itemName].buy_one >= min_one,
                    ten: shopConfig[itemName].buy_ten >= min_ten,
                };

                return newStates;
            }, {...prevShowStates});
        });
    }, [shopConfig]);

    const handleBuyOnMissingChange = (itemName) => {
        setShopConfig({
            ...shopConfig,
            [itemName]: {
                ...shopConfig[itemName],
                buy_on_missing: !shopConfig[itemName].buy_on_missing
            }
        });
    };

    const handleBuyChange = (itemName, value, amount) => {

        const numberValue = value !== "" && Number(value);

        setShopConfig({
            ...shopConfig,
            [itemName]: {
                ...shopConfig[itemName],
                [`buy_${amount}`]: numberValue
            }
        });
    };

    return (
        <div className={"category-container"}>

            <div className={"category-title-container"}>
                <span className={"category-title"}>{shopText.LABEL}</span>
                <div className={"tooltip-container"} tooltip={shopText.HELP}/>
                <button className={"show-hide-button"} onClick={() => setShowSopDiv(!showShopDiv)}>
                    <div className={`triangle ${showShopDiv ? "collapse" : "expand"}`}/>
                </button>
            </div>

            <CollapsibleDiv showDiv={showShopDiv}>

                <div className={"collapsible-content-container shop-content-container"}>

                    {Object.keys(shopConfig).map(itemName => (

                        <div key={itemName} className={"shop-item-container"}>

                            <label className={"label-title shop-label-title"}>
                                <span>{reformatBallName(itemName)}</span>
                            </label>

                            <label className={"shop-label"}>
                                <span className={"label-text"}>{shopText.CHECKBOX}</span>

                                <input
                                    type={"checkbox"}
                                    checked={shopConfig[itemName].buy_on_missing}
                                    onChange={() => handleBuyOnMissingChange(itemName)}
                                />
                            </label>

                            <label className={"shop-label"}>

                                <span className={"label-text"}>{shopText.ONE}</span>

                                <input
                                    className={`input-text shop-input ${!isValueValid[itemName]["one"] && "invalid-input"}`}
                                    type={"number"}
                                    min={SHOP_VALIDATOR[itemName].min_one}
                                    value={shopConfig[itemName].buy_one}
                                    onChange={(e) => handleBuyChange(itemName, e.target.value, "one")}
                                    disabled={!shopConfig[itemName].buy_on_missing}
                                />
                                <span className={"shop-dollar-label"}>$</span>
                            </label>

                            <label className={"shop-label"}>

                                <span className={"label-text"}>{shopText.TEN}</span>

                                <input
                                    className={`input-text shop-input ${!isValueValid[itemName]["ten"] && "invalid-input"}`}
                                    type={"number"}
                                    min={SHOP_VALIDATOR[itemName].min_ten}
                                    value={shopConfig[itemName].buy_ten}
                                    onChange={(e) => handleBuyChange(itemName, e.target.value, "ten")}
                                    disabled={!shopConfig[itemName].buy_on_missing}
                                />
                                <span className={"shop-dollar-label"}>$</span>
                            </label>

                        </div>

                    ))}

                </div>

            </CollapsibleDiv>

        </div>
    );
};
