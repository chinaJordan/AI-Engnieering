from langgraph.checkpoint.postgres import PostgresSaver
import psycopg

DB_URL = "postgresql://admin:admin@localhost:5432/postgres?sslmode=disable"

print(f"Psycopg: {psycopg.__version__};  File: {psycopg.__file__}")


def getCheckpointer() -> PostgresSaver:
    with PostgresSaver.from_conn_string(DB_URL) as checkponiter:
        checkponiter.setup()
        config = {"configurable": {"thread_id": "1"}}
        response = list(checkponiter.list(config=config))
        print(f"Response data: {response}")


def getDbConnect(url: str | None):
    if not url:
        connect = psycopg.connect(conninfo=DB_URL)
    else:
        connect = psycopg.connect(conninfo=url)
    connect.autocimmit = False
    return connect


"""
    创建数据库表方法，可以指定表名字，如果不传默认： user
"""


def createTable(tableName: str | None):
    connect = getDbConnect(None)
    connect.autocimmit = True
    cursor = connect.cursor()
    if not tableName:
        tableName = "user"
    create_table_sql = f"""
        CREATE TABLE IF NOT EXISTS "{tableName}" (
            id serial primary key,
            name varchar(50),
            score integer,
            email varchar(100),
            create_time timestamp default current_timestamp
        );
    """
    cursor.execute(create_table_sql)
    connect.commit()


def deleteTable(tablename: str | None) -> bool:
    if not tablename:
        print(f"Current table name is {tablename}, can't be null!")
        return False
    deleteSql = f""" DROP TABLE {tablename} """
    connect = getDbConnect(None)
    cursor = connect.cursor()
    cursor.execute(deleteSql)
    connect.commit()

    queryTableExist = f""" SELECT EXISTS(
        select 1 from information_schema.tables where table_name = '{tablename}'
      AND table_schema = 'public'   
      AND table_type = 'BASE TABLE'
    ) as table_exist; """

    cursor.execute(queryTableExist)
    result = cursor.fetchone()

    print(f"Query table result: {result}")
    return result


def queryData():
    connect = getDbConnect(None)
    cursor = connect.cursor()
    # cursor.itersize = 100  where "id"=1
    querySql = """select * from "user";"""
    describe_table = """ SELECT table_schema, table_name 
        FROM information_schema.tables 
        WHERE table_type = 'BASE TABLE' 
        AND table_schema NOT IN ('pg_catalog', 'information_schema'); """

    # 仅将SQL发送到服务端，不返回结果
    cursor.execute(describe_table)
    connect.commit()
    results = cursor.fetchmany(size=100)
    description = cursor.description
    if not description:
        print("Can't find table column data! Only return data!")
    columnNames = [descrp[0] for descrp in description]

    for row in results:
        rowLen = len(row)
        dictData = dict(zip(columnNames, row))
        dateTime = dictData.get("create_time", None)
        if not dateTime:
            pass
        else:
            # 转为字符串格式 example: 2025-12-24 13:00:32
            # dictData["create_time"] = dateTime.strftime("%Y-%m-%d %H:%M:%S")

            # 转为时间戳
            dictData["create_time"] = dateTime.timestamp()
        print(f"return data : {dictData}")

    # print(f"id: {row[0]}, name: {row[1]}, score: {row[2]}, email: {row[3]}, create_time: {row[4]}")


def insertDataToTable():
    with getDbConnect(None) as connect:
        cursor = connect.cursor()
        insert_sql = """
            insert into "user" ("name","score","email") VALUES('闻韶华', 90, '13545678@139.com');
        """
        cursor.execute(insert_sql)
        connect.commit()
    print(f"Insert data Success!")


if __name__ == "__main__":
    getCheckpointer()
    # connect = psycopg.connect(conninfo=DB_URL)

    # cursor.execute(create_table_sql)
    # print(f"Create table user Success!")
    # cursor.execute(insert_sql)
    # createTable()
    # deleteTable("user2")

    # insertTable()
    queryData()
