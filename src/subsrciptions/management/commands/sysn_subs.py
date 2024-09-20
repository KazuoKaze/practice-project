from typing import Any
from subsrciptions.models import Subscriptions
from django.core.management.base import BaseCommand

class Command(BaseCommand):
    def handle(self, *args: Any, **options: Any):
        qs = Subscriptions.objects.filter(active=True)
        for obj in qs:
            sub_prem = obj.permisssions.all()
            for grp in obj.groups.all():
                grp.permissions.set(sub_prem)