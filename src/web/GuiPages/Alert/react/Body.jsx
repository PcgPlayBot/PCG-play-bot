const Body = () => {

    const language = useLanguage()
    const bodyText = language.BODY

    const [dontShowAgain, setDontShowAgain] = React.useState(false)
    const [showCustomAlert, setShowCustomAlert] = React.useState(false);


    const handleCloseButtonClick = () => {
        if (dontShowAgain) {
            setShowCustomAlert(true);
        } else {
            handleClose()
        }
    };

    return (
        <div id={"body-container"}>

            <div>

                {bodyText.PARAGRAPHS.map((paragraph, idx) => (
                    <p
                        key={idx}
                        className={"page-text"}
                        dangerouslySetInnerHTML={{__html: paragraph}}
                    />
                ))}

                <p className={"page-text"}>
                    <strong className={"attention-text"}>{bodyText.ATTENTION_LABEL}</strong> {bodyText.ATTENTION_PARAGRAPH}
                </p>

            </div>

            <div>
                <div className={"dont-show-div"}>
                    <span className={"page-text"}>{bodyText.DONT_SHOW}</span>

                    <input
                        type={"checkbox"}
                        checked={dontShowAgain}
                        onChange={() => setDontShowAgain(!dontShowAgain)}
                    />
                </div>
                <div className={"buttons-container"}>
                    <button className={"close-button"} onClick={handleCloseButtonClick}>{bodyText.BUTTON1}</button>
                    <button className={"close-button"} onClick={handleCloseButtonClick}>{bodyText.BUTTON2}</button>
                </div>
            </div>

            {showCustomAlert && (
                <CustomAlert onClose={handleClose}/>
            )}

        </div>
    )
}


const CustomAlert = ({onClose}) => {

    const language = useLanguage()
    const bodyText = language.BODY

    return (
        <div className="custom-alert">
            <p className={"custom-alert-text"}>{bodyText.ALERT}</p>
            <button className={"custom-alert-button"} onClick={onClose}>{bodyText.ALERT_CLOSE}</button>
        </div>
    );
};
