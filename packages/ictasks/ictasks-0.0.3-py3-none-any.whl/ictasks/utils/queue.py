class Queue:
    def __init__(self) -> None:
        self.ids: list = []

    def pop(self):
        id = self.ids[0]
        del self.ids[0]
        return id

    def available(self):
        return len(self.ids) != 0

    def push(self, id):
        self.ids.append(id)
