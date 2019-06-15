class EventEmmiter:
    def __init__(self):
        self._listeners = {}

    def on(self, event_name, handler):
        if not event_name in self._listeners:
            self._listeners[event_name] = []
        self._listeners[event_name].append(handler)

    def emit(self, event_name, data=None):
        if event_name in self._listeners:
            for listener in self._listeners[event_name]:
                listener(data)


event_emmiter = EventEmmiter()
