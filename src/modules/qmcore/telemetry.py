"""Per-run SDK request counters; no additional CloudWatch metrics or API calls."""
from time import perf_counter


class ApiTelemetry:
    def __init__(self, session):
        self.services = {}
        session.events.register_first('before-call.*.*', self.before)
        session.events.register('after-call.*.*', self.after)
        session.events.register('after-call-error.*.*', self.failed)

    def before(self, model, context, **kwargs):
        service = model.service_model.service_name
        context['_qm_api'] = (service, perf_counter())
        stats = self.services.setdefault(service, dict(calls=0, errors=0, retries=0, apiSeconds=0.0))
        stats['calls'] += 1

    def finish(self, context, error, retries=0):
        started = context.pop('_qm_api', None)
        if started is None:
            return
        service, timestamp = started
        stats = self.services[service]
        stats['apiSeconds'] += perf_counter() - timestamp
        stats['errors'] += int(error)
        stats['retries'] += retries

    def after(self, context, http_response, parsed, **kwargs):
        self.finish(context, http_response.status_code >= 300,
                    parsed.get('ResponseMetadata', {}).get('RetryAttempts', 0))

    def failed(self, context, **kwargs):
        self.finish(context, True)

    def snapshot(self):
        return {service: {**stats, 'apiSeconds': round(stats['apiSeconds'], 3)}
                for service, stats in sorted(self.services.items())}
