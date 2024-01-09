import socket
from threading import Thread
from datetime import datetime, timedelta

from src.helpers.Worker import Worker

from assets.const.pokemon_data import POKEMON_BOT_NAME
from assets.const.urls import TWITCH_CHAT_SERVER, TWITCH_CHAT_PORT

teste = Worker(15 * 1000)


class TwitchSocketManager:
    """

    This class is responsible to manage socket connection.
    It uses user oAuth code to connect to a channel and listen/send chat messages.
    """

    def __init__(self,
                 chat_connection_callback,
                 chat_disconnection_callback,
                 chat_connection_error_callback,
                 poke_spawn_callback,
                 ):

        self._connection_callback = chat_connection_callback
        self._disconnection_callback = chat_disconnection_callback
        self._error_callback = chat_connection_error_callback
        self._poke_spawn_callback = poke_spawn_callback

        self._socket = socket.socket()

        self._listener_thread = Thread()

        self._connected = False
        self._connected_channel = None

    def connect(self, user_data, channel_name):
        """Creates a socket connection to Twitch chat using user oAuth and desired channel"""

        print("Connecting socket.")

        try:
            self._socket.close()
            self._socket = socket.socket()
            self._socket.setblocking(True)
            self._socket.connect((TWITCH_CHAT_SERVER, TWITCH_CHAT_PORT))

        except socket.gaierror as error:
            print("Socket connection error:\n", error)
            self._error_callback()

        self._socket.send(f'PASS {user_data.oauth}\nNICK {user_data.username}\n Join #{channel_name}\n'.encode())

        self._connected = True
        self._connected_channel = channel_name

        self._socket.setblocking(False)

        self._listener_thread = Thread(target=self._check_connection_started).start()

    def _check_connection_started(self):
        """Listen socket on connection to verify connection was successfully started"""

        loading = True
        loading_started = datetime.now()

        while loading:

            if datetime.now() - loading_started > timedelta(seconds=15):
                return self._on_disconnect()

            try:
                read_buffer = self._socket.recv(1024).decode()

                for line in read_buffer.split('\r\n')[0:-1]:
                    if "End of /NAMES list" in line:
                        loading = False
                        break
                    elif "Login authentication failed" in line:
                        print("Twitch authentication failed.")
                        return self._on_disconnect()

            except BlockingIOError:
                continue

        self._on_connect()

    def _on_connect(self):
        """Callback on socket connection successfully created"""

        print("Socket connected.")

        self._listener_thread = Thread(target=self._receive_messages).start()

        self._connection_callback()

    def disconnect(self):
        """Closes a socket connection to Twitch chat"""

        self._socket.close()

        if self._connected:
            self._on_disconnect()

    def _on_disconnect(self):
        """Callback on socket connection closed"""

        self._connected = False
        self._connected_channel = None
        self._disconnection_callback()

    def _receive_messages(self):
        """Keeps listening to socket chat messages"""

        while self._connected:

            try:
                read_buffer = self._socket.recv(1024).decode()

                for line in read_buffer.split('\r\n'):

                    # Ping pong to stay alive
                    if 'PING' in line and 'PRIVMSG' not in line:
                        self._socket.send('PONG tmi.twitch.tv\r\n'.encode())

                    elif line != '' and 'PRIVMSG' in line and POKEMON_BOT_NAME in line:
                        parts = line.split(':', 2)
                        try:
                            self._process_message(parts[1].split('!', 1)[0], parts[2])
                        except IndexError:
                            print("Index Error:", line)

            except BlockingIOError:
                continue

            except OSError:
                self._on_disconnect()

            except Exception as error:
                print("Socket error: ", error)
                continue

    def _process_message(self, sender, message):
        """Processes a chat message and verify if it was a PCG spawn message"""

        if sender != POKEMON_BOT_NAME:
            return

        else:
            if "!pokecatch" in message and "90" in message:
                self._poke_spawn_callback(message)

    def send_chat_message(self, message):
        """Sends a message in chat"""

        if self._connected and self._connected_channel is not None:
            message_temp = f'PRIVMSG #{self._connected_channel} :{message}'
            self._socket.send(f'{message_temp}\n'.encode())

    @property
    def connected(self):
        return self._connected
