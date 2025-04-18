from apps.trips.models import Trip
import uuid

for obj in Trip.objects.filter(public_token__isnull=True):
    obj.public_token = uuid.uuid4()
    obj.save()
