from django.utils.text import slugify

from ...models import RecruitmentArea, RecruitmentDepartment, RecruitmentJob, RecruitmentRegion, ProductTag, Dealer


def serialize_job(job):
    department = job.department_ref
    return {"id": job.id, "title": job.title, "slug": job.slug, "department": job.business_unit.name if job.business_unit else (department.name if department else job.department), "department_id": department.id if department else None, "region": job.region.name if job.region else "", "region_id": job.region_id, "area": job.area.name if job.area else "", "area_id": job.area_id, "business_unit": job.business_unit.name if job.business_unit else "", "business_unit_id": job.business_unit_id, "location": job.location, "employment_type": job.employment_type, "description": job.description, "requirements": job.requirements, "benefits": job.benefits, "deadline": job.deadline.isoformat() if job.deadline else None, "status": job.status, "status_label": job.get_status_display(), "tags": [tag.name for tag in job.managed_tags.all()], "tag_ids": list(job.managed_tags.values_list("id", flat=True))}


def job_payload(data):
    title = str(data.get("title") or "").strip()
    slug = str(data.get("slug") or slugify(title)).strip()
    if not title or not slug:
        return None, "Title and slug are required."
    try:
        status = int(data.get("status", RecruitmentJob.STATUS_DRAFT))
    except (TypeError, ValueError):
        return None, "Status must be a valid number."
    if status not in dict(RecruitmentJob.STATUS_CHOICES):
        return None, "Invalid recruitment status."
    department_id = data.get("department_id") or None
    try: department_id = int(department_id) if department_id else None
    except (TypeError, ValueError): return None, "Department must be valid."
    ids = {}
    for key in ("region_id", "area_id", "business_unit_id"):
        try: ids[key] = int(data.get(key)) if data.get(key) else None
        except (TypeError, ValueError): return None, "Location selection must be valid."
    if ids["area_id"] and not RecruitmentArea.objects.filter(id=ids["area_id"], status=1).exists():
        return None, "Area must be valid."
    if ids["region_id"] and ids["area_id"] and not RecruitmentArea.objects.filter(id=ids["area_id"], region_id=ids["region_id"], status=1).exists():
        return None, "Area must belong to the selected region."
    if ids["business_unit_id"] and not Dealer.objects.filter(id=ids["business_unit_id"], status=1).exists():
        return None, "Business unit must be valid."
    if ids["business_unit_id"] and ids["area_id"] and not Dealer.objects.filter(id=ids["business_unit_id"], area_id=ids["area_id"], status=1).exists():
        return None, "Business unit must belong to the selected area."
    tag_ids = data.get("tag_ids") or []
    if not isinstance(tag_ids, list): return None, "Tags must be a list."
    try: tag_ids = [int(tag_id) for tag_id in tag_ids]
    except (TypeError, ValueError): return None, "Tags must be valid."
    business_unit = Dealer.objects.filter(id=ids["business_unit_id"], status=1).first() if ids["business_unit_id"] else None
    return {"title": title[:255], "slug": slug[:280], "department": business_unit.name if business_unit else str(data.get("department") or "")[:160], "department_ref_id": department_id, **ids, "location": str(data.get("location") or "")[:160], "employment_type": str(data.get("employment_type") or "")[:80], "description": str(data.get("description") or ""), "requirements": str(data.get("requirements") or ""), "benefits": str(data.get("benefits") or ""), "deadline": data.get("deadline") or None, "status": status, "tag_ids": tag_ids}, None


def serialize_taxonomy(item):
    return {"id": item.id, "name": item.name, "slug": item.slug, "status": item.status, "usage_count": item.jobs.count()}


def taxonomy_payload(data):
    name = str(data.get("name") or "").strip()
    slug = str(data.get("slug") or slugify(name)).strip()
    return ({"name": name[:160], "slug": slug[:180], "status": int(data.get("status", 1))}, None) if name and slug else (None, "Name is required.")