from base64 import b64decode
from pathlib import Path

import environ

from libnftinema.structs import ClientKey

BASE_DIR = Path(__file__).resolve().parent.parent

env = environ.Env()


SECRET_KEY = "your_secret_key"
INSTALLED_APPS = [
    "django.contrib.contenttypes",
    "django.contrib.auth",
    "libnftinema.testapp",
]
AUTH_USER_MODEL = "testapp.TestUser"
MIDDLEWARE = []
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": ":memory:",
    },
}
USE_I18N = False
USE_L10N = False
USE_TZ = False

ROOT_URLCONF = "libnftinema.testapp.urls"

NFTINEMA_CHECK_API_CLIENT_HANDLER = env.str(
    "NFTINEMA_CHECK_API_CLIENT_HANDLER",
    "libnftinema.testapp.handlers.check_api_client_test",
)


NFTINEMA_CLIENT_KEY = ClientKey(
    "eyJhbGciOiJub25lIiwidHlwIjoiSldUIn0.eyJrdHkiOiJvY3QiLCJrIjoiRGZra3h1ZVZTVnl3TmJfSW9lVU5WOG5fUjBFclcwVUVtaTB6aGRCY01TVSIsImFsZyI6IkhTMjU2Iiwia2lkIjoiYXBpX2NsaWVudF9Bb1l6blB6ckhNTXY0b1IydkZqU1FDIn0.",
)

PASSPORT_PUBLIC_KEY = b64decode(
    "LS0tLS1CRUdJTiBQVUJMSUMgS0VZLS0tLS0KTUlJQklqQU5CZ2txaGtpRzl3MEJBUUVGQUFPQ0FROEFNSUlCQ2dLQ0FRRUFzTFBMd2lPSlc2Zk9VRG9GSy9KMAp6SG9oQTdlTzBoQ2YrOXBFWGsrdWpURS9td2xHVDBYUXRUMEo4ZWIwT2NNOUo4NGdSYndVYTBpQnBaMWJnQTA5CnBnQWNJeFVzSmt4M1dKVHI5cW9kTzd4d2FHQ3FWVlEwMjZIR2FmNGZrSUE5YTUrQWF2S2NTeFVTdURmK2JMUHMKNkNtQXJEZ2ZGQ1R3VUtwWFdQdWNLWEdFeDIwRURUZTdTYnNYTEI3UUIvUXFpekVCUnk1cE10VThLaGtpb0ZUcQowOElLd3lSQU1ZbWxzUlRZWWIwRHlQWGtsazlab3VMdFNYTkZabHFqWS9qTnpESHZTbTlwaUhSZnpHN0pZUWYrCk1rVVQzWmJwWEZORjBwSFlFRTkrcTYvYThlMjNwYnA2cFFyNVo4Sk5hSi96cHhRSXJkOThwWDAyZ25tYVVmZzYKR1FJREFRQUIKLS0tLS1FTkQgUFVCTElDIEtFWS0tLS0t",
).decode()

USER_JWT = "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJpYXQiOjE3MjQxMTQyOTgsImV4cCI6MjAzOTQ3NDI5OCwidXNlcl91dWlkIjoiMTQ3Zjk0MzQtY2Q5NS00ZmFhLWJmNjgtZTYyMTk5YzYxOTFkIiwidGFyZ2V0X2FjY2VzcyI6Im1haW4iLCJjb3VudHJ5X2lzbyI6IlVTIn0.GXwf5taLnyfqaCx7QI00HCaU0ddHFJUUxNe9Ld7DDIkMxTmjMaNkeevibbaQ_9TXLgrD3xH6oor6Pi0sEtqJzh1pgqnpwlZVxsHfM8cnJCdYiTM1xqFHziwSvXMhM4Hkt6HCq8G6njqB-nWzeoKyWhfTRu-HVOOy5zEzUm4AqQfGM6CMDW4m1G90TvsSrrqzuBdTDddqoPcDwAeyzJ5xV3XlWEXiMruGzSCaMpDUimGCXKdYulUEm0q_u9ETNzpatq-WSKQLvo3331vuZ9UjVTe_P3ahV0YSN4yFBYBbdeyoNdbzr8L5BdowNryBnc6AvFWzWgRy290wvg96gWRWGw"
