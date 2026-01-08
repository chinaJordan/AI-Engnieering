from typing import List, Dict, Any

from pydantic import BaseModel, Field, EmailStr, ConfigDict
from pydantic.alias_generators import to_camel
from agent.memory.PgSqlShortMemory import getDbConnect

TABEL_NAME = "userinfo"

CREATE_TABLE = """
    create table if not exists userinfo(
        id BIGSERIAL primary key,
        user_name varchar(50) UNIQUE,
        pass_word varchar(64),
        phone varchar(30) UNIQUE,
        email varchar(60),
        create_time timestamp default current_timestamp,
        update_time timestamp default current_timestamp
    );
"""


# columns = ()
# values = ()
# INSERT_SQL = """
#     insert into userinfo {} values{};
# """


def snake_to_camel(snakerStr: str) -> str:
    """
    下划线转驼峰式命名
    :param snakerStr:
    :return:
    """
    if not snakerStr:
        return None
    words = snakerStr.split("_")
    return words[0] + "".join(word.capitalize() for word in words[1:])


def dynamicSqlGenerate(data: dict[str, Any], operate: str, tableName: str | None, limit=100, offset=0, queryCondition = None ) -> str:
    if not data or not operate:
        print(f"Data and operate can't be Null!")
        return None

    match operate:
        case "select":
            condition = queryCondition if queryCondition else " and "
            whereSql = condition.join(f"{key} = %s" for key, value in data.items())
            return f"select * from {tableName if tableName else 'userinfo'} where " + \
                whereSql + f" limit {limit} offset {offset};"
        case "insert":
            columns = "(" + ",".join(data.keys()) + ")"
            placeholders = "(" + ",".join(["%s"] * len(data)) + ")"
            return f"insert into {tableName if tableName else 'userinfo'} {columns} values {placeholders}"
        case "delete":
            condition = queryCondition if queryCondition else " and "
            whereSql = condition.join(f"{key} = %s" for key, value in data.items())
            return f"delete from {tableName if tableName else 'userinfo'} where {whereSql}"
        case "update":
            """ 更新语句必须根据主键ID更新，所以这里会将id 字段单独取出来，其它值作为更新值 """
            id = data.get("id", None)
            if not id:
                raise Exception(f"The update operate must have id!")
            data.pop("id", None)
            setSql = " , ".join(f"{key} = %s" for key, value in data.items())
            return f"update {tableName if tableName else 'userinfo'} set {setSql} where id={id}"
        case _:
            raise Exception(f"The operate {operate} is not support!")


class BaseEntity(BaseModel):
    model_config = ConfigDict(
        alias_generator=to_camel,
        validate_by_name=True,
        validate_by_alias=True,
        from_attributes=True
    )


class UserDTO(BaseEntity):
    user_name: str = Field(description="用户名")
    pass_word: str = Field(description="用户密码", min_length=8, max_length=32)
    phone: str = Field(description="用户手机号")
    email: str | None = None
    create_time: str | None = None
    update_time: str | None = None
    id: int | None = None


class UserInfo(BaseEntity):
    user_name: str = Field(description="用户名", default=None)
    pass_word: str = Field(description="用户密码", min_length=8, max_length=32, default=None)
    phone: str = Field(description="用户手机号", default=None)
    email: str | None = None
    create_time: str | None = None
    update_time: str | None = None
    id: int | None = None
    salt: str | None = None

    def insertToDb(self,insertList: List["UserInfo"]) -> int:
        """
        向数据库插入多条数据，如果插入失败，返回None, 插入成功，返回对应插入的条数
        :param insertList:
        :return:
        """
        if not insertList:
            print(f"The input data is Empty!")
            return 0
        dbconnect = None
        cursor = None
        dictData = None
        try:

            dbconnect = getDbConnect(None)
            cursor = dbconnect.cursor()

            for userInfo in insertList:
                if isinstance(userInfo, UserInfo):
                    dictData = userInfo.model_dump(exclude_none=True)
                    insertSQL = dynamicSqlGenerate(dictData, "insert", tableName=None)
                    values = tuple(dictData.values())
                    print(f"Insert SQl: {insertSQL}, values: {values}")
                    cursor.execute(insertSQL, values)
            dbconnect.commit()
        except Exception as e:
            dbconnect.rollback()
            print(f"Insert data to DB fail, data: {dictData}, Exception: {e}")
            return None
        finally:
            if cursor: cursor.close()
            if dbconnect: dbconnect.close()

        return len(insertList)


    def queryFromDb(self, queryData: "UserInfo", *,queryCondition=None) -> List[dict[str, Any]]:
        if not queryData:
            return []
        dbconnect = None
        cursor = None
        dictData = None
        resultsConvert = []
        try:

            dbconnect = getDbConnect(None)
            cursor = dbconnect.cursor()

            dictData = queryData.model_dump(exclude_none=True)
            querySql = dynamicSqlGenerate(dictData, "select", tableName=None, queryCondition=queryCondition)
            values = tuple(dictData.values())
            print(f"Query sql: {querySql}, values: {values}")

            cursor.execute(querySql, values)
            results = cursor.fetchall()
            description = cursor.description
            if not description:
                print("Can't find table column data! Only return data!")
            columnNames = [descrp[0] for descrp in description]

            for row in results:
                columnToValue = dict(zip(columnNames, row))
                createTime = columnToValue.get("create_time", None)
                updateTime = columnToValue.get("update_time", None)
                if createTime: columnToValue["create_time"] = createTime.strftime("%Y-%m-%d %H:%M:%S")
                if updateTime: columnToValue["update_time"] = updateTime.strftime("%Y-%m-%d %H:%M:%S")
                resultsConvert.append(columnToValue)
                # if not createTime:
                #     pass
                # else:
                #     # 转为字符串格式 example: 2025-12-24 13:00:32
                #     columnToValue["create_time"] = createTime.strftime("%Y-%m-%d %H:%M:%S")

                # 转为时间戳
                # columnToValue["create_time"] = dateTime.timestamp()

        except Exception as e:
            print(f"Query data from DB fail, data: {queryData}, Exception: {e.__traceback__}")
        finally:
            if cursor: cursor.close()
            if dbconnect: dbconnect.close()

        return resultsConvert


    def updateFromDb(self,updateData: "UserInfo", *, queryCondition = None) -> int:
        if not updateData:
            return 0
        dbconnect = None
        cursor = None
        dictData = None
        try:
            dbconnect = getDbConnect(None)
            cursor = dbconnect.cursor()

            dictData = updateData.model_dump(exclude_none=True)
            values = tuple(v for k, v in dictData.items() if k != "id")
            updateSql = dynamicSqlGenerate(dictData, "update", tableName=None, queryCondition=queryCondition)
            cursor.execute(updateSql, values)

            dbconnect.commit()
        except Exception as e:
            dbconnect.rollback()
            print(f"Update from DB fail, data: {updateData}, Exception: {e}")
        finally:
            if cursor: cursor.close()
            if dbconnect: dbconnect.close()

        return 1


    def deleteFromDb(self,deleteData: "UserInfo") -> int:
        """
        从数据库删除数据，删除成功返回1或者0， 0表示没有删除， 删除失败返回None
        :param deleteData:
        :return:
        """
        if not deleteData:
            return 0
        dbconnect = None
        cursor = None
        dictData = None
        try:
            dbconnect = getDbConnect(None)
            cursor = dbconnect.cursor()

            dictData = deleteData.model_dump(exclude_none=True)
            values = tuple(dictData.values())
            deleteSql = dynamicSqlGenerate(dictData, "delete", tableName=None)
            cursor.execute(deleteSql, values)
            print(f"Delete SQL: {deleteSql}, Values; {values}")
            dbconnect.commit()
        except Exception as e:
            dbconnect.rollback()
            print(f"Delete data from DB fail, data: {deleteData}, Exception: {e}")
            return None
        finally:
            if cursor: cursor.close()
            if dbconnect: dbconnect.close()

        return 1


def createTable() -> bool:
    dbconnect = None
    cursor = None
    try:
        dbconnect = getDbConnect(None)
        cursor = dbconnect.cursor()

        cursor.execute(CREATE_TABLE)
        dbconnect.commit()
    except Exception as e:
        dbconnect.rollback()
        print(f"Create table {TABEL_NAME} fail !, Exception: {e}")
        return False
    finally:
        if cursor: cursor.close()
        if dbconnect: dbconnect.close()

    return True

def __executeSQL(executeSql: str) -> Any:
    if not  executeSql:
        print(f"Execute sql can't be NUll!")
        return False
    dbconnect = None
    cursor = None
    try:
        dbconnect = getDbConnect(None)
        cursor = dbconnect.cursor()

        cursor.execute(executeSql)
        results = cursor.fetchall()
        dbconnect.commit()
        return results
    except Exception as e:
        dbconnect.rollback()
        print(f"Execute sql {executeSql} fail !, Exception: {e}")
        return False
    finally:
        if cursor: cursor.close()
        if dbconnect: dbconnect.close()

    return True





if __name__ == "__main__":
    user = UserInfo(pass_word="wer122343243", phone="13723456784")
    print(f"{user}")
    print(f"Dump info: {user.model_dump(by_alias=True, exclude_none=True)}")
    print(f"Dump json info: {user.model_dump_json(by_alias=True, indent=2)}")
    userList = []
    user2 = UserInfo(userName="liwen2", pass_word="wer122343243", phone="13723456764", email="14456732qq.com")
    # userList.append(user2)
    # user2.insertToDb(userList)

    #  创建表
    # result = createTable()
    # print(f"Create table result; {result}")


    # # 插入数据
    # result = insertToDb(userList)
    # print(f"Insert table result; {result}")


    # 查询数据
    query = UserInfo(user_name="liwen2")
    result = user.queryFromDb(query,queryCondition=None)
    print(f"Query table result; {result}")


    #  更新数据
    user.user_name = "zhangfei"
    user.id = 1
    # alterTable = "SELECT column_name,data_type,is_nullable,column_default FROM information_schema.columns WHERE table_schema='public' AND table_name='userinfo';"
    # print(f"Result: {__executeSQL(executeSql=alterTable)}")
    # result = updateFromDb(user)
    # print(f"Update table result; {result}")

    # # 删除数据
    userinfo = UserInfo(user_name="liwen")
    result = userinfo.deleteFromDb(userinfo)
    print(f"Delete table result; {result}")

    #  测试动态SQL
    # dictData = user2.model_dump(exclude_none=True)
    # strSql = dynamicSqlGenerate(dictData, "delete", None);
    # print(f"Insert SQL:  {strSql}")
