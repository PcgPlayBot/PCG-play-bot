// Receive messages
const runSetLanguage = (language) => {
    store.dispatch(setLanguage(language));
};


// Send messages
let backend_channel;
new QWebChannel(qt.webChannelTransport, function (channel) {
    backend_channel = channel.objects.backend_channel;
});


const handleClose = () => backend_channel.handle_close()
const handleOpenLink = (link) => backend_channel.handle_open_link(link)
