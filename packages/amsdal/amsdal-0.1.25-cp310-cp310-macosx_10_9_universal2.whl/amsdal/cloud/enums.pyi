from enum import Enum

class AuthType(Enum):
    CREDENTIALS = ...
    TOKEN = ...

class DeployType(str, Enum):
    lakehouse_only = 'lakehouse_only'
    include_state_db = 'include_state_db'

class StateOption(str, Enum):
    sqlite = 'sqlite'
    postgres = 'postgres'

class LakehouseOption(str, Enum):
    spark = 'spark'
    postgres = 'postgres'
    postgres_immutable = 'postgres-immutable'

class ResponseStatus(str, Enum):
    success = 'success'
    error = 'error'
