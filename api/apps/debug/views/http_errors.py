from django.views.generic import View


class HTTP500(View):
    def get(self, request, *args, **kwargs):
        raise RuntimeError('Deliberate error to cause HTTP 500.')
