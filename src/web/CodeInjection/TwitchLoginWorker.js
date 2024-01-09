(function () {

    let backend_channel;
    new QWebChannel(qt.webChannelTransport, function (channel) {
        backend_channel = channel.objects.backend_channel;
    });

    function sendLoginSuccess(displayName) {

        if (backend_channel != null) {
            backend_channel.login_success_callback(JSON.stringify({displayName}))
        }
    }

    function checkLoginState() {

        console.log("Verifying login state...")

        if (document.querySelector('[data-a-target="login-button"]') == null) {

            const dropButton = document.querySelector('[data-a-target="user-menu-toggle"]')
            dropButton?.click()

            const displayName = document.querySelector('[data-a-target="user-display-name"]')?.textContent

            if (displayName != null) {

                if (backend_channel != null) backend_channel.login_success_callback(JSON.stringify({displayName}))
                else setInterval(() => sendLoginSuccess(displayName), 1000)
            }
        }
    }

    setInterval(checkLoginState, 2000)
})();
