"""
Schema module initialization.
"""
from .clio_api import *
from .base import *

__all__ = [
    # Base schemas
    'BaseResponse',
    'ErrorResponse',
    'SuccessResponse',
    
    # Clio API schemas
    'ContactResponse',
    'ContactCreate',
    'ContactUpdate',
    'CustomActionResponse', 
    'CustomActionCreate',
    'CustomActionUpdate',
    'WebhookSubscriptionResponse',
    'WebhookSubscriptionCreate',
    'WebhookSubscriptionUpdate',
    'WebhookEvent',
    'WebhookPayload',
]
