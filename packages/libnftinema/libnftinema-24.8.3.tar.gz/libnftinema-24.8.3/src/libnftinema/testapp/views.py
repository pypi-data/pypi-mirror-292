from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from libnftinema.server import DrfAuth


class SimpleGetView(APIView):
    def get(self, request):
        return Response(
            {"message": "Simple GET view"}, status=200, content_type="application/json"
        )


class SercurePostView(APIView):
    authentication_classes = [DrfAuth]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        data = request.data

        user = None
        if request.user:
            u = request.user
            user = {
                "uuid": f"{u.uuid}",
                "username": u.username,
                "email": u.email,
                "is_active": u.is_active,
                "is_staff": u.is_staff,
                "is_superuser": u.is_superuser,
            }

        return Response(
            {"message": "Data received", "data": data, "user": user},
            status=200,
            content_type="application/json",
        )
