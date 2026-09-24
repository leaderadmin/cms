from django.utils.text import slugify
from ...models import FAQCategory, FAQQuestion

def serialize_question(item):
    return {"id": item.id, "category_id": item.category_id, "question_vi": item.question_vi, "answer_vi": item.answer_vi, "question_en": item.question_en, "answer_en": item.answer_en, "ordering": item.ordering, "status": item.status}

def serialize_category(item):
    return {"id": item.id, "name": item.name, "slug": item.slug, "ordering": item.ordering, "status": item.status, "questions": [serialize_question(question) for question in item.questions.all()]}

def category_payload(data):
    name = str(data.get("name") or "").strip()
    slug = str(data.get("slug") or slugify(name)).strip()
    if not name or not slug: return None, "Name and slug are required."
    return {"name": name[:160], "slug": slug[:180], "ordering": int(data.get("ordering", 0) or 0), "status": int(data.get("status", 1) or 1)}, None

def question_payload(data):
    if not str(data.get("question_vi") or "").strip() or not str(data.get("answer_vi") or "").strip(): return None, "Vietnamese question and answer are required."
    try: category_id, ordering, status = int(data.get("category_id")), int(data.get("ordering", 0) or 0), int(data.get("status", 1) or 1)
    except (TypeError, ValueError): return None, "Category, ordering and status must be valid numbers."
    if not FAQCategory.objects.filter(pk=category_id).exists(): return None, "FAQ category was not found."
    return {"category_id": category_id, "question_vi": str(data["question_vi"]), "answer_vi": str(data["answer_vi"]), "question_en": str(data.get("question_en") or ""), "answer_en": str(data.get("answer_en") or ""), "ordering": ordering, "status": status}, None