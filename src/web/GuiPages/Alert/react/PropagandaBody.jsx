const PropagandaBody = () => {

    const language = useLanguage()
    const propagandaText = language.PROPAGANDA

    const [selectedPropaganda, setSelectedPropaganda] = React.useState(propagandaText.DOCUMENTS[0]);

    React.useEffect(() => {
        const randomIndex = Math.floor(Math.random() * propagandaText.DOCUMENTS.length);
        setSelectedPropaganda(propagandaText.DOCUMENTS[randomIndex]);
    }, [propagandaText]);

    const handleReadMore = () => {
        handleOpenLink(selectedPropaganda.SOURCE)
    }

    return (
        <div id={"body-container"}>

            <div>

                {selectedPropaganda.PARAGRAPHS.map((paragraph, idx) => (
                    <p key={idx} className={"page-text"}>
                        {paragraph}
                    </p>
                ))}

                <p className={"page-text"}>
                    <a id={"github-link"} onClick={handleReadMore}>
                        {propagandaText.KEEP_READING}
                    </a>
                </p>

            </div>

            <div>
                <div className={"buttons-container"}>
                    <button className={"close-button"} onClick={handleClose}>{propagandaText.BUTTON1}</button>
                    <button className={"close-button"} onClick={handleReadMore}>{propagandaText.BUTTON2}</button>
                </div>
            </div>

        </div>
    )
}
