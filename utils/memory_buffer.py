class ContextMemory:
    def __init__(self, max_turns=5):
        self.turns = []
        self.max_turns = max_turns

    def update(self, entry: str):
        self.turns.append(entry)
        if len(self.turns) > self.max_turns:
            self.turns.pop(0)

    def get_context(self):
        return "\n".join(self.turns)