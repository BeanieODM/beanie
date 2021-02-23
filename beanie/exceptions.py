class WrongDocumentUpdateStrategy(Exception):
    pass


class DocumentNotFound(Exception):
    pass


class DocumentAlreadyCreated(Exception):
    pass


class DocumentWasNotSaved(Exception):
    pass
