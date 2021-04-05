import motor


class DBHandler:
    data = {}

    def set_db(self, uri, db_name):
        self.data["client"] = motor.motor_asyncio.AsyncIOMotorClient(uri)
        self.data["database"] = self.data["client"][db_name]

    def get_cli(self):
        return self.data.get("client")

    def get_db(self):
        return self.data.get("database")
