from django.db.models import Q
from rest_framework.response import Response
from rest_framework.views import APIView
from ..auth.permissions import HasRoutePermission
from ...models import Dealer
from .permissions import DEALER_CREATE, DEALER_DELETE, DEALER_READ, DEALER_UPDATE
from .serializers import dealer_payload, serialize_dealer

class DealerListView(APIView):
    permission_classes = [HasRoutePermission]
    required_permissions = {"GET": DEALER_READ, "POST": DEALER_CREATE}
    def get(self, request):
        queryset = Dealer.objects.all(); query = request.query_params.get("q", "").strip(); dealer_type = request.query_params.get("type", "").strip()
        if query: queryset = queryset.filter(Q(name__icontains=query) | Q(code__icontains=query) | Q(province_city__icontains=query) | Q(address__icontains=query))
        if dealer_type in dict(Dealer.TYPE_CHOICES): queryset = queryset.filter(dealer_type=dealer_type)
        return Response([serialize_dealer(item) for item in queryset[:500]])
    def post(self, request):
        payload, error = dealer_payload(request.data)
        if error: return Response({"detail": error}, status=400)
        try: item = Dealer.objects.create(**payload)
        except Exception: return Response({"detail": "A dealer with this code may already exist."}, status=400)
        return Response(serialize_dealer(item), status=201)

class DealerDetailView(APIView):
    permission_classes = [HasRoutePermission]
    required_permissions = {"PATCH": DEALER_UPDATE, "DELETE": DEALER_DELETE}
    def patch(self, request, dealer_id):
        item = Dealer.objects.filter(pk=dealer_id).first()
        if not item: return Response({"detail": "Dealer not found."}, status=404)
        payload, error = dealer_payload(request.data)
        if error: return Response({"detail": error}, status=400)
        for key, value in payload.items(): setattr(item, key, value)
        try: item.full_clean(); item.save()
        except Exception: return Response({"detail": "A dealer with this code may already exist."}, status=400)
        return Response(serialize_dealer(item))
    def delete(self, request, dealer_id):
        deleted, _ = Dealer.objects.filter(pk=dealer_id).delete()
        return Response(status=204) if deleted else Response({"detail": "Dealer not found."}, status=404)