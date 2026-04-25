import threading
from src.config import MAX_UNDO_STACK


class HistoryManager:
    def __init__(self, app):
        self.app = app
        self.undo_stack = []
        self.redo_stack = []
        self._lock = threading.Lock()
        self._is_restoring = False

    def record(self, key, old, new):
        if self._is_restoring or old == new:
            return
        with self._lock:
            self.undo_stack.append((key, old, new))
            self.redo_stack.clear()
            if len(self.undo_stack) > MAX_UNDO_STACK:
                self.undo_stack.pop(0)

    def undo(self):
        with self._lock:
            if not self.undo_stack:
                return
            k, o, n = self.undo_stack.pop()
            self.redo_stack.append((k, o, n))
            self._is_restoring = True
        self.app.vars[k].set(o)
        self._is_restoring = False

    def redo(self):
        with self._lock:
            if not self.redo_stack:
                return
            k, o, n = self.redo_stack.pop()
            self.undo_stack.append((k, o, n))
            self._is_restoring = True
        self.app.vars[k].set(n)
        self._is_restoring = False
