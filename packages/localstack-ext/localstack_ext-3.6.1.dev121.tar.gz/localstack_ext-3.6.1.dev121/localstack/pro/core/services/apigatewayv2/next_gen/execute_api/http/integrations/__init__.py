from .aws import (
    AppConfigGetConfigurationIntegration,
    EventBridgePutEventsIntegration,
    HttpApiAwsProxyIntegration,
    KinesisPutRecordIntegration,
    SQSDeleteMessageIntegration,
    SQSPurgeQueueIntegration,
    SQSReceiveMessageIntegration,
    SQSSendMessageIntegration,
    StepFunctionsStartExecutionIntegration,
    StepFunctionsStartSyncExecutionIntegration,
    StepFunctionsStopExecutionIntegration,
)
from .core import HttpApiIntegration
from .http import HttpApiHttpProxyIntegration
from .private import HttpApiPrivateIntegration

HTTP_API_INTEGRATIONS: dict[tuple[str, str], HttpApiIntegration] = {
    (integration.name, integration.subtype): integration()
    for integration in [
        AppConfigGetConfigurationIntegration,
        EventBridgePutEventsIntegration,
        HttpApiAwsProxyIntegration,
        KinesisPutRecordIntegration,
        SQSDeleteMessageIntegration,
        SQSPurgeQueueIntegration,
        SQSReceiveMessageIntegration,
        SQSSendMessageIntegration,
        StepFunctionsStartExecutionIntegration,
        StepFunctionsStartSyncExecutionIntegration,
        StepFunctionsStopExecutionIntegration,
        HttpApiHttpProxyIntegration,
        HttpApiPrivateIntegration,
    ]
}

__all__ = [
    "HTTP_API_INTEGRATIONS",
]
