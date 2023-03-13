import logging

from django.db.models import signals

from apps.core.models import CoreUser
from django.conf import settings
from cacheops import invalidate_obj

logger = logging.getLogger(__name__)


def change_user_permission_handler(sender, instance:CoreUser, action, reverse, model, pk_set, using, **kwargs):
    permissions = list(instance.get_all_permissions())
    instance._meta.model.objects.filter(pk=instance.pk).update(cached_permissions=permissions)
    invalidate_obj(instance)

def init_core_signals():
    logger.info('------------- LCORE SIGNALS INIT ------------')
    signals.m2m_changed.connect(receiver=change_user_permission_handler, sender=CoreUser.user_permissions.through)
