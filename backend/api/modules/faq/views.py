from django.db.models import Prefetch, Q
from rest_framework.response import Response
from rest_framework.views import APIView
from ..auth.permissions import HasRoutePermission
from ...models import FAQCategory, FAQQuestion
from .permissions import FAQ_CREATE, FAQ_DELETE, FAQ_READ, FAQ_UPDATE
from .serializers import category_payload, question_payload, serialize_category, serialize_question

class FAQCategoryListView(APIView):
    permission_classes = [HasRoutePermission]
    required_permissions = {"GET": FAQ_READ, "POST": FAQ_CREATE}
    def get(self, request):
        queryset = FAQCategory.objects.prefetch_related(Prefetch("questions", queryset=FAQQuestion.objects.all()))
        query = request.query_params.get("q", "").strip()
        if query: queryset = queryset.filter(Q(name__icontains=query) | Q(questions__question_vi__icontains=query)).distinct()
        return Response([serialize_category(item) for item in queryset])
    def post(self, request):
        payload, error = category_payload(request.data)
        if error: return Response({"detail": error}, status=400)
        try: item = FAQCategory.objects.create(**payload)
        except Exception: return Response({"detail": "A FAQ category with this slug may already exist."}, status=400)
        return Response(serialize_category(item), status=201)

class FAQCategoryDetailView(APIView):
    permission_classes = [HasRoutePermission]
    required_permissions = {"PATCH": FAQ_UPDATE, "DELETE": FAQ_DELETE}
    def patch(self, request, category_id):
        item = FAQCategory.objects.filter(pk=category_id).first()
        if not item: return Response({"detail": "FAQ category not found."}, status=404)
        payload, error = category_payload(request.data)
        if error: return Response({"detail": error}, status=400)
        for key, value in payload.items(): setattr(item, key, value)
        try: item.full_clean(); item.save()
        except Exception: return Response({"detail": "A FAQ category with this slug may already exist."}, status=400)
        return Response(serialize_category(item))
    def delete(self, request, category_id):
        deleted, _ = FAQCategory.objects.filter(pk=category_id).delete()
        return Response(status=204) if deleted else Response({"detail": "FAQ category not found."}, status=404)

class FAQQuestionListView(APIView):
    permission_classes = [HasRoutePermission]
    required_permissions = {"POST": FAQ_CREATE}
    def post(self, request):
        payload, error = question_payload(request.data)
        if error: return Response({"detail": error}, status=400)
        return Response(serialize_question(FAQQuestion.objects.create(**payload)), status=201)

class FAQQuestionDetailView(APIView):
    permission_classes = [HasRoutePermission]
    required_permissions = {"PATCH": FAQ_UPDATE, "DELETE": FAQ_DELETE}
    def patch(self, request, question_id):
        item = FAQQuestion.objects.filter(pk=question_id).first()
        if not item: return Response({"detail": "FAQ question not found."}, status=404)
        payload, error = question_payload(request.data)
        if error: return Response({"detail": error}, status=400)
        for key, value in payload.items(): setattr(item, key, value)
        item.save()
        return Response(serialize_question(item))
    def delete(self, request, question_id):
        deleted, _ = FAQQuestion.objects.filter(pk=question_id).delete()
        return Response(status=204) if deleted else Response({"detail": "FAQ question not found."}, status=404)