const CollapsibleDiv = ({showDiv, children}) => {

    const outerDivRef = React.useRef(null)
    const wrapperDivRef = React.useRef(null)

    React.useEffect(() => {

        if (outerDivRef.current == null || wrapperDivRef.current == null) return

        if (!showDiv || outerDivRef.current.clientHeight) {
            outerDivRef.current.style.height = "0";
        } else {
            outerDivRef.current.style.height = wrapperDivRef.current.clientHeight + "px";
        }
    }, [showDiv])

    return (
        <div className={"collapsible"} ref={outerDivRef}>
            <div ref={wrapperDivRef}>
                {children}
            </div>
        </div>
    )
}