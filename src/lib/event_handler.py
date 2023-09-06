class EventHandler:
    event_listeners = {}

    def add(self, name, listener):
        self.event_listeners[name] = listener

    def invoke(self, name, *args, **kwargs):
        listener = self.event_listeners[name]
        listener(*args, **kwargs)
