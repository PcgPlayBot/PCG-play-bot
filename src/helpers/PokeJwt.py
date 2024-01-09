from base64 import urlsafe_b64decode
from datetime import datetime
from json import loads


class PokeJwt:
    """

    A class to deal with PCG JWT extracted from Twitch.
    Contains raw JWT string and expiration date.
    """

    def __init__(self, encoded_jwt):
        header, payload, signature = encoded_jwt.split(".")
        payload_decoded = urlsafe_b64decode(payload + "==").decode("utf-8")
        payload_dict = loads(payload_decoded)
        expiration_datetime = datetime.fromtimestamp(payload_dict["exp"])

        self._exp = expiration_datetime
        self._jwt = encoded_jwt

    @property
    def jwt(self):
        return self._jwt

    @property
    def exp(self):
        return self._exp
