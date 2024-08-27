import threading
from unittest import TestCase, mock

from openmodule.alert import AlertHandleType
from openmodule.config import override_settings
from openmodule.core import core, init_openmodule, shutdown_openmodule
from openmodule.models.base import ZMQMessage
from openmodule_test.alert import AlertTestMixin
from openmodule_test.health import HealthTestMixin


class OpenModuleCoreTest(AlertTestMixin, HealthTestMixin, TestCase):
    topics = ["healthpong", "sentry", "alert", "test"]
    protocol = "tcp://"

    @override_settings(NAME="x123x")
    def test_core_init_and_shutdown(self):
        self.assertIsNone(core())

        init_openmodule(self.zmq_config())
        try:
            self.assertIsNotNone(core())
            self.wait_for_health(name="x123x")
        finally:
            shutdown_openmodule()

    @override_settings(DEBUG=False, TESTING=False)
    def test_core_sentry_error_logging(self):
        # sentry is not active during unittests / debug
        init_openmodule(self.zmq_config())
        self.wait_for_health()

        try:
            core().log.error("some-error-message")
            sentry_message = self.zmq_client.wait_for_message_on_topic("sentry")
            self.assertIn("some-error-message", str(sentry_message))
        finally:
            shutdown_openmodule()

    def test_core_alerts(self):
        init_openmodule(self.zmq_config())
        self.wait_for_health()

        try:
            core().alerts.send("some_type", AlertHandleType.state_change)
            self.assertAlert(alert_type="some_type")
        finally:
            shutdown_openmodule()

    def test_shutdown_wait_for_message_handling(self):
        def handler(_):
            nonlocal error
            handler_started.set()
            if shutdown_finished.wait(timeout=3):
                error = "shutdown finished while message was still being handled"
                return
            if core().messages._shutdown:
                error = "shutdown flag was set while message was still being handled"

        error = ""
        handler_started = threading.Event()
        shutdown_finished = threading.Event()
        init_openmodule(self.zmq_config())
        self.wait_for_health()
        core().messages.register_handler("test", ZMQMessage, handler, register_schema=False, match_type=False)
        core().publish(ZMQMessage(type="test"), "test")
        self.assertTrue(handler_started.wait(timeout=3))
        try:
            core().shutdown()
            shutdown_finished.set()
            self.assertEqual(error, "")
        finally:
            shutdown_openmodule()

    def test_no_message_submit_after_shutdown(self):
        def dispatch_wrapper(topic, message):
            nonlocal error
            dispatch_started.set()
            if not shutdown_done.wait(timeout=3):
                error = "shutdown did not finish when expected"
            original_dispatch(topic, message)
            dispatch_done.set()

        error = ""
        dispatch_started = threading.Event()
        dispatch_done = threading.Event()
        shutdown_done = threading.Event()
        init_openmodule(self.zmq_config())
        self.wait_for_health()
        original_dispatch = core().messages.dispatch
        handler = mock.MagicMock()
        core().messages.dispatch = dispatch_wrapper

        core().messages.register_handler("test", ZMQMessage, handler, register_schema=False, match_type=False)
        core().publish(ZMQMessage(type="test"), "test")
        self.assertTrue(dispatch_started.wait(timeout=3))
        try:
            with mock.patch("zmq.Context.term", side_effect=shutdown_done.set):
                core().shutdown()
            self.assertTrue(dispatch_done.wait(timeout=3))
            self.assertFalse(handler.called)
            self.assertEqual(error, "")
        finally:
            shutdown_openmodule()
