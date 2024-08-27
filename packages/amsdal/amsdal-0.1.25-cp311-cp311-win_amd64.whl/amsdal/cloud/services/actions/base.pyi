import abc
from _typeshed import Incomplete
from abc import ABC, abstractmethod
from amsdal.cloud.client import AuthClientService as AuthClientService
from amsdal.cloud.constants import ENCRYPT_PUBLIC_KEY as ENCRYPT_PUBLIC_KEY
from amsdal.cloud.enums import ResponseStatus as ResponseStatus
from amsdal.cloud.models.base import ResponseBaseModel as ResponseBaseModel
from amsdal.configs.main import settings as settings
from amsdal.errors import AmsdalCloudAlreadyDeployedError as AmsdalCloudAlreadyDeployedError, AmsdalCloudError as AmsdalCloudError
from enum import Enum
from typing import Any

class AuthErrorCodes(str, Enum):
    INVALID_EMAIL = 'invalid_email'
    MISSING_CREDENTIALS = 'missing_credentials'
    INVALID_CREDENTIALS = 'invalid_credentials'
    INVALID_APPLICATION_UUID = 'invalid_application_uuid'
    CLIENT_IS_INACTIVE = 'client_is_inactive'
    CLIENT_ALREADY_EXISTS = 'client_already_exists'
    DEPLOY_FAILED = 'deploy_failed'
    DEPLOY_ALREADY_EXISTS = 'deploy_already_exists'
    DEPLOY_NOT_IN_DEPLOYED_STATUS = 'deploy_not_in_deployed_status'
    DESTROY_FAILED = 'destroy_failed'
    DEPLOY_NOT_FOUND = 'deploy_not_found'
    INVALID_DEPENDENCY = 'invalid_dependency'
    EXPOSE_DB_ACCESS_FAILED = 'expose_access_failed'
    APPLICATION_ALREADY_EXISTS = 'application_already_exists'
    MULTIPLE_APPLICATIONS_FOUND = 'multiple_applications_found'
    MAXIMUM_APPLICATIONS_REACHED = 'maximum_applications_reached'
    INTERNAL_SECRET = 'internal_secret'
    BA_DOES_NOT_EXIST = 'ba_does_not_exist'
    INVALID_IP_ADDRESS = 'invalid_ip_address'
    MONITORING_NOT_FOUND = 'monitoring_not_found'
    INVALID_ENVIRONMENT_NAME = 'invalid_environment_name'
    SAME_ENVIRONMENT_NAME = 'same_environment_name'
    ENVIRONMENT_NOT_FOUND = 'environment_not_found'
    ENVIRONMENT_NOT_DEPLOYED = 'environment_not_deployed'
    MAXIMUM_DEPLOYS_PER_APPLICATION_REACHED = 'maximum_deploys_per_application_reached'
    CANNOT_DELETE_ENVIRONMENT = 'cannot_delete_environment'

FRIENDLY_ERROR_MESSAGES: Incomplete

class CloudActionBase(ABC, metaclass=abc.ABCMeta):
    auth_client: Incomplete
    def __init__(self) -> None: ...
    @abstractmethod
    def action(self, *args: Any, **kwargs: Any) -> Any: ...
    def _credentials_data(self) -> bytes: ...
    @staticmethod
    def _input(msg: str) -> str: ...
    @staticmethod
    def _print(msg: str) -> None: ...
    def execute_transaction(self, transaction_name: str, data: dict[str, Any]) -> dict[str, Any]: ...
    def process_errors(self, response: ResponseBaseModel) -> None: ...
