
from pyairtable import Table

def create_record(table: Table, record: dict) -> dict:
    result = table.create(record)
    return result
