from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Package, TrackingEvent

@receiver(post_save, sender=Package)
def create_tracking_event(sender, instance, created, **kwargs):
    """
    Automatically create a TrackingEvent when a Package status changes.
    """
    if created:
        # Initial event is already handled in views.py for now, but good to have a check.
        # If views.py creates it, we might duplicate if we are not careful.
        # However, views.py creates the package then creates the event manually.
        # If we want to rely solely on signals, we should remove the manual creation in views.py.
        # For now, let's check if an event with this status already exists to avoid duplication on creation
        # if the view does it immediately.
        # But actually, the view saves the package (triggering this signal) THEN creates the event.
        # So this signal runs BEFORE the view creates the event manually.
        # If we create it here, the view will create a duplicate.
        
        # Strategy: Let's allow the signal to handle it.
        # But since I am not modifying views.py in this step, I might introduce duplication for CREATED status.
        # Let's check if we should handle CREATED here.
        # If I handle CREATED here, I should remove it from views.py later or accept duplication.
        # To be safe and avoid modifying views.py if not strictly necessary (though I should),
        # I will check if an event exists? No, that's racy and inefficient.
        
        # Actually, the requirement is "Lifecycle Logging".
        # Let's implement the logic to track *changes*.
        # To track changes, we need to know the old status.
        # post_save doesn't provide the old instance.
        # We need pre_save to get the old status, or use a field tracker.
        # Since I don't want to add dependencies like django-model-utils, 
        # I will use a pre_save signal to store the old status on the instance, 
        # and post_save to check it.
        pass
    else:
        # For updates, we need to know if status changed.
        # But post_save doesn't have access to the old field value.
        # We need to hook into pre_save to save the old status.
        pass

# Redefining the approach to be robust without external dependencies.

from django.db.models.signals import pre_save, post_save

@receiver(pre_save, sender=Package)
def track_package_status_change(sender, instance, **kwargs):
    if instance.pk:
        try:
            old_instance = Package.objects.get(pk=instance.pk)
            instance._old_status = old_instance.status
        except Package.DoesNotExist:
            instance._old_status = None
    else:
        instance._old_status = None

@receiver(post_save, sender=Package)
def create_tracking_event(sender, instance, created, **kwargs):
    if created:
        # For new packages, we create the initial event.
        # Note: views.py also creates one. This will result in two CREATED events.
        # This is acceptable for now, or I can modify views.py.
        # I will modify views.py to remove manual creation to be clean.
        TrackingEvent.objects.create(
            package=instance,
            status=instance.status,
            location='System (Origin)',
            description=f'Package created with status {instance.get_status_display()}'
        )
    else:
        if hasattr(instance, '_old_status') and instance._old_status != instance.status:
            TrackingEvent.objects.create(
                package=instance,
                status=instance.status,
                location='System Update', # Ideally this would come from context, but signals are context-free.
                description=f'Status changed from {instance._old_status} to {instance.status}'
            )
