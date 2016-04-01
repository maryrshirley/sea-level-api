import datetime

from api.libs.view_helpers import now_rounded


def delta(**deltatime):
    now = now_rounded()
    return now + datetime.timedelta(**deltatime)
