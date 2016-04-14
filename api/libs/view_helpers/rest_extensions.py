from rest_framework import views


def get_view_name(view_cls, suffix=None):
    if hasattr(view_cls, 'Meta') and hasattr(view_cls.Meta, 'name'):
        return view_cls.Meta.name
    return views.get_view_name(view_cls, suffix)
