from django.shortcuts import _get_queryset

def get_or_none(klass, *args, **kwargs):
    """
    Use get() to return an object, or return an empty queryset if the object
    does not exist.

    klass may be a Model, Manager, or QuerySet object. All other passed
    arguments and keyword arguments are used in the get() query.
    """
    queryset = _get_queryset(klass)
    if not hasattr(queryset, "get"):
        klass__name = (
            klass.__name__
            if isinstance(klass, type)
            else klass.__class__.__name__
        )
        raise ValueError(
            "First argument to get_or_none() must be a Model, Manager, "
            "or QuerySet, not '%s'." % klass__name
        )
    try:
        return queryset.get(*args, **kwargs)
    except queryset.model.DoesNotExist:
        queryset.none()