from typing import List

from pyairtable import Table
from pyairtable.formulas import match

def get_record(table: Table, filter_: dict) -> List[dict]:
    formula = match(filter_)
    result = table.all(formula=formula)
    return result
