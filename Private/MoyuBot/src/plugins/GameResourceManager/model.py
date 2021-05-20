from enum import Enum


#   Database Status Code
class DBSCode(Enum):
    SUCCESS = 200
    INSERTION_ERROR = 501
    RETRIEVAL_ERROR = 502
