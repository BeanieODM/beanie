import motor


class DDHandler:
    data = {}

    def set_db(self, uri, db_name):
        self.data["cli"] = motor.motor_asyncio.AsyncIOMotorClient(uri)
        self.data["database"] = self.data["cli"][db_name]

    def get_cli(self):
        return self.data.get("cli")

    def get_db(self):
        return self.data.get("database")
