(function () {

    let backend_channel;
    new QWebChannel(qt.webChannelTransport, function (channel) {
        backend_channel = channel.objects.backend_channel;
    });

    function sendOauth(oauth) {

        if (backend_channel != null) {
            backend_channel.get_oauth_callback(JSON.stringify({oauth}))
        }
    }

    function getOauth() {

        const connectButton = document.querySelector("a.btn.btn-large.btn-primary");
        const authorizeButton = document.querySelector("button.js-authorize");

        if (connectButton?.offsetParent != null) {
            connectButton.click()

        } else if (authorizeButton != null) {
            authorizeButton.click()

        } else {

            const oAuthElement = document.getElementById("tmiPasswordField")

            if (oAuthElement?.offsetParent != null) {

                const oauth = oAuthElement.value

                if (backend_channel != null) backend_channel.get_oauth_callback(JSON.stringify({oauth}))
                else setInterval(() => sendOauth(oauth), 1000)
            }
        }
    }

    if (document.readyState === "complete") getOauth()
    else window.addEventListener("load", getOauth);
})();
