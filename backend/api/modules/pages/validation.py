from ...models import PageComponentDefinition


def validate_regions_against_template(regions, template):
    if not isinstance(regions, dict):
        return "regions must be an object keyed by region id."
    definitions = {str(region.get("id")): region for region in template.regions if isinstance(region, dict) and region.get("id")}
    for region_id, blocks in regions.items():
        definition = definitions.get(str(region_id))
        if definition is None:
            return f"Region '{region_id}' is not defined by template '{template.key}'."
        if not isinstance(blocks, list):
            return f"Region '{region_id}' must contain an array of blocks."
        max_blocks = definition.get("maxBlocks")
        if max_blocks is not None and len(blocks) > max_blocks:
            return f"Region '{region_id}' accepts at most {max_blocks} block(s)."
        allowed = set(definition.get("allowedBlocks") or [])
        registered_types = set(PageComponentDefinition.objects.values_list("component_key", flat=True))
        if definition.get("locked") and blocks:
            return f"Region '{region_id}' is locked and cannot contain editable blocks."
        for block in blocks:
            block_type = block.get("type") if isinstance(block, dict) else None
            if block_type not in allowed and block_type not in registered_types:
                return f"Block type '{block_type}' is not allowed in region '{region_id}'."
    return None