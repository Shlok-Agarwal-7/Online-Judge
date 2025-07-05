from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import Problem
from django.core.cache import cache


@receiver([post_save, post_delete], sender=Problem)
def invalidate_product_cache(sender, instance, **kwargs):
    """
    Invalidate product list caches when a product is created, updated, or deleted
    """
    
    # Clear product list caches
    cache.delete_pattern('*product_list*')