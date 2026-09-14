"""Amazon Location regional resource-count quotas."""
from modules.qmcore.aws import CheckContext, maximum, session_from_env


def tracker_consumers(ctx):
    values = []
    for tracker in ctx.call('location', 'list_trackers', 'Entries'):
        name = tracker.get('TrackerName') or tracker.get('Name')
        if name:
            values.append((name, len(ctx.call('location', 'list_tracker_consumers', 'ConsumerArns',
                                              TrackerName=name)), None))
    return maximum(values, 'LocationTracker', 'location:ListTrackerConsumers')


def geofences_per_collection(ctx):
    values = []
    for collection in ctx.call('location', 'list_geofence_collections', 'Entries'):
        name = collection.get('CollectionName') or collection.get('Name')
        if name:
            values.append((name, len(ctx.call('location', 'list_geofences', 'Entries',
                                               CollectionName=name)), None))
    return maximum(values, 'GeofenceCollection', 'location:ListGeofences')


CHECKS = [
    ('L-8CDBA5E9', 'Tracker resources per account',
     lambda c: dict(usage=len(c.call('location', 'list_trackers', 'Entries')),
                    source='location:ListTrackers', method='ACCOUNT_COUNT')),
    ('L-93FB3073', 'Geofence Collection resources per account',
     lambda c: dict(usage=len(c.call('location', 'list_geofence_collections', 'Entries')),
                    source='location:ListGeofenceCollections', method='ACCOUNT_COUNT')),
    ('L-A94FDED2', 'Map resources per account',
     lambda c: dict(usage=len(c.call('location', 'list_maps', 'Entries')),
                    source='location:ListMaps', method='ACCOUNT_COUNT')),
    ('L-AE411BEA', 'API Key resources per account',
     lambda c: dict(usage=len(c.call('location', 'list_keys', 'Entries')),
                    source='location:ListKeys', method='ACCOUNT_COUNT')),
    ('L-AF0CC293', 'Place Index resources per account',
     lambda c: dict(usage=len(c.call('location', 'list_place_indexes', 'Entries')),
                    source='location:ListPlaceIndexes', method='ACCOUNT_COUNT')),
    ('L-D4E15F64', 'Route Calculator resources per account',
     lambda c: dict(usage=len(c.call('location', 'list_route_calculators', 'Entries')),
                    source='location:ListRouteCalculators', method='ACCOUNT_COUNT')),
    ('L-7B55057C', 'Tracker consumers per tracker', tracker_consumers),
    ('L-DDC336FA', 'Geofences per Geofence Collection', geofences_per_collection),
]


def get_current_quotastatus_location(session=None, *, ctx=None, skip=()):
    context = ctx or CheckContext(session or session_from_env())
    if not any(service == 'geo' for service, _ in context.quotas):
        return []
    return context.run('geo', CHECKS, skip)
