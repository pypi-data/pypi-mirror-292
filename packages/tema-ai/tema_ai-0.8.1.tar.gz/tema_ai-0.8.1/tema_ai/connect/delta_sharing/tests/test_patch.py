import json
from unittest.mock import MagicMock, patch

import pandas as pd
from parameterized import parameterized_class

from ..patch import (
    DSR,
    AddFile,
    DeltaSharingProfile,
    DeltaSharingReader,
    Table,
    get_files_in_table,
    get_table_schema,
    load_as_pandas,
)

SCHEMA_STRING = json.dumps(
    {
        "fields": [
            {"metadata": {}, "name": "h3_hex_id", "nullable": True, "type": "string"},
            {"metadata": {}, "name": "month", "nullable": True, "type": "string"},
        ],
        "type": "struct",
    }
)
COLUMNS = [f["name"] for f in json.loads(SCHEMA_STRING)["fields"]]
FILES = [
    AddFile(url="file1", id="id1", partition_values={"month": "202001"}, size=120),
    AddFile(url="file2", id="id2", partition_values={"month": "202002"}, size=120),
    AddFile(url="file3", id="id3", partition_values={"month": "202003"}, size=120),
    AddFile(url="file4", id="id4", partition_values={"month": "202004"}, size=120),
    AddFile(url="file5", id="id5", partition_values={"month": "202005"}, size=120),
]
ROWS = [("hex", file.partition_values["month"]) for file in FILES]
FULL_DF = pd.DataFrame(ROWS, columns=COLUMNS)

CASES1 = [
    {"partition_values": None, "expected": FULL_DF},
    {
        "partition_values": {"month": ["202001", "202002"]},
        "expected": FULL_DF[FULL_DF.month.isin(["202001", "202002"])],
    },
    {
        "partition_values": {"month": ["202003"]},
        "expected": FULL_DF[FULL_DF.month.isin(["202003"])],
    },
]


@parameterized_class(CASES1)
class TestDeltaSharingReader:
    def list_files_in_table(
        self, table, predicateHints=None, limitHint=None, version=None, timestamp=None
    ):
        files = MagicMock(
            metadata=MagicMock(schema_string=SCHEMA_STRING), add_files=FILES
        )
        return files

    @property
    def reader(self):
        RestClient = MagicMock()
        RestClient.list_files_in_table.side_effect = self.list_files_in_table
        return DeltaSharingReader(
            table=Table(name="table", share="share", schema="schema"),
            rest_client=RestClient,
            limit=None,
            version=None,
            timestamp=None,
        )

    def _to_pandas(self, file, *args):
        month = file.partition_values["month"]
        rows = [("hex", month)]
        return pd.DataFrame(rows, columns=COLUMNS)

    @patch.object(DSR, "_to_pandas")
    def test_to_pandas(self, mock_to_pandas):
        reader = self.reader
        mock_to_pandas.side_effect = self._to_pandas
        df = reader.to_pandas(self.partition_values)
        pd.testing.assert_frame_equal(
            df.reset_index(drop=True), self.expected.reset_index(drop=True)
        )


CASES = [
    {"path": "file.config#share.schema.table", "partition_values": None},
    {
        "path": "file.config#share.schema.table",
        "partition_values": {"month": ["202001"]},
    },
]


@parameterized_class(CASES)
class TestLoadAsPandas:
    def _split_path(self):
        profile, table = self.path.split("#")
        share, schema, table = table.split(".")
        return profile, share, schema, table

    @patch.object(DeltaSharingProfile, "read_from_file")
    @patch("tema_ai.connect.delta_sharing.patch.DataSharingRestClient")
    @patch("tema_ai.connect.delta_sharing.patch.DeltaSharingReader")
    def test(self, mock_dsr, mock_client, mock_profile):
        client = "CLIENT"
        mock_client.return_value = client

        load_as_pandas(self.path, partition_values=self.partition_values)
        profile, share, schema, table = self._split_path()

        mock_profile.assert_called_with(profile)
        mock_dsr.assert_called_with(
            table=Table(name=table, share=share, schema=schema),
            rest_client=client,
            limit=None,
            version=None,
            timestamp=None,
        )
        mock_dsr().to_pandas.assert_called_with(partition_values=self.partition_values)


TABLE_SCHEMA = [
    {"name": "file", "type": "string", "nullable": True, "metadata": {}},
    {"name": "year", "type": "integer", "nullable": True, "metadata": {}},
    {"name": "day", "type": "integer", "nullable": True, "metadata": {}},
    {"name": "quality", "type": "string", "nullable": True, "metadata": {}},
    {"name": "parent_hex_id", "type": "string", "nullable": True, "metadata": {}},
    {"name": "hex_ids", "type": "string", "nullable": True, "metadata": {}},
    {"name": "nvdi", "type": "decimal(6,3)", "nullable": True, "metadata": {}},
]


class TestGetTableSchema:
    @patch.object(DeltaSharingProfile, "read_from_file")
    @patch("tema_ai.connect.delta_sharing.patch.DataSharingRestClient")
    def test(self, mock_client, mock_dsr):
        mock_client().list_files_in_table().metadata.schema_string = json.dumps(
            {"fields": TABLE_SCHEMA}
        )
        schema = get_table_schema("file.config#share.schema.table")
        assert schema == TABLE_SCHEMA


STATS1 = {
    "numRecords": 10,
    "minValues": {},
    "maxValues": {},
    "nullCount": {},
}
STATS2 = {
    "numRecords": 10,
    "minValues": {},
    "maxValues": {},
    "nullCount": {},
}
FILES_FOR_STATS = [
    AddFile(
        url="file1",
        id="id1",
        partition_values={"month": "202001"},
        size=120,
        stats=json.dumps(STATS1),
    ),
    AddFile(
        url="file2",
        id="id2",
        partition_values={"month": "202002"},
        size=120,
        stats=json.dumps(STATS2),
    ),
]


class TestGetFilesInTable:
    @patch.object(DeltaSharingProfile, "read_from_file")
    @patch("tema_ai.connect.delta_sharing.patch.DataSharingRestClient")
    def test(self, mock_client, mock_dsr):
        mock_client().list_files_in_table().add_files = FILES_FOR_STATS
        files = get_files_in_table("file.config#share.schema.table")
        print(files)
        assert files == [
            {
                "id": "id1",
                "size": 120,
                "partition_values": {"month": "202001"},
                "timestamp": None,
                "version": None,
                **STATS1,
            },
            {
                "id": "id2",
                "size": 120,
                "partition_values": {"month": "202002"},
                "timestamp": None,
                "version": None,
                **STATS2,
            },
        ]
