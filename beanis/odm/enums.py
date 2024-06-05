from enum import Enum


class InspectionStatuses(str, Enum):
    """
    Statuses of the collection inspection
    """

    FAIL = "FAIL"
    OK = "OK"
