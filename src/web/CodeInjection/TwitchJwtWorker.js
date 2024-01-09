(function () {

    const EXTENSION_ID = "pm0qkv9g4h87t5y6lg329oam8j7ze9"

    let isLogged = false;

    let backend_channel;
    new QWebChannel(qt.webChannelTransport, function (channel) {
        backend_channel = channel.objects.backend_channel;
    });

    function sendJwt(jwt) {

        if (isLogged && backend_channel != null) {
            backend_channel.get_jwt_callback(JSON.stringify({
                    jwt: jwt,
                }))
        }
    }

    function hookFetch() {

        console.log("Hooking fetch...");

        let realFetch = window.fetch;

        window.fetch = function (url, init, ...args) {

            if (typeof url === "string" && url.includes("gql") && init && init.method.toUpperCase() === "POST") {

                const result = realFetch.apply(this, arguments);

                result.then(response => {

                    response.text().then(bodyText => {

                        if (bodyText.includes(EXTENSION_ID)) {

                            const regex = new RegExp('"token":{[^}]*"extensionID":"(' + EXTENSION_ID + ')",[^}]*"jwt":"([^"]+)"[^}]*}', 'i');
                            const match = bodyText.match(regex);

                            if (match && match.length === 3) {
                                const jwt = match[2]

                                if (isLogged && backend_channel != null) backend_channel.get_jwt_callback(JSON.stringify({jwt}))
                                else setInterval(() => sendJwt(jwt), 1000)
                            }
                        }
                    });
                }).catch(error => {
                    console.error("Fetch error:", error);
                });
            }

            return realFetch.apply(this, arguments);
        };
    }

    function checkLogin() {

        console.log("Verifying login state...")

        if (document.querySelector('[data-a-target="login-button"]') == null) {

            const dropButton = document.querySelector('[data-a-target="user-menu-toggle"]')
            dropButton?.click()

            const displayName = document.querySelector('[data-a-target="user-display-name"]')?.textContent

            if (displayName != null) {
                isLogged = true
            } else {
                backend_channel.login_error()
            }
        }
    }

    hookFetch();

    if (document.readyState === "complete") checkLogin()
    else window.addEventListener("load", checkLogin);
})();
