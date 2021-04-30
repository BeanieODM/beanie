from typing import Optional

from pymongo.client_session import ClientSession


class SessionMethods:
    def set_session(self, session: Optional[ClientSession] = None):
        if session is not None:
            self.session = session
        return self
