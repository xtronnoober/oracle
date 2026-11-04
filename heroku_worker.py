"""Long-running Heroku worker for Oracle A1 capacity retries.

OCI capacity errors are retried inside main.launch_instance() every
REQUEST_WAIT_TIME_SECS seconds. Once an instance exists, this process stays
alive and periodically verifies that state.
"""
import logging
import sys
import time
import traceback

# Import main only after stdout logging is configured. main.py also configures
# file handlers; we explicitly add stdout handlers so Heroku captures logs.
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s [%(name)s] %(message)s",
    stream=sys.stdout,
    force=True,
)
logging.getLogger().setLevel(logging.INFO)

logging.info("Heroku Oracle worker booting; Python=%s", sys.version.split()[0])
logging.info("Importing OCI application module.")

try:
    import main
except Exception:
    logging.exception("Failed while importing main.py / initializing OCI clients.")
    raise

# main.py has its own launch_instance logger with a file handler. Add a
# stdout handler to that logger as well.
oci_logger = logging.getLogger("launch_instance")
oci_logger.setLevel(logging.INFO)
if not any(getattr(handler, "_heroku_stdout", False) for handler in oci_logger.handlers):
    stream_handler = logging.StreamHandler(sys.stdout)
    stream_handler.setLevel(logging.INFO)
    stream_handler.setFormatter(logging.Formatter(
        "%(asctime)s %(levelname)s [%(name)s] %(message)s"
    ))
    stream_handler._heroku_stdout = True
    oci_logger.addHandler(stream_handler)

CHECK_INTERVAL_SECONDS = 60 * 60


def run():
    logging.info("OCI SDK initialized. Starting instance/capacity check.")
    while True:
        try:
            logging.info("Calling main.launch_instance().")
            main.launch_instance()
            logging.info(
                "launch_instance() returned; checking again in %s seconds.",
                CHECK_INTERVAL_SECONDS,
            )
            time.sleep(CHECK_INTERVAL_SECONDS)
        except KeyboardInterrupt:
            logging.info("Shutdown signal received; exiting worker.")
            raise
        except Exception:
            logging.exception("Unexpected worker error; restarting check in 120 seconds.")
            time.sleep(120)


if __name__ == "__main__":
    run()
