import os
from django.core.wsgi import get_wsgi_application
import datetime
from django.utils import timezone

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'djangoapp.settings')
application = get_wsgi_application()
from core.models import Time, Employee, Surgeon, Cleaner, Patient, Surgery, Schedule
def clear_database():
    Time.objects.all().delete()
    Employee.objects.all().delete()
    Surgeon.objects.all().delete()
    Patient.objects.all().delete()
    Cleaner.objects.all().delete()
clear_database()

time_instance = Time.objects.create(
    id = 1,
    timestart=timezone.make_aware(datetime.datetime(2024, 1, 1, 13, 0)),  # 1:00pm
    timeend=timezone.make_aware(datetime.datetime(2024, 12, 1, 13, 0))  # 2:00pm
)



