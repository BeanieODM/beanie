class SettersInterface:
    @classmethod
    def set_collection(cls, collection):
        """
        Collection setter
        """
        cls._document_settings.motor_collection = collection

    @classmethod
    def set_database(cls, database):
        """
        Database setter
        """
        cls._document_settings.motor_db = database

    @classmethod
    def set_collection_name(cls, name: str):
        """
        Collection name setter
        """
        cls._document_settings.name = name
