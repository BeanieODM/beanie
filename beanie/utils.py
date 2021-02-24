from functools import wraps


def check_document_type(func):
    @wraps(func)
    async def decorator(self, document, *args, **kwargs):
        if not isinstance(document, self.document_model):
            raise TypeError("Document must be object of the Document class")
        return await func(self, document, *args, **kwargs)

    return decorator
