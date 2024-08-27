import io
import logging
from unittest import TestCase, mock

import openmodule.logging


class LoggingTestCase(TestCase):
    def test_logging_to_stdout(self):
        logging.basicConfig(force=True)  # reset logging
        stdout = io.StringIO()
        stderr = io.StringIO()
        with mock.patch("sys.stdout.write", stdout.write), mock.patch("sys.stderr.write", stderr.write):
            logging.warning("test")
        self.assertNotIn("test", stdout.getvalue())
        self.assertIn("test", stderr.getvalue())

        core = mock.MagicMock()
        core.config.LOG_LEVEL = logging.INFO
        for h in logging.root.handlers[:]:  # reset logging again
            logging.root.removeHandler(h)
            h.close()
        openmodule.logging.init_logging(core)
        stdout = io.StringIO()
        stderr = io.StringIO()
        with mock.patch("sys.stdout.write", stdout.write), mock.patch("sys.stderr.write", stderr.write):
            logging.warning("test")
        self.assertIn("test", stdout.getvalue())
        self.assertNotIn("test", stderr.getvalue())
