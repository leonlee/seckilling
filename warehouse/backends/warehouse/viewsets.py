import logging

from django.db.models import Count, Q
from django.conf import settings

from rest_framework import viewsets
from rest_framework.decorators import detail_route, list_route
from rest_framework.response import Response

from . import redis_inst
from .serializer import BrandStatsSerializer, PrizeSerializer, ActivitiesSerializer
from .models import Brand, Prizes, Activities


logger = logging.getLogger(__name__)


class BrandStatsViewSet(viewsets.ReadOnlyModelViewSet):
    """
    """
    # def list(self, request, *args, **kwargs):
    #     pass
    #
    # def retrieve(self, request, *args, **kwargs):
    #     pass

    def get_queryset(self):
        return Brand.objects.annotate(total_prize_count=Count('prizes'))

    queryset = Brand.objects.all()
    serializer_class = BrandStatsSerializer


class PrizeViewSet(viewsets.ReadOnlyModelViewSet):
    """
    """
    # def list(self, request, *args, **kwargs):
    #     pass
    #
    # def retrieve(self, request, *args, **kwargs):
    #     pass

    queryset = Prizes.objects.all()
    serializer_class = PrizeSerializer


class ActivitiesViewSet(viewsets.ReadOnlyModelViewSet):
    """
    """
    # def list(self, request, *args, **kwargs):
    #     pass
    #
    # def retrieve(self, request, *args, **kwargs):
    #     pass

    @detail_route(methods=['get'], url_path='delivered-count')
    def delivered_count(self, request, pk, **kwages):
        event_key = settings.REDIS['key_fmts']['delivered_count'] % str(pk)
        count = redis_inst.get(event_key)
        if count:
            logger.info('Get delivered count %s for event %s.' % (count, pk))
        else:
            logger.warn('No delivered count for event %s in Redis!' % pk)
        return Response({'count': int(count)})

    @list_route(methods=['get'], url_path='current-activity')
    def current_activity(self, request, **kwages):
        event_key = settings.REDIS['key_fmts']['current_eid']
        current_eid = int(redis_inst.get(event_key))
        if not current_eid:
            logger.warn('No current event ID(%s) found in Redis!' % event_key)
        event_key = settings.REDIS['key_fmts']['event_hash'] % str(int(current_eid))
        event_status = redis_inst.hget(event_key, 'status')
        if event_status:
            status = int(event_status)
        else:
            logger.warn('No status info for current event %s in Redis.' % current_eid)
            status = 2  # waiting/init status, not started yet
        check_and_update_activity_status(current_eid, status)
        return Response({'current_eid': current_eid})

    queryset = Activities.objects.all()
    serializer_class = ActivitiesSerializer


def check_and_update_activity_status(eid, status, **kwargs):
    event_status_mapping = {
        1: 'running',
        2: 'waiting',
        3: 'end'
    }
    cur_event = Activities.objects.get(id=eid)
    # check events that should be finished before has the correct status, update if not
    qs = Activities.objects.filter(Q(end_at__lte=cur_event.start_at) & ~Q(status='end'))
    if qs:
        # loop over to call save with `update_fields`
        for item in qs:
            logger.info('Event %s end before current event %s, update its status.' % (item.id, eid))
            item.status = 'end'
            item.save(update_fields=['status'])
            logger.info('Updated event %s status to end.' % item.id)
    status = event_status_mapping[status]
    # update current event status accordingly
    if cur_event.status != status:
        logger.info("Current event %s status is not up-to-date. Updating to %s." % (eid, status))
        cur_event.status = status
        cur_event.save(update_fields=['status'])
        logger.info("Update current event %s status to %s done." % (eid, status))
