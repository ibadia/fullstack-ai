from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView


class HealthCheckAPI(APIView):
    permission_classes = (AllowAny,)

    
    def get(self, request):
        status = {"status": "OK"}
        return Response(status)
