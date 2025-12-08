from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
    help = "Promote an existing user to enterprise-catalog superadmin"

    def add_arguments(self, parser):
        parser.add_argument(
            "--username",
            dest="username",
            help="Username of the existing user to promote",
        )
        parser.add_argument(
            "--email",
            dest="email",
            help="Email address to confirm/assign to the user (optional but recommended)",
        )

    def handle(self, *args, **options):
        User = get_user_model()

        username = options.get("username") or input("Username: ").strip()
        email = options.get("email")

        if not username:
            raise CommandError("Username is required")

        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            raise CommandError(f"User '{username}' does not exist in enterprise-catalog DB")

        if email:
            if user.email != email:
                user.email = email
                self.stdout.write(f"Updated email for '{username}' to '{email}'")
        elif not user.email:
            # prompt if no email and none provided
            email_input = input("User has no email set. Enter one now (or leave blank to skip): ").strip()
            if email_input:
                user.email = email_input
                self.stdout.write(f"Updated email for '{username}' to '{email_input}'")

        user.is_staff = True
        user.is_superuser = True
        user.save()

        self.stdout.write(self.style.SUCCESS(f"User '{username}' promoted to enterprise-catalog superadmin"))
