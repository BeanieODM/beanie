class RunInterface:
    def run(self):
        raise NotImplementedError

    def __invert__(self):
        return self.run()
