from unittest import TestCase, mock

from src.lib.event_handler import EventHandler


class EventHandlerTest(TestCase):
    @staticmethod
    def test_all_events_called_on_invoke():
        my_handler = EventHandler()

        listener_1 = mock.Mock()
        listener_2 = mock.Mock()
        listener_3 = mock.Mock()

        my_handler.add(listener_1)
        my_handler.add(listener_2)
        my_handler.add(listener_3)

        my_handler.invoke("foo", bar="baz")

        listener_1.assert_called_once_with("foo", bar="baz")
        listener_2.assert_called_once_with("foo", bar="baz")
        listener_3.assert_called_once_with("foo", bar="baz")
