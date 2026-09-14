"""Manual catalog refresh using the same schema/cache as the collector."""
import sys
from pathlib import Path

if __package__ in {None, ''}:
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from modules.qmcore.aws import CheckContext, session_from_env
from modules.qmcore.catalog import get_catalog
from modules.qmdb.db import QuotaLogDb


def lambda_handler(event, context):
    session = session_from_env()
    quotas, errors = get_catalog(CheckContext(session), QuotaLogDb(session), force=True)
    if errors:
        raise RuntimeError(f'Catalog refresh incomplete: {errors}')
    return {'statusCode': 200, 'body': {'quotas_count': len(quotas)}}


if __name__ == '__main__':
    print(lambda_handler({}, None))
