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

            if (dropButton != null) {

                dropButton.click()

                setTimeout(() => {

                    const displayName = document.querySelector('[data-a-target="user-display-name"]')?.textContent

                    if (backend_channel != null) backend_channel.login_success_callback(JSON.stringify({displayName}))
                    else setInterval(() => sendLoginSuccess(displayName), 1000)
                }, 1000)

            } else {
                setTimeout(checkLoginState, 500)
            }
        }
    }

    setInterval(checkLoginState, 2000)
})();
