from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView


class HealthCheckAPI(APIView):
    permission_classes = (AllowAny,)
    
    """
    HealthCheck endpoint is kept public (AllowAny) so that load balancers 
    and uptime monitoring services can verify backend availability without authentication.
    """

    def get(self, request):
        from utils.response.resp import APIResponse
        return Response(APIResponse.get_response(data={"status": "OK"}))
