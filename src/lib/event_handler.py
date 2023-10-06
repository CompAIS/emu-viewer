class EventHandler:
    def __init__(self):
        self.event_listeners = []

    def add(self, listener):
        self.event_listeners.append(listener)

    def remove(self, listener):
        self.event_listeners.remove(listener)

    def invoke(self, *args, **kwargs):
        for listener in self.event_listeners:
            listener(*args, **kwargs)
