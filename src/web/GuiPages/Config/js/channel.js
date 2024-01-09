// Receive messages
const runSetConfig = (config) => {
    store.dispatch(setConfig(JSON.parse(config)));
};


// Send messages
let backend_channel;
new QWebChannel(qt.webChannelTransport, function (channel) {
    backend_channel = channel.objects.backend_channel;
});


const handleSaveConfig = (newConfig) => backend_channel.save_config(newConfig)
