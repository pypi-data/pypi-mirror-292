import os
from pyairtable.orm import Model, fields as F


class RestOrder(Model):
    phone = F.TextField("phone")
    order_id = F.NumberField("order_id")
    name = F.TextField("name")
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
        try:
            table.create_field("name", "singleLineText")
        except:
            pass

        try:
            table.create_field("order_id", "number", options= {"precision":0})
        except:
            pass  

        try:  
            table.create_field("name", "singleLineText")
        except:
            pass

        try:
            table.create_field("address", "singleLineText")
        except:
            pass
            
        try:
            table.create_field("number_address", "number")
        except:
            pass

        try:
            table.create_field("apartment","singleLineText")
        except:
            pass


        try:
            table.create_field(
                "status_payment",
                "checkbox", 
                options={"color": "greenBright", "icon": "xCheckbox"}
            )
        except:
            pass

        try:
            table.create_field(
                "status_delivery",
                "multipleSelects",
                options= {"choices": [
                    {"name": "order_processing"},
                    {"name":"underway"},
                    {"name": "delivered"}
                ]}
            )
        except:
            pass

        try:
            table.create_field("url_payment", "url")
        except:
            pass

