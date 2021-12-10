from application_services.BaseApplicationResource import BaseRDBApplicationResource
from database_services.RDBService import RDBService


class AddressResource(BaseRDBApplicationResource):

    def __init__(self):
        super().__init__()

    @classmethod
    def get_links(cls, resource_data):
        pass

    @classmethod
    def get_all_addresses(cls):
        res = RDBService.get_all("users", "address")
        return res

    @classmethod
    def insert_address(cls, column_name_list, value_list): # db_schema, table_name, column_name_list, value_list
        res = RDBService.insert("users", "address", column_name_list, value_list)
        return res

    @classmethod
    def get_by_address_id(cls, address_id):
        res = RDBService.get_by_value("users", "address",
                                      "addressID", address_id)
        return res

    @classmethod
    def update_by_aid(cls, address_id, column_name, value):
        res = RDBService.update_by_column("users", "address", "addressID", address_id, column_name, value)
        return res

    @classmethod
    def delete_by_aid(cls, address_id):
        res = RDBService.delete_by_column("users", "address", "addressID", address_id)
        return res