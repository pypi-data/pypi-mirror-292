import os
from unittest.mock import patch

from delta_sharing import Schema, Share, Table  # type: ignore

from ..sharing import DeltaSharingCredentials, SharingClient, TemaAIShareAPI
from .test_credentials import ENVIRON, MOCKED_CREDENTIALS

CONNECTION_NAME = "recipient"
SHARE = Share("share")
SCHEMA = Schema("schema", "share")
TABLE = Table("table", "share", "schema")


class TestDeltaShare:
    @property
    @patch.dict(os.environ, ENVIRON)
    def sharer(self):
        return TemaAIShareAPI(CONNECTION_NAME)

    def test_connection_name(self):
        assert self.sharer.connection_name == CONNECTION_NAME

    @patch.object(DeltaSharingCredentials, "refresh")
    def test_credentials(self, mock_cred):
        sharer = self.sharer
        cred = sharer.credentials
        mock_cred.assert_called_with(CONNECTION_NAME, host=None)
        sharer.credentials
        #  because there is a caching mechanism we should only hve 1 call
        assert mock_cred.call_count == 1

    @patch.object(DeltaSharingCredentials, "refresh")
    def test_client(self, mock_cred):
        mock_cred.return_value = DeltaSharingCredentials(
            MOCKED_CREDENTIALS, CONNECTION_NAME
        )
        sharer = self.sharer
        sharer.client
        mock_cred.assert_called_with(CONNECTION_NAME, host=None)
        client = sharer.client
        # only 1 call because of the cache for 1 hour
        assert mock_cred.call_count == 1
        assert client._profile.bearer_token == MOCKED_CREDENTIALS["bearerToken"]
        assert client._profile.endpoint == MOCKED_CREDENTIALS["endpoint"]

    @patch.object(DeltaSharingCredentials, "refresh")
    def _test_fnc(
        self, fnc, mock_cred, args=()
    ):  # the with args is to to interfere with the mock
        mock_cred.return_value = DeltaSharingCredentials(
            MOCKED_CREDENTIALS, CONNECTION_NAME
        )
        return getattr(self.sharer, fnc)(*args)

    @patch.object(SharingClient, "list_shares")
    def test_shares(self, mock_c):
        self._test_fnc("shares")
        mock_c.assert_called_with()

    @patch.object(SharingClient, "list_schemas")
    def test_schemas(self, mock_c):
        self._test_fnc("schemas", args=[SHARE])
        mock_c.assert_called_with(SHARE)

    @patch.object(SharingClient, "list_tables")
    def test_tables(self, mock_c):
        self._test_fnc("tables", args=[SCHEMA])
        mock_c.assert_called_with(SCHEMA)

    @patch.object(SharingClient, "list_all_tables")
    def test_list_all_tables(self, mock_c):
        self._test_fnc("list_all_tables")
        mock_c.assert_called_with()

    @patch.object(DeltaSharingCredentials, "to_file")
    @patch.object(DeltaSharingCredentials, "refresh")
    def _test(self, fnc, path, mock_cred, mock_to_file):
        mock_to_file.return_value = path
        mock_cred.return_value = DeltaSharingCredentials(
            MOCKED_CREDENTIALS, CONNECTION_NAME
        )
        return getattr(self.sharer, fnc)(TABLE)

    @patch("tema_ai.connect.sharing.load_as_pandas")
    def test_table_to_pandas(self, mock_table):
        path = "file.config"
        self._test("table_to_pandas", path)
        mock_table.assert_called_with(f"{path}#share.schema.table")

    @patch("tema_ai.connect.sharing.get_table_schema")
    def test_table_schema(self, mock_table):
        path = "file.config"
        self._test("table_schema", path)
        mock_table.assert_called_with(f"{path}#share.schema.table")

    @patch("tema_ai.connect.sharing.get_files_in_table")
    def test_get_files_in_table(self, mock_table):
        path = "file.config"
        self._test("table_files", path)
        mock_table.assert_called_with(f"{path}#share.schema.table")

    @patch.object(TemaAIShareAPI, "table_files")
    def test_table_report(self, mock_table):
        mock_table.return_value = [
            {"numRecords": 10, "size": 10, "partition_values": {"years": "2023"}}
        ]
        path = "file.config"
        report = self._test("table_report", path)
        print(report)
        assert report == {
            "num_files": 1,
            "partition_columns": ["years"],
            "total_records": 10,
            "avg_records_per_file": 10,
            "size": 10,
            "avg_size_per_file": 10,
        }
