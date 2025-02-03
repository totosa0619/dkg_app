from django.core.management.base import BaseCommand

from storage import blob
from diagrams.models import DiagramFrame


class Command(BaseCommand):
    help = "Copy local files to azure"

    def handle(self, *args, **options):
        cl = blob.new_client()
        for f in DiagramFrame.objects.filter():
            blob.upload_diagram(cl, f.source.path, f.source.name)
