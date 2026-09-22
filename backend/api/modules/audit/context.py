def set_activity_context(request, **values):
    """Attach business event metadata for the activity-log middleware."""
    context = getattr(request, "activity_context", {})
    context.update(values)
    request.activity_context = context
    underlying_request = getattr(request, "_request", None)
    if underlying_request is not None:
        underlying_request.activity_context = context