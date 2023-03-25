from django.core.management.base import BaseCommand
from promo.models import Promo
from django.utils import timezone


class Command(BaseCommand):
    help = "Check the status of all Promos and update their active field accordingly"
    def handle(self, *args, **options):
        now = timezone.now()
        for promo in Promo.objects.all():
            if promo.start_date <= now <= promo.end_date:
                promo.active = True
            else:
                promo.active = False
            promo.save()
