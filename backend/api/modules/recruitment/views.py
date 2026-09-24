from django.db.models import Q
from rest_framework.response import Response
from rest_framework.views import APIView

from ..auth.permissions import HasRoutePermission
from ...models import Dealer, ProductTag, RecruitmentArea, RecruitmentDepartment, RecruitmentJob, RecruitmentRegion
from .permissions import *
from .serializers import job_payload, serialize_job, serialize_taxonomy, taxonomy_payload


class RecruitmentListView(APIView):
    permission_classes = [HasRoutePermission]
    required_permissions = {"GET": RECRUITMENT_READ, "POST": RECRUITMENT_CREATE}

    def get(self, request):
        queryset = RecruitmentJob.objects.all()
        query = request.query_params.get("q", "").strip()
        if query:
            queryset = queryset.filter(Q(title__icontains=query) | Q(department__icontains=query) | Q(location__icontains=query))
        if request.query_params.get("status"):
            queryset = queryset.filter(status=request.query_params["status"])
        return Response([serialize_job(item) for item in queryset[:200]])

    def post(self, request):
        payload, error = job_payload(request.data)
        if error:
            return Response({"detail": error}, status=400)
        try:
            tag_ids = payload.pop("tag_ids"); job = RecruitmentJob.objects.create(**payload); job.managed_tags.set(ProductTag.objects.filter(id__in=tag_ids))
        except Exception:
            return Response({"detail": "A recruitment job with this slug may already exist."}, status=400)
        return Response(serialize_job(job), status=201)


class RecruitmentDetailView(APIView):
    permission_classes = [HasRoutePermission]
    required_permissions = {"GET": RECRUITMENT_READ, "PATCH": RECRUITMENT_UPDATE, "DELETE": RECRUITMENT_DELETE}

    def get(self, request, job_id):
        job = RecruitmentJob.objects.filter(pk=job_id).first()
        return Response(serialize_job(job)) if job else Response({"detail": "Recruitment job not found."}, status=404)

    def patch(self, request, job_id):
        job = RecruitmentJob.objects.filter(pk=job_id).first()
        if not job:
            return Response({"detail": "Recruitment job not found."}, status=404)
        payload, error = job_payload(request.data)
        if error:
            return Response({"detail": error}, status=400)
        try:
            tag_ids = payload.pop("tag_ids"); department_ref_id = payload.pop("department_ref_id"); payload["department_ref_id"] = department_ref_id
            for key, value in payload.items(): setattr(job, key, value)
            job.full_clean(); job.save()
            job.managed_tags.set(ProductTag.objects.filter(id__in=tag_ids))
        except Exception:
            return Response({"detail": "A recruitment job with this slug may already exist."}, status=400)
        return Response(serialize_job(job))

    def delete(self, request, job_id):
        deleted, _ = RecruitmentJob.objects.filter(pk=job_id).delete()
        return Response(status=204) if deleted else Response({"detail": "Recruitment job not found."}, status=404)


class RecruitmentTaxonomyListView(APIView):
    permission_classes = [HasRoutePermission]
    model = RecruitmentDepartment
    required_permissions = {"GET": RECRUITMENT_DEPARTMENT_READ, "POST": RECRUITMENT_DEPARTMENT_CREATE}

    def get(self, request): return Response([serialize_taxonomy(item) for item in self.model.objects.all()])
    def post(self, request):
        payload, error = taxonomy_payload(request.data)
        if error: return Response({"detail": error}, status=400)
        try: item = self.model.objects.create(**payload)
        except Exception: return Response({"detail": "Name or slug already exists."}, status=400)
        return Response(serialize_taxonomy(item), status=201)


class RecruitmentTaxonomyDetailView(APIView):
    permission_classes = [HasRoutePermission]
    model = RecruitmentDepartment
    required_permissions = {"PATCH": RECRUITMENT_DEPARTMENT_UPDATE, "DELETE": RECRUITMENT_DEPARTMENT_DELETE}

    def patch(self, request, item_id):
        item = self.model.objects.filter(pk=item_id).first()
        if not item: return Response({"detail": "Item not found."}, status=404)
        payload, error = taxonomy_payload(request.data)
        if error: return Response({"detail": error}, status=400)
        for key, value in payload.items(): setattr(item, key, value)
        try: item.save()
        except Exception: return Response({"detail": "Name or slug already exists."}, status=400)
        return Response(serialize_taxonomy(item))

    def delete(self, request, item_id):
        deleted, _ = self.model.objects.filter(pk=item_id).delete()
        return Response(status=204) if deleted else Response({"detail": "Item not found."}, status=404)


class RecruitmentRegionListView(APIView):
    permission_classes = [HasRoutePermission]
    required_permissions = {"GET": RECRUITMENT_READ}

    def get(self, request):
        return Response([{"id": item.id, "name": item.name} for item in RecruitmentRegion.objects.filter(status=1)])

    def post(self, request):
        payload, error = taxonomy_payload(request.data)
        if error: return Response({"detail": error}, status=400)
        try: item = RecruitmentRegion.objects.create(**payload)
        except Exception: return Response({"detail": "Region name or slug already exists."}, status=400)
        return Response({"id": item.id, "name": item.name, "slug": item.slug, "status": item.status}, status=201)


class RecruitmentRegionDetailView(APIView):
    permission_classes = [HasRoutePermission]
    required_permissions = {"PATCH": RECRUITMENT_DEPARTMENT_UPDATE, "DELETE": RECRUITMENT_DEPARTMENT_DELETE}

    def patch(self, request, item_id):
        item = RecruitmentRegion.objects.filter(pk=item_id).first()
        if not item: return Response({"detail": "Region not found."}, status=404)
        payload, error = taxonomy_payload(request.data)
        if error: return Response({"detail": error}, status=400)
        for key, value in payload.items(): setattr(item, key, value)
        try: item.save()
        except Exception: return Response({"detail": "Region name or slug already exists."}, status=400)
        return Response({"id": item.id, "name": item.name, "slug": item.slug, "status": item.status})

    def delete(self, request, item_id):
        deleted, _ = RecruitmentRegion.objects.filter(pk=item_id).delete()
        return Response(status=204) if deleted else Response({"detail": "Region not found."}, status=404)


class RecruitmentAreaListView(APIView):
    permission_classes = [HasRoutePermission]
    required_permissions = {"GET": RECRUITMENT_READ}

    def get(self, request):
        queryset = RecruitmentArea.objects.filter(status=1)
        if request.query_params.get("region_id"):
            queryset = queryset.filter(region_id=request.query_params["region_id"])
        return Response([{"id": item.id, "name": item.name, "region_id": item.region_id} for item in queryset])

    def post(self, request):
        payload, error = taxonomy_payload(request.data)
        if error: return Response({"detail": error}, status=400)
        try: region_id = int(request.data.get("region_id"))
        except (TypeError, ValueError): return Response({"detail": "Region is required."}, status=400)
        if not RecruitmentRegion.objects.filter(pk=region_id, status=1).exists(): return Response({"detail": "Region is invalid."}, status=400)
        try: item = RecruitmentArea.objects.create(region_id=region_id, **payload)
        except Exception: return Response({"detail": "Area already exists in this region."}, status=400)
        return Response({"id": item.id, "name": item.name, "slug": item.slug, "status": item.status, "region_id": item.region_id}, status=201)


class RecruitmentAreaDetailView(APIView):
    permission_classes = [HasRoutePermission]
    required_permissions = {"PATCH": RECRUITMENT_DEPARTMENT_UPDATE, "DELETE": RECRUITMENT_DEPARTMENT_DELETE}

    def patch(self, request, item_id):
        item = RecruitmentArea.objects.filter(pk=item_id).first()
        if not item: return Response({"detail": "Area not found."}, status=404)
        payload, error = taxonomy_payload(request.data)
        if error: return Response({"detail": error}, status=400)
        try: region_id = int(request.data.get("region_id", item.region_id))
        except (TypeError, ValueError): return Response({"detail": "Region is invalid."}, status=400)
        if not RecruitmentRegion.objects.filter(pk=region_id, status=1).exists(): return Response({"detail": "Region is invalid."}, status=400)
        for key, value in payload.items(): setattr(item, key, value)
        item.region_id = region_id
        try: item.save()
        except Exception: return Response({"detail": "Area already exists in this region."}, status=400)
        return Response({"id": item.id, "name": item.name, "slug": item.slug, "status": item.status, "region_id": item.region_id})

    def delete(self, request, item_id):
        deleted, _ = RecruitmentArea.objects.filter(pk=item_id).delete()
        return Response(status=204) if deleted else Response({"detail": "Area not found."}, status=404)


class RecruitmentBusinessUnitListView(APIView):
    permission_classes = [HasRoutePermission]
    required_permissions = {"GET": RECRUITMENT_READ}

    def get(self, request):
        queryset = Dealer.objects.filter(status=1, province_city__isnull=False).exclude(province_city="")
        area_id = request.query_params.get("area_id")
        if area_id:
            queryset = queryset.filter(area_id=area_id)
        return Response([{"id": item.id, "name": item.name, "area_id": item.area_id} for item in queryset])


RecruitmentDepartmentListView = RecruitmentTaxonomyListView
RecruitmentDepartmentDetailView = RecruitmentTaxonomyDetailView