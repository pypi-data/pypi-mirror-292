import copy
from datetime import datetime
from enum import Enum
from uuid import UUID
from dateutil import parser


# Enums
class FileIndexFieldType(Enum):
    Datetime = 0
    String = 1
    Number = 2
    Integer = 3

class DateBucketSize(Enum):
    Minute = 0
    Hour = 1
    Day = 2
    Week = 3
    Month = 4
    Year = 5

class InputstreamStatus(Enum):
    ToDiscover = 0
    Undiscovered = 1
    Exposed = 2
    ToDiscoverAgain = 3

class InputstreamStorage(Enum):
    Collection = 0
    TimeSeriesCollection = 1
    File = 2

class InputstreamProtocol(Enum):
    MQTT = 0
    HTTP = 1
    BOTH = 2

class RealTimeMode(Enum):
    OFF = 0
    ON = 1

class IndexType(Enum):
    Unique = 0
    Search = 1

class SortType(Enum):
    Ascending = 0
    Descending = 1

# Models
class IndexField:
    Name: str
    FieldType: FileIndexFieldType
    DoubleBucketSize: float
    DateBucketSize: DateBucketSize

    def __init__(self, from_response=False, **kwargs):
        if from_response:
            kwargs["Name"] = kwargs.pop('name')
            kwargs["DoubleBucketSize"] = kwargs.pop('doubleBucketSize')
            kwargs["FieldType"] = FileIndexFieldType(kwargs.pop('fieldType'))
            kwargs["DateBucketSize"] = DateBucketSize(kwargs.pop('dateBucketSize'))
        else:
            kwargs["FieldType"] = FileIndexFieldType(kwargs.pop('FieldType'))
            kwargs["DateBucketSize"] = DateBucketSize(kwargs.pop('DateBucketSize'))
        self.__dict__ = kwargs

    def get_dict(self):
        data = copy.deepcopy(self.__dict__)
        return data


class CollectionIndexField:
    Name: str
    SortType: SortType

    def __init__(self, from_response=False, **kwargs):
        if from_response:
            kwargs["Name"] = kwargs.pop('name')
            kwargs["SortType"] = SortType(kwargs.pop('sortType'))
        else:
            kwargs["SortType"] = SortType(kwargs["SortType"])
        self.__dict__ = kwargs

    def get_dict(self):
        data = copy.deepcopy(self.__dict__)
        return data


class CollectionIndex:
    Name: str
    Fields: list[CollectionIndexField]
    IndexType: IndexType
    DateCreated: datetime

    def __init__(self, from_response=False, **kwargs):
        if from_response:
            kwargs["Name"] = kwargs.pop('name')
            kwargs["DateCreated"] = kwargs.pop('dateCreated')
            kwargs["Fields"] = [CollectionIndexField(from_response=True, **x) for x in kwargs.pop('fields')]
            kwargs["IndexType"] = IndexType(kwargs.pop('indexType'))
        else:
            kwargs["DateCreated"] = kwargs.pop('DateCreated')
            kwargs["Fields"] = [CollectionIndexField(**x) for x in kwargs["Fields"]]
            kwargs["IndexType"] = IndexType(kwargs.pop('IndexType'))
        self.__dict__ = kwargs

    def get_dict(self):
        data = copy.deepcopy(self.__dict__)
        data["Fields"] = [x.get_dict() for x in self.Fields]
        return data

class Inputstream:
    Id: UUID
    Name: str
    InputstreamCollectionName: str
    Schema: str
    SchemaSample: str
    SampleDate: datetime
    Status: InputstreamStatus
    Tags: list[str]
    Ikey: str
    CollectionIndexes: list[CollectionIndex]
    FilesIndex: list[IndexField]
    Storage: InputstreamStorage
    Protocol: InputstreamProtocol
    RealTimeMode: RealTimeMode
    Size: int
    MaxNDocsByFile: int
    AllowAnyOrigin: bool
    FileConsolidatorCron: str
    Removed: bool
    CreatedOn: datetime
    RemovedOn: datetime


    def __init__(self, from_response = False, **kwargs):
        if from_response: self.from_response(**kwargs)
        else:
            kwargs["Id"] = UUID(kwargs.pop('Id'))

            kwargs["Status"]       = InputstreamStatus(kwargs.pop('Status'))
            kwargs["Storage"]      = InputstreamStorage(kwargs.pop('Storage'))
            kwargs["Protocol"]     = InputstreamProtocol(kwargs.pop('Protocol'))
            kwargs["RealTimeMode"] = RealTimeMode(kwargs.pop('RealTimeMode'))

            kwargs["FilesIndex"]        = [IndexField(**x) for x in kwargs["FilesIndex"]]
            kwargs["CollectionIndexes"] = [CollectionIndex(**x) for x in kwargs["CollectionIndexes"]]

            self.__dict__ = kwargs

    
    def from_response(self, **kwargs) -> None:
        kwargs["Id"]           = UUID(kwargs.pop('id'))

        kwargs["Name"]                      = kwargs.pop('name')
        kwargs["InputstreamCollectionName"] = kwargs.pop('inputstreamCollectionName')
        kwargs["Schema"]                    = kwargs.pop('schema')
        kwargs["SchemaSample"]              = kwargs.pop('schemaSample')
        kwargs["Tags"]                      = kwargs.pop('tags')
        kwargs["Ikey"]                      = kwargs.pop('ikey')
        kwargs["Size"]                      = kwargs.pop('size')
        kwargs["MaxNDocsByFile"]            = kwargs.pop('maxNDocsByFile')
        kwargs["AllowAnyOrigin"]            = kwargs.pop('allowAnyOrigin')
        kwargs["FileConsolidatorCron"]      = kwargs.pop('fileConsolidatorCron')
        kwargs["Removed"]                   = kwargs.pop('removed')

        kwargs["Status"]       = InputstreamStatus(kwargs.pop('status'))
        kwargs["Storage"]      = InputstreamStorage(kwargs.pop('storage'))
        kwargs["Protocol"]     = InputstreamProtocol(kwargs.pop('protocol'))
        kwargs["RealTimeMode"] = RealTimeMode(kwargs.pop('realTimeMode'))

        kwargs["FilesIndex"]        = [IndexField(from_response=True,**x) for x in kwargs.pop("filesIndex")]
        kwargs["CollectionIndexes"] = [CollectionIndex(from_response=True, **x) for x in kwargs.pop("collectionIndexes")]

        kwargs["SampleDate"]  = kwargs.pop('sampleDate')
        kwargs["CreatedOn"]   = kwargs.pop('createdOn') 
        kwargs["RemovedOn"]   = kwargs.pop('removedOn') 

        self.__dict__ = kwargs

    def get_dict(self):
        data = copy.deepcopy(self.__dict__)
        data["Id"] = str(data["Id"])
        data["FilesIndex"] = [x.get_dict() for x in self.FilesIndex]
        data["CollectionIndexes"] = [x.get_dict() for x in self.CollectionIndexes]
        return data
