"""Amazon Interactive Video Service resource inventories."""
from modules.qmcore.aws import CheckContext, session_from_env


CHECKS = [
    ('L-C01DFF58', 'Channels',
     lambda c: dict(usage=len(c.call('ivs', 'list_channels', 'channels')),
                    source='ivs:ListChannels', method='ACCOUNT_COUNT')),
    ('L-90ABAB37', 'Recording configurations',
     lambda c: dict(usage=len(c.call('ivs', 'list_recording_configurations', 'recordingConfigurations')),
                    source='ivs:ListRecordingConfigurations', method='ACCOUNT_COUNT')),
    ('L-BF843A02', 'Storage configurations',
     lambda c: dict(usage=len(c.call('ivs-realtime', 'list_storage_configurations', 'storageConfigurations')),
                    source='ivs-realtime:ListStorageConfigurations', method='ACCOUNT_COUNT')),
    ('L-F7C5B6C9', 'Encoder configurations',
     lambda c: dict(usage=len(c.call('ivs-realtime', 'list_encoder_configurations', 'encoderConfigurations')),
                    source='ivs-realtime:ListEncoderConfigurations', method='ACCOUNT_COUNT')),
    ('L-CE6ADDBE', 'Ingest configurations',
     lambda c: dict(usage=len(c.call('ivs-realtime', 'list_ingest_configurations', 'ingestConfigurations')),
                    source='ivs-realtime:ListIngestConfigurations', method='ACCOUNT_COUNT')),
]


def get_current_quotastatus_ivs(session=None, *, ctx=None, skip=()):
    context = ctx or CheckContext(session or session_from_env())
    if not any(service == 'ivs' for service, _ in context.quotas):
        return []
    return context.run('ivs', CHECKS, skip)
