from django.core.mail import mail_admins
from django.http import JsonResponse
from django.views.generic import View


class MailAdmins(View):
    def get(self, request, *args, **kwargs):
        mail_admins('Debug: mail-admins', 'Hello! Your request: {}'.format(
            request))
        return JsonResponse({'status': 'OK, mail sent.'})
