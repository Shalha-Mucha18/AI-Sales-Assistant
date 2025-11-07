class SimpleMemory:
    """Lightweight conversation memory to persist user & agent exchanges."""
    def __init__(self, max_entries: int = 10):
        self.max_entries = max_entries
        self.buffer = []

    def add(self, role: str, content: str):
        """Add a user or assistant message to memory."""
        self.buffer.append({"role": role, "content": content})
        if len(self.buffer) > self.max_entries:
            self.buffer.pop(0)

    def get_context(self) -> str:
        """Return all messages in readable chronological format."""
        return "\n".join([f"{m['role'].capitalize()}: {m['content']}" for m in self.buffer])
