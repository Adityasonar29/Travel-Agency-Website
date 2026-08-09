from django.core.management.base import BaseCommand
from apps.booking.models import Booking


class Command(BaseCommand):

    help = 'Automatically complete confirmed journeys that have ended.'

    def handle(self, *args, **options):

        bookings = Booking.objects.filter(
            status='confirmed'
        )

        completed_count = 0

        for booking in bookings:

            if booking.update_completion_status():
                completed_count += 1

                self.stdout.write(
                    self.style.SUCCESS(
                        f'Completed {booking.booking_id}'
                    )
                )

        self.stdout.write(
            self.style.SUCCESS(
                f'{completed_count} booking(s) completed.'
            )
        )