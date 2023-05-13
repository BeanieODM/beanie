from pydantic import BaseModel

from beanie.exceptions import MongoDBVersionError


class DatabaseVersion(BaseModel):
    major: int
    minor: int
    patch: int

    @classmethod
    def from_str(cls, version: str) -> "DatabaseVersion":
        parts = version.split(".")
        if not parts[0]:
            raise MongoDBVersionError("MongoDB version can't be empty")
        return DatabaseVersion(
            major=parts[0],
            minor=parts[1] if len(parts) > 1 else 0,
            patch=parts[2] if len(parts) > 2 else 0,
        )

    def __str__(self):
        return f"{self.major}.{self.minor}.{self.patch}"
