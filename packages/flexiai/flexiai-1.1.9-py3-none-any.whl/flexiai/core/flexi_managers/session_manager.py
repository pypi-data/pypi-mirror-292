# flexiai/core/flexi_managers/session_manager.py
from flask import session


class SessionManager:
    """
    SessionManager handles the creation, retrieval, and deletion of user sessions
    within a Flask application. It also manages logging for these operations.

    Attributes:
        client: The client object for interacting with the backend.
        logger (logging.Logger): Logger for logging information and errors.
    """

    def __init__(self, client, logger):
        """
        Initializes the SessionManager with the provided client and logger.

        Args:
            client: The client object for interacting with the backend.
            logger (logging.Logger, optional): Logger for logging information and errors. Defaults to None.
        """
        self.client = client
        self.logger = logger


    def create_session(self, session_id, data):
        """
        Creates a new session or updates an existing session with the given session_id.

        Args:
            session_id (str): The ID of the session.
            data (dict): The data to store in the session.

        Returns:
            dict: The session data.

        Raises:
            Exception: If an unexpected error occurs while creating/updating the session.
        """
        try:
            self.logger.info(f"Creating or updating session with ID: {session_id}")
            session[session_id] = data
            # self.logger.info(f"Session data: {data}")
            return session[session_id]
        except Exception as e:
            self.logger.error(f"An unexpected error occurred while creating/updating session {session_id}: {str(e)}", exc_info=True)
            raise


    def get_session(self, session_id):
        """
        Retrieves session data by session_id.

        Args:
            session_id (str): The ID of the session.

        Returns:
            dict: The session data.

        Raises:
            KeyError: If the session ID is not found.
            Exception: If an unexpected error occurs while retrieving the session.
        """
        try:
            self.logger.info(f"Retrieving session with ID: {session_id}")
            data = session.get(session_id)
            if data is None:
                raise KeyError(f"Session ID {session_id} not found.")
            # self.logger.info(f"Retrieved session data: {data}")
            return data
        except KeyError as e:
            self.logger.error(f"Session ID {session_id} not found: {str(e)}", exc_info=True)
            raise
        except Exception as e:
            self.logger.error(f"An unexpected error occurred while retrieving session {session_id}: {str(e)}", exc_info=True)
            raise


    def delete_session(self, session_id):
        """
        Deletes session data by session_id.

        Args:
            session_id (str): The ID of the session to delete.

        Returns:
            bool: True if the session was deleted successfully, False otherwise.

        Raises:
            Exception: If an unexpected error occurs while deleting the session.
        """
        try:
            self.logger.info(f"Deleting session with ID: {session_id}")
            if session_id in session:
                session.pop(session_id)
                # self.logger.info(f"Deleted session with ID: {session_id}")
                return True
            else:
                self.logger.warning(f"Session ID {session_id} not found.")
                return False
        except Exception as e:
            self.logger.error(f"An unexpected error occurred while deleting session {session_id}: {str(e)}", exc_info=True)
            raise


    def get_all_sessions(self):
        """
        Retrieves all current sessions.

        Returns:
            dict: A dictionary containing all current sessions.
        """
        try:
            self.logger.info("Retrieving all sessions")
            all_sessions = session.items()
            # self.logger.info(f"All sessions data: {all_sessions}")
            return dict(all_sessions)
        except Exception as e:
            self.logger.error(f"An unexpected error occurred while retrieving all sessions: {str(e)}", exc_info=True)
            raise


    def clear_all_sessions(self):
        """
        Clears all current sessions.

        Returns:
            bool: True if all sessions were cleared successfully, False otherwise.
        """
        try:
            self.logger.info("Clearing all sessions")
            session.clear()
            # self.logger.info("All sessions cleared successfully")
            return True
        except Exception as e:
            self.logger.error(f"An unexpected error occurred while clearing all sessions: {str(e)}", exc_info=True)
            raise
