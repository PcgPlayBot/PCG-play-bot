class UserData:
    """

    A class to deal with user credentials extracted from Twitch.
    Contains raw username string and oAuth code.
    """

    def __init__(self, user_data):
        self._username = user_data["username"]
        self._oauth = user_data["oauth"]

    @property
    def username(self):
        return self._username

    @property
    def oauth(self):
        return self._oauth
