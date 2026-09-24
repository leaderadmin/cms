from ...models import Dealer, RecruitmentArea

def serialize_dealer(item):
    return {"id": item.id, "name": item.name, "code": item.code, "dealer_type": item.dealer_type, "province_city": item.province_city, "address": item.address, "hotline": item.hotline, "email": item.email, "latitude": str(item.latitude) if item.latitude is not None else None, "longitude": str(item.longitude) if item.longitude is not None else None, "opening_hours": item.opening_hours, "status": item.status, "area_id": item.area_id, "area": item.area.name if item.area else "", "region_id": item.area.region_id if item.area else None, "region": item.area.region.name if item.area else ""}

def dealer_payload(data):
    name, code = str(data.get("name") or "").strip(), str(data.get("code") or "").strip()
    if not name or not code: return None, "Dealer name and code are required."
    try: latitude = data.get("latitude") or None; longitude = data.get("longitude") or None; status = int(data.get("status", 1) or 1)
    except (TypeError, ValueError): return None, "Coordinates and status must be valid."
    try: area_id = int(data.get("area_id")) if data.get("area_id") else None
    except (TypeError, ValueError): return None, "Area must be valid."
    if area_id and not RecruitmentArea.objects.filter(pk=area_id, status=1).exists(): return None, "Area must be valid."
    region_id = data.get("region_id")
    if region_id and area_id:
        try: region_id = int(region_id)
        except (TypeError, ValueError): return None, "Region must be valid."
        if not RecruitmentArea.objects.filter(pk=area_id, region_id=region_id, status=1).exists(): return None, "Area must belong to the selected region."
    dealer_type = str(data.get("dealer_type") or Dealer.TYPE_BRANCH)
    if dealer_type not in dict(Dealer.TYPE_CHOICES): return None, "Dealer type must be branch, atm, or transaction_office."
    return {"name": name[:255], "code": code[:80], "dealer_type": dealer_type, "province_city": str(data.get("province_city") or "")[:160], "address": str(data.get("address") or "")[:500], "hotline": str(data.get("hotline") or "")[:80], "email": str(data.get("email") or "")[:254], "latitude": latitude, "longitude": longitude, "opening_hours": str(data.get("opening_hours") or "")[:255], "status": status, "area_id": area_id}, None