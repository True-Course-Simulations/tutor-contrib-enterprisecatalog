from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand, CommandError
from getpass import getpass


class Command(BaseCommand):
    help = "Create or update an enterprise-catalog superadmin user"

    def add_arguments(self, parser):
        parser.add_argument(
            "--username",
            dest="username",
            help="Username of the superadmin to create or update",
        )
        parser.add_argument(
            "--email",
            dest="email",
            help="Email address of the superadmin",
        )
        parser.add_argument(
            "--password",
            dest="password",
            help="Password for the superadmin. Omit to set no password (for SSO only).",
        )
        parser.add_argument(
            "--no-password",
            action="store_true",
            dest="no_password",
            default=False,
            help="Create/update the user with an unusable password (SSO-only).",
        )

    def handle(self, *args, **options):
        User = get_user_model()

        username = options.get("username") or input("Username: ").strip()
        email = options.get("email") or input("Email: ").strip()
        password = options.get("password")
        no_password = options.get("no_password")

        if not username:
            raise CommandError("Username is required")
        if not email:
            raise CommandError("Email is required")

        if password and no_password:
            raise CommandError("Cannot use --password and --no-password at the same time")

        # Interactive password prompt if neither is set
        if not password and not no_password:
            self.stdout.write(self.style.WARNING("No password provided."))
            if input("Do you want to set a password now? [y/N]: ").lower() == "y":
                password = getpass("Password: ")
            else:
                no_password = True

        user, created = User.objects.get_or_create(username=username, defaults={"email": email})

        if created:
            self.stdout.write(self.style.SUCCESS(f"Created user '{username}'"))
        else:
            # Update email if changed
            if user.email != email:
                user.email = email
                self.stdout.write(f"Updated email for '{username}' to '{email}'")

        # Ensure staff/superuser flags
        user.is_staff = True
        user.is_superuser = True

        # Handle password
        if password:
            user.set_password(password)
            self.stdout.write("Set local password.")
        elif no_password:
            user.set_unusable_password()
            self.stdout.write("Set unusable password (SSO-only account).")

        user.save()

        self.stdout.write(self.style.SUCCESS(f"Enterprise-catalog superadmin ensured: {username}"))
