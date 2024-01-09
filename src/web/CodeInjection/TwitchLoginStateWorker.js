(function () {

    let backend_channel;
    new QWebChannel(qt.webChannelTransport, function (channel) {
        backend_channel = channel.objects.backend_channel;
    });


    function sendLoginState(isLogged, displayName) {

        if (backend_channel != null) {
            backend_channel.login_state_callback(
                JSON.stringify({isLogged, displayName})
            )
        }
    }

    function checkLogin() {

        console.log("Verifying login state...")

        let isLogged = false
        let displayName = ""

        if (document.querySelector('[data-a-target="login-button"]') == null) {

            const dropButton = document.querySelector('[data-a-target="user-menu-toggle"]')
            dropButton?.click()

            displayName = document.querySelector('[data-a-target="user-display-name"]')?.textContent

            if (displayName != null) {
                isLogged = true
            }
        }

        if (backend_channel != null) backend_channel.login_state_callback(JSON.stringify({isLogged, displayName}))
        else setInterval(() => sendLoginState(isLogged, displayName), 1000)
    }

    if (document.readyState === "complete") checkLogin()
    else window.addEventListener("load", checkLogin);
})();
