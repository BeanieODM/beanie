from typing import Optional

from pymongo.asynchronous.client_session import AsyncClientSession


class SessionMethods:
    """
    Session methods
    """

    def set_session(self, session: Optional[AsyncClientSession] = None):
        """
        Set session
        :param session: Optional[AsyncClientSession] - pymongo session
        :return:
        """
        if session is not None:
            self.session: Optional[AsyncClientSession] = session
        return self
