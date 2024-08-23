from pyairtable import Table
from pyairtable.formulas import match

def delete_record(table: Table, filter_: dict) -> dict:
    formula = match(filter_)
    result = table.delete(formula['id'])
    return result
