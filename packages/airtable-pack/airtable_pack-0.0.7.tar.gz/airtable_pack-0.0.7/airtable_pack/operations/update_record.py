from pyairtable import Table
from pyairtable.formulas import match

def update_record(table: Table, filter_: dict, update: dict) -> dict:
    """ TODO: Poner docstring."""
    formula = match(filter_)
    record = table.all(formula=formula)
    if len(record) > 0:
        id_ = record[0]['id']
        result = table.update(id_, update)
        return result
    else:
        return []