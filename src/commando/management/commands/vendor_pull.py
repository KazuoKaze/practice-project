import helpers

from typing import Any
from django.conf import settings
from django.core.management.base import BaseCommand


STATICFILES_VENDOR_DIR = getattr(settings, 'STATICFILES_VENDOR_DIR')

VENDOR_STATICFILES = {
    "flowbite.min.css": "https://cdn.jsdelivr.net/npm/flowbite@2.5.1/dist/flowbite.min.css",
    "flowbite.min.js": "https://cdn.jsdelivr.net/npm/flowbite@2.5.1/dist/flowbite.min.js",
    "flowbite.min.js.map": "https://cdn.jsdelivr.net/npm/flowbite@2.5.1/dist/flowbite.min.js.map"
}

class Command(BaseCommand):
    def handle(self, *args: Any, **options: Any):
        self.stdout.write("Downloading Vendor static files")
        completed_urls = []

        for name, url in VENDOR_STATICFILES.items():
            out_path = STATICFILES_VENDOR_DIR / name
            dl_success = helpers.download_to_loacl(url, out_path)
            if dl_success:
                completed_urls.append(url)
            else:
                self.stdout.write("Something went wrong")
        
        if set(completed_urls) == set(VENDOR_STATICFILES.values()):
            self.stdout.write("Success")
        else:
            self.stdout.write("Something went horible wrong")