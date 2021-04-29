from abc import ABC
from typing import Optional

from beanie.odm.operators.find import BaseFindOperator


class BaseFindEvaluationOperator(BaseFindOperator, ABC):
    ...


class Expr(BaseFindEvaluationOperator):
    def __init__(self, expression: dict):
        self.expression = expression

    @property
    def query(self):
        return {"$expr": self.expression}


class JsonSchema(BaseFindEvaluationOperator):
    def __init__(self, expression: dict):
        self.expression = expression

    @property
    def query(self):
        return {"$jsonSchema": self.expression}


class Mod(BaseFindEvaluationOperator):
    def __init__(self, field, divisor, remainder):
        self.field = field
        self.divisor = divisor
        self.remainder = remainder

    @property
    def query(self):
        return {self.field: {"$mod": [self.divisor, self.remainder]}}


class RegEx(BaseFindEvaluationOperator):
    def __init__(self, field, pattern, options: Optional[str] = None):
        self.field = field
        self.pattern = pattern
        self.options = options

    @property
    def query(self):
        expression = {"$regex": self.pattern}
        if self.options:
            expression["$options"] = self.options
        return {self.field: expression}


class Text(BaseFindEvaluationOperator):
    def __init__(
        self,
        search: str,
        language: Optional[str] = None,
        case_sensitive: bool = False,
        diacritic_sensitive: bool = False,
    ):
        self.search = search
        self.language = language
        self.case_sensitive = case_sensitive
        self.diacritic_sensitive = diacritic_sensitive

    @property
    def query(self):
        expression = {
            "$text": {
                "$search": self.search,
                "$caseSensitive": self.case_sensitive,
                "$diacriticSensitive": self.diacritic_sensitive,
            }
        }
        if self.language:
            expression["$text"]["$language"] = self.language
        return expression


class Where(BaseFindEvaluationOperator):
    def __init__(self, expression: str):
        self.expression = expression

    @property
    def query(self):
        return {"$where": self.expression}
