from django.core.management.base import BaseCommand
from django.core.mail import EmailMultiAlternatives
from django.conf import settings
from django.contrib.auth.models import User
from django.db import transaction
from datetime import datetime, timedelta
import smtplib
from cms.models import EmailLog


class Command(BaseCommand):
    help = "Notify users inactive for more than X years or before a given cutoff date."

    def add_arguments(self, parser):

        parser.add_argument(
            "--years",
            type=int,
            default=5,
            help="Check inactivity older than this many years (default = 5). Ignored if --cutoff-date provided.",
        )

        parser.add_argument(
            "--limit",
            type=int,
            default=None,
            help="Limit number of users to notify",
        )

        parser.add_argument(
            "--cutoff-date",
            type=str,
            default=None,
            help="Custom cutoff date in YYYY-MM-DD format (overrides --years)",
        )

    @transaction.atomic
    def handle(self, *args, **options):

        years = options.get("years")
        limit = options.get("limit")
        cutoff_input = options.get("cutoff_date")

        if cutoff_input:
            try:
                cutoff_date = datetime.strptime(cutoff_input, "%Y-%m-%d")
            except ValueError:
                self.stdout.write(self.style.ERROR(
                    "❌ Invalid cutoff date format! Use YYYY-MM-DD"
                ))
                return
        else:
            cutoff_date = datetime.now() - timedelta(days=years * 365)

        cutoff_str = cutoff_date.strftime("%Y-%m-%d")
        self.stdout.write(self.style.WARNING(
            f"\n📅 Using cutoff date: {cutoff_str} (YYYY-MM-DD)\n"
        ))

        users = User.objects.filter(
            last_login__lt=cutoff_date,
            is_active=True
        ).order_by("id")

        if limit:
            users = users[:limit]

        total_users = users.count()
        self.stdout.write(self.style.NOTICE(
            f"🔎 Users inactive since before {cutoff_str}: {total_users}\n"
        ))

        subject = "Reminder: Your account has been inactive for a long time"

        sent_count = 0
        failed_count = 0
        for user in users:

            message = f"""
Dear {user.first_name} {user.last_name},

Our system indicates that your account has not been used for a long time.

Your last login was on: {user.last_login.strftime("%Y-%m-%d")}

This is a reminder to log in again and continue using our services.

If you need help, simply reply to this email.

Regards,
Support Team
"""

            email = EmailMultiAlternatives(
                subject,
                message,
                settings.NO_REPLY_EMAIL,
                to=[user.email],
            )

            try:
                email.send(fail_silently=False)

                sent_count += 1

                EmailLog.objects.create(
                    user=user,
                    email=user.email,
                    status=True,
                    reason=None
                )

                self.stdout.write(self.style.SUCCESS(f"[SENT] {user.email}"))

            except (smtplib.SMTPException, Exception) as e:

                failed_count += 1

                EmailLog.objects.create(
                    user=user,
                    email=user.email,
                    status=False,
                    reason=str(e)
                )

                self.stdout.write(self.style.ERROR(f"[FAILED] {user.email} → {e}"))

        self.stdout.write("\n---------------------------------------")
        self.stdout.write(self.style.SUCCESS(f"Emails Sent: {sent_count}"))
        self.stdout.write(self.style.ERROR(f"Failed: {failed_count}"))
        self.stdout.write(self.style.WARNING(f"Total Processed: {total_users}"))
        self.stdout.write(self.style.NOTICE(f"Cutoff Date Used: {cutoff_str}"))
        self.stdout.write("---------------------------------------\n")
