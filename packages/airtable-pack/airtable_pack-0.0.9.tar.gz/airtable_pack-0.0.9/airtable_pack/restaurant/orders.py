from typing import List, Tuple, Optional
import traceback
import os
import logging

from pyairtable.orm import Model, fields as F

logger = logging.getLogger(__name__)


class RestOrder(Model):
    phone = F.TextField("phone")
    name = F.TextField("name")
    order_id = F.NumberField("order_id")
    address = F.TextField("address")
    number_address = F.NumberField("number_address")
    apartment = F.TextField("apartment") 
    status_payment = F.CheckboxField("status_payment")
    status_delivery = F.MultipleSelectField("status_delivery")
    url_payment = F.TextField("url_payment")

    class Meta:
        base_id = os.getenv('RESTEST_AIRTABLE_BASE_ID')
        table_name = "orders"
        api_key = os.getenv('RESTEST_AIRTABLE_API_KEY')

    @classmethod
    def create_fields(cls):
        table = cls.get_table()
        name_type_options: List[Tuple[str, str, Optional[dict]]] = [
            ("name", "singleLineText", None),
            ("order_id", "number", {"precision": 0}),
            ("address", "singleLineText", None),
            ("number_address", "number", {"precision": 0}),
            ("apartment", "singleLineText", None),
            ("status_payment", "checkbox", {"color": "greenBright", "icon": "xCheckbox"})
        ]
        name_type_options.append((
            "status_delivery", "multipleSelects", {
                "choices": [
                    {"name": "order_processing"},
                    {"name": "underway"},
                    {"name": "delivered"}
                ]
            }
        ))
        name_type_options.append(("url_payment", "url", None))


        for field_name, field_type, options in name_type_options:
            msg = f"--> field_name={field_name} | field_type={field_type}"
            try:
                table.create_field(field_name, field_type, options=options)
                logger.info(msg)
            except Exception as e:
                logger.warning(f"{msg} | error={e}")
                logger.warning(traceback.format_exc())
