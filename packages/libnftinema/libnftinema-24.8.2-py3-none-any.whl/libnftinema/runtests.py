import os

import django
import pytest
from django.core.management import call_command

os.environ["DJANGO_SETTINGS_MODULE"] = "libnftinema.test_settings"
django.setup()

# Run migrations
call_command("makemigrations", "testapp")
call_command("migrate")

# Run tests
pytest.main(["src/libnftinema/test_client.py"])
pytest.main(["src/libnftinema/test_server.py"])
