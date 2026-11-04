"""Long-running Heroku worker for Oracle A1 capacity retries.

The OCI launch function already retries retryable OCI errors using
REQUEST_WAIT_TIME_SECS. After an instance exists, periodically re-check
so daily Heroku dyno cycling is safe and no duplicate success email is sent.
"""
import time
import logging

import main

CHECK_INTERVAL_SECONDS = 60 * 60

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")


def run():
    while True:
        logging.info("Checking OCI for an existing A1 instance or available capacity.")
        main.launch_instance()
        logging.info(
            "An A1 instance exists. Will check again in %s seconds.",
            CHECK_INTERVAL_SECONDS,
        )
        time.sleep(CHECK_INTERVAL_SECONDS)


if __name__ == "__main__":
    run()
