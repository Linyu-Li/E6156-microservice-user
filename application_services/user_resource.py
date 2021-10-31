from application_services.BaseApplicationResource import BaseRDBApplicationResource
from database_services.RDBService import RDBService


class UserResource(BaseRDBApplicationResource):

    def __init__(self):
        super().__init__()

    @classmethod
    def get_links(cls, resource_data):
        pass

    @classmethod
    def get_all_users(cls):
        res = RDBService.get_all("users", "User")
        return res

    @classmethod
    def insert_users(cls, column_name_list, value_list):  # db_schema, table_name, column_name_list, value_list
        return RDBService.insert("users", "User", column_name_list, value_list, return_id=True)

    @classmethod
    def get_by_user_id(cls, user_id):
        res = RDBService.get_by_value("users", "User",
                                      "userID", user_id)
        return res

    @classmethod
    def exists_by_email(cls, email):
        return len(RDBService.get_by_value("users", "User", "email", "'{}'".format(email))) > 0

    @classmethod
    def get_user_id_by_email_pwd(cls, email, pwd):
        res = RDBService.find_by_template("users", "User", {
            'email': email,  # "'{}'".format(email),
            'password': pwd,
        }, ['userID'])
        if len(res):
            return res[0]
        return None

    @classmethod
    def update_by_uid(cls, user_id, column_name, value):
        res = RDBService.update_by_column("users", "User", "userID", user_id, column_name, value)
        return res

    @classmethod
    def delete_by_uid(cls, user_id):
        res = RDBService.delete_by_column("users", "User", "userID", user_id)
        return res
