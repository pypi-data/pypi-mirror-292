from pyairtable import Table

from airtable_pack.operations.get_record import get_record

def update_fields(table: Table, filter_: dict, fields: dict) -> dict:
    record = get_record(table=table, filter_=filter_)
    record_id = record[0]["id"]
    return table.update(record_id, fields)
