from database_services.RDBService import RDBService


def t1():
    res = RDBService.get_by_prefix(
        "demo_flask", "names_basic_recent", "primaryName", "Tom H")#schema_name, table_name, column, value (not sure if correspond but ukwim)
    print("t1 resule = ", res)


def t2():

    res = RDBService.find_by_template(
        "demo_flask", "names_basic_recent", {"primaryName": "Tom Hanks"}, None
    )
    print("t2 resuls = ", res)


def t3():

    res = RDBService.create(
        "aaaaf21", "user",
            {
                "last_name": "Zhang",
                "first_name": "Olivia",
                "email": "xz2997@columbia.edu",
                "status": "USA"
            })
    print("t3: res = ", res)

#t2()
t1()


