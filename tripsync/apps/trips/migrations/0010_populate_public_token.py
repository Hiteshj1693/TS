# yourapp/migrations/xxxx_populate_public_token.py

from django.db import migrations
import uuid

def populate_public_token(apps, schema_editor):
    # Get the model
    Trip = apps.get_model('trips', 'Trip')
    
    # Loop through all records and set public_token
    for obj in Trip.objects.filter(public_token__isnull=True):
        obj.public_token = uuid.uuid4()
        obj.save()

class Migration(migrations.Migration):

    dependencies = [
        # Make sure this migration depends on the one that added the field
        ('trips', '0009_trip_public_token'),
    ]

    operations = [
        migrations.RunPython(populate_public_token),
    ]
