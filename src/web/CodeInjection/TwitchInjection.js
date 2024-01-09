if (document.getElementById("qt_channel") == null) {
    let newScript = document.createElement("script");
    newScript.id = "qt_channel";
    newScript.innerHTML = `{channel_code}`

    document.head.appendChild(newScript);
}

if (document.getElementById("qt_channel") != null && document.getElementById("qt_injection") == null) {
    let newScript = document.createElement("script");
    newScript.id = "qt_injection";
    newScript.innerHTML = `{injected_code}`

    document.head.appendChild(newScript);
}