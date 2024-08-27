"""
Patched to the delta_sharing library until the pre-filter
of files by partition is implemented
"""

from json import loads
from numbers import Number
from typing import (
    Any,
    Callable,
    Dict,
    Iterator,
    List,
    Optional,
    Sequence,
    TypedDict,
    Union,
)

import pandas as pd
from delta_sharing import Table
from delta_sharing.converter import get_empty_table, to_converters
from delta_sharing.delta_sharing import _parse_url
from delta_sharing.protocol import AddFile, DeltaSharingProfile
from delta_sharing.reader import DeltaSharingReader as DSR
from delta_sharing.rest_client import DataSharingRestClient, ListFilesInTableResponse

PartitionValuesType = Dict[str, List[Union[str, Number]]]


class Column(TypedDict):
    name: str
    type: str
    nullable: bool
    metadata: Dict


class FileStats(TypedDict):
    numRecords: int
    minValues: Dict[str, Any]
    maxValues: Dict[str, Any]
    nullCount: Dict[str, Any]


class File(FileStats):
    id: str
    size: int
    partition_values: Dict[str, str]
    timestamp: Optional[int]
    version: Optional[int]


class DeltaSharingReader(DSR):
    @staticmethod
    def _check_partition(file: AddFile, partition_values: PartitionValuesType) -> bool:
        file_partition_values = file.partition_values
        for pk, pv in partition_values.items():
            # let if fail if the key is not a partition key
            if file_partition_values[pk] not in pv:
                return False
        return True

    def schema(self, response: Optional[ListFilesInTableResponse] = None) -> Dict:
        """
        Returns the json schema for the table. You ca either pass the response if you
        have already retrieved it or leave the code to retrieve it again
        """
        if response is None:
            response = self.get_files_in_table()
        return loads(response.metadata.schema_string)

    def get_files_in_table(
        self, partition_values: Optional[PartitionValuesType] = None
    ) -> ListFilesInTableResponse:
        return self._rest_client.list_files_in_table(
            self._table,
            predicateHints=self._predicateHints,
            limitHint=self._limit if partition_values is None else None,
            version=self._version,
            timestamp=self._timestamp,
        )

    def _read_files(
        self,
        files: Sequence[AddFile],
        converters: Dict[str, Callable[[str], Any]],
        limit: Optional[int],
    ) -> Iterator[pd.DataFrame]:
        for file in files:
            # read the file
            pdf = self._to_pandas(file, converters, False, limit)
            yield pdf
            if limit:
                limit -= len(pdf)
            if limit and limit <= 0:
                break

    def to_pandas(
        self, partition_values: Optional[PartitionValuesType] = None
    ) -> pd.DataFrame:
        """
        Retrieves the table as a pandas DataFrame

        TODO: the predicateHints argument should in theory be used to do
        pre-filters on the files by passing for example
        predicateHints=["month = '202304'", "month = '202305'"]
        but so far it is not a public argument on the library and I have not
        been able to correctly use it (documentation is lacking). I've tried with the
        provided example but it yields all files anyway. For now we have done our
        own implementation of a filter by partition which works quite well

        Parameters
        ----------
        partition_values: PartitionValuesType
            Optional partition dictionary. Each key is a partition column and
            the values are the partition values to query
            Example: {"month": ["202307", "202306"]}
                If table is partitioned by month and we want those values
            Code will fail if key is not a partition of the table

        Returns
        -------
        : pd.DataFrame
            DataFrame containing the data queried
        """
        response = self.get_files_in_table(partition_values=partition_values)
        schema_json = self.schema(response=response)
        files = response.add_files
        # filter the files based on the partition values
        if partition_values is not None:
            # check the available partitions
            files = [f for f in files if self._check_partition(f, partition_values)]
        converters = to_converters(schema_json)
        files = [file for file in self._read_files(files, converters, self._limit)]

        if len(files) == 0 or self._limit == 0:
            return get_empty_table(schema_json)
        columns = [field["name"] for field in schema_json["fields"]]
        data = pd.concat(files, axis=0, ignore_index=True, copy=False)
        return data[columns]


def _access_ds(
    url: str,
    limit: Optional[int] = None,
    version: Optional[int] = None,
    timestamp: Optional[str] = None,
) -> DeltaSharingReader:
    """
    Load the DeltaSharingReader object

    Parameters
    ----------
    url: str
        a url under the format "<profile>#<share>.<schema>.<table>"

    limit: int
        a non-negative int. Load only the ``limit`` rows if the parameter is specified.
        Use this optional parameter to explore the shared table without loading the entire table to
        the memory.

    version: int
        an optional non-negative int. Load the snapshot of table at version

    Returns
    -------
    : DeltaSharingReader
        Instance of DeltaSharingReader with access to the delta share table
    """
    profile_json, share, schema, table = _parse_url(url)
    profile = DeltaSharingProfile.read_from_file(profile_json)

    return DeltaSharingReader(
        table=Table(name=table, share=share, schema=schema),
        rest_client=DataSharingRestClient(profile),
        limit=limit,
        version=version,
        timestamp=timestamp,
    )


def get_table_schema(*args: Any, **kwargs: Any) -> List[Column]:
    schema = _access_ds(*args, **kwargs).schema()
    return schema["fields"]


def _load_stats(file: AddFile) -> FileStats:
    stats = loads(file.stats)
    return {
        "numRecords": stats["numRecords"],
        "minValues": stats["minValues"],
        "maxValues": stats["maxValues"],
        "nullCount": stats["nullCount"],
    }


def _create_file_dict(file: AddFile) -> File:
    stats = _load_stats(file)
    return {
        "id": file.id,
        "size": file.size,
        "partition_values": file.partition_values,
        "timestamp": file.timestamp,
        "version": file.version,
        **stats,  # type: ignore
    }


def get_files_in_table(*args: Any, **kwargs: Any) -> List[File]:
    """
    Retrieves the files from Delta Share

    Parameters
    ----------
    url: str
        a url under the format "<profile>#<share>.<schema>.<table>"

    limit: int
        a non-negative int. Load only the ``limit`` rows if the parameter is specified.
        Use this optional parameter to explore the shared table without loading the entire table to
        the memory.

    version: int
        an optional non-negative int. Load the snapshot of table at version

    Returns
    -------
    : Files
        Instance of DeltaSharingReader with access to the delta share table
    """
    files = _access_ds(*args, **kwargs).get_files_in_table()
    return [_create_file_dict(file) for file in files.add_files]


def load_as_pandas(
    *args: Any, partition_values: Optional[PartitionValuesType] = None, **kwargs: Any
) -> pd.DataFrame:
    """
    Load the shared table using the given url as a pandas DataFrame.

    Parameters
    ----------
    url: str
        a url under the format "<profile>#<share>.<schema>.<table>"

    limit: int
        a non-negative int. Load only the ``limit`` rows if the parameter is specified.
        Use this optional parameter to explore the shared table without loading the entire table to
        the memory.

    version: int
        an optional non-negative int. Load the snapshot of table at version

    partition_values: PartitionValuesType
        An optional dictionary of partition key and values.
        Only values specified in the partition will be loaded
        Partition keys must exist on the target table or the code will fail
        Example: if the table is partitioned by a column month
            {"month": ["202003", "202004"]}


    Returns
    -------
    : pd.DataFrame
        A pandas DataFrame representing the shared table.
    """
    return _access_ds(*args, **kwargs).to_pandas(partition_values=partition_values)
