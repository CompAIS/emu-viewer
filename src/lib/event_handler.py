class EventHandler:
    event_listeners = []

    def add(self, listener):
        self.event_listeners.append(listener)

    def invoke_listeners(self, *args, **kwargs):
        for listener in self.event_listeners:
            listener(*args, **kwargs)
