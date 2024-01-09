const LanguageAndChannel = ({languageConfig, setLanguageConfig, channel, setChannel}) => {

    const language = useLanguage()
    const languageText = language.LANGUAGE
    const channelText = language.CHANNEL

    const [isChannelValid, setIsChannelValid] = React.useState(true);

    const handleLanguageChange = (e) => {
        const inputValue = e.target.value;
        setLanguageConfig(inputValue);
    };

    const handleChannelChange = (e) => {
        const inputValue = e.target.value;
        setChannel(inputValue.toLowerCase());

        setIsChannelValid(/^[a-zA-Z0-9]*$/.test(inputValue));
    };

    const handleChannelBlur = () => {
        setIsChannelValid(/^[a-zA-Z0-9]*$/.test(channel));
    };

    return (
        <div className={"category-container language-channel-container"}>

            <label className={"language-label"}>

                <span className={"category-title language-channel-title"}>{languageText.LABEL}</span>

                <select className={"language-select"} value={languageConfig} onChange={handleLanguageChange}>
                    <option value={"pt-br"}>{languageText.PT_BR}</option>
                    <option value={"es-la"}>{languageText.ES_LA}</option>
                    <option value={"en-us"}>{languageText.EN_US}</option>
                </select>

            </label>

            <label>

                <span className={"category-title language-channel-title"}>{channelText.LABEL}</span>

                <input
                    className={`input-text ${!isChannelValid && "invalid-input"}`}
                    type={"text"}
                    value={channel}
                    onChange={handleChannelChange}
                    onBlur={handleChannelBlur}
                />

            </label>

        </div>
    )
}