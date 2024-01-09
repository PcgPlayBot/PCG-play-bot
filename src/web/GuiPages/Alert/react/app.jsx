const AlertPage = () => {

    const [showPropaganda, setShowPropaganda] = React.useState(false);

    React.useEffect(() => {

        const calculateProbability = () => Math.random() < 0.1; // 10% chance to show propaganda
        setShowPropaganda(calculateProbability());
    }, []);

    return (
        <div id={"outer-container"}>
            <div id={"center-container"}>

                {!showPropaganda ? <Body/> : <PropagandaBody/>}

            </div>
        </div>
    );
};


ReactDOM.render(
    <ReactRedux.Provider store={store}>
        <AlertPage/>
    </ReactRedux.Provider>,
    document.getElementById("root")
);
