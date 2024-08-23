from enum import Enum


class DataSourceStatusChoices(Enum):
    ERROR = 'error', 'Error'
    HEALTHY = 'healthy', 'Healthy'
    IDLE = 'idle', 'Idle'
    NEW = 'new', 'New'


