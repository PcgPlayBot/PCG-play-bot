const LANG = {
    "pt-br": LANG_PT_BR,
    "es-la": LANG_ES_LA,
    "en-us": LANG_EN_US,
    "default": LANG_PT_BR,
}


const useLanguage = () => {

    const language = ReactRedux.useSelector(state => state.language);

    const [langDict, setLangDict] = React.useState(LANG["language"] || LANG["default"])

    React.useEffect(() => {
        setLangDict(LANG[language] || LANG["default"]);
    }, [language]);

    return langDict;
};
