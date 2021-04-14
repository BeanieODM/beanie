class WrongDocumentUpdateStrategy(Exception):
    pass


class DocumentNotFound(Exception):
    pass


class DocumentAlreadyCreated(Exception):
    pass


class DocumentWasNotSaved(Exception):
    pass


class CollectionWasNotInitialized(Exception):
    pass


class MigrationException(Exception):
    pass


class ReplaceError(Exception):
    pass
