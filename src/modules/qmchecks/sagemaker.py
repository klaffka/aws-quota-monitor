"""Compatibility wrapper for the consolidated SageMaker checks."""
from modules.qmchecks.sagemaker_resources import (
    CHECKS as _RESOURCE_CHECKS, get_current_quotastatus_sagemaker_resources,
)

# Keep the historical public wrapper limited to the original notebook and
# pipeline checks.  The collector imports ``sagemaker_resources`` directly,
# so newer resource checks remain active without breaking callers that relied
# on the old two-entry compatibility module.
CHECKS = _RESOURCE_CHECKS[:2]


def get_current_quotastatus_sagemaker(*args, **kwargs):
    return get_current_quotastatus_sagemaker_resources(*args, **kwargs)
