import logging
import time

from django.core.management.base import BaseCommand
from django.db import close_old_connections

from apps.core.utils.email_queue import process_next_email

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Continuously deliver queued email and retry temporary failures."

    def add_arguments(self, parser):
        parser.add_argument(
            "--poll-interval",
            type=float,
            default=2,
            help="Seconds to wait when no email is ready (default: 2).",
        )
        parser.add_argument(
            "--once",
            action="store_true",
            help="Process due emails and exit when the queue is empty.",
        )

    def handle(self, *args, **options):
        poll_interval = options["poll_interval"]
        if poll_interval <= 0:
            raise ValueError("--poll-interval must be greater than zero.")

        self.stdout.write("Email queue worker started.")
        while True:
            close_old_connections()
            try:
                processed = process_next_email()
            except Exception:
                logger.exception("Email queue worker iteration failed.")
                processed = False
            finally:
                close_old_connections()

            if options["once"]:
                if not processed:
                    return
            elif not processed:
                time.sleep(poll_interval)
