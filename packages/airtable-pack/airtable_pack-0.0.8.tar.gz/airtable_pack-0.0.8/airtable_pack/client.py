from typing import TypeVar, List

from pyairtable import Api, Base, Table

from airtable_pack.operations.create_record import create_record
from airtable_pack.operations.delete_record import delete_record
from airtable_pack.operations.get_record import get_record
from airtable_pack.operations.update_fields import update_fields
from airtable_pack.operations.update_record import update_record

T_Airtable = TypeVar("T_Airtable", bound="Airtable")

class Airtable:
    def __init__(self, api_key: str, base_id: str):
        self.api = Api(api_key=api_key)
        self.base_id: str = base_id
        self.base: Base = self.api.base(self.base_id)
    
    def get_table(self, table_name: str) -> Table:
        return self.base.table(table_name)

    def create_record(self, table: Table, record: dict) -> dict:
        return create_record(table=table, record=record)

    def get_record(self, table: Table, filter_: dict) -> List[dict]:
        return get_record(table=table, filter_=filter_)

    def delete_record(self, table: Table, filter_: dict) -> dict:
        return delete_record(table=table, filter_=filter_)

    def update_fields(self, table: Table, filter_: dict, fields: dict) -> dict:
        return update_fields(table=table, filter_=filter_, fields=fields)

    def update_record(self, table: Table, filter_: dict, update: dict):
        return update_record(table=table, filter_=filter_, update=update)
