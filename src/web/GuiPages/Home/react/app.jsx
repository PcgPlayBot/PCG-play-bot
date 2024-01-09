const HomePage = () => {

    return (
        <div id={"outer-container"}>
            <div id={"center-container"}>

                <Header/>
                <Body/>
                <Footer/>

            </div>
        </div>
    );
};


ReactDOM.render(
    <ReactRedux.Provider store={store}>
        <HomePage/>
    </ReactRedux.Provider>,
    document.getElementById("root")
);
