#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys


def main():
    """Run administrative tasks."""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hr_saas.settings')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    import os
    if os.environ.get('CREATE_SUPERUSER', '') == '1':
        from django.contrib.auth import get_user_model
        User = get_user_model()
        username = "ktamangsuper"
        email = "ktamang@gmail.com"
        password = "Dilanjali"
        if not User.objects.filter(username=username).exists():
            User.objects.create_superuser(username, email, password)
            print("Superuser created!")
        else:
            print("Superuser already exists.")
    main()
