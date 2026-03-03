from typing import List, Any

from pydantic import BaseModel,Field


class ReviewRequest(BaseModel):
    """ 审核请对象 """
    actionName: str = Field(description="审核请求的动作名称")
    actions: List[str] = Field(description="审核请求的动作列表")
    id: str = Field(description="审核请求的id")
    content: dict[str,Any] = Field(description="审核请求的内容")

    # def __init__(self, actionName: str, actions: List[str], id: str, content: dict[str,Any] ):
    #     super().__init__(actionName=actionName, actions=actions, id=id, content=content)
    #     self.actionName = actionName
    #     self.actions = actions
    #     self.id = id
    #     self.content = content


class ReviewResponse(BaseModel):
    """ 审核请对象 """
    actionName: str = Field(description="审核响应的动作名称", default="审核操作")
    doAction: str = Field(description="审核响应的动作列表")
    id: str = Field(description="审核响应的id")
    content: Any | dict[str, Any] = Field(description="审核请求的内容")


    # def __init__(self, actionName: str, doAction: str, id: str, content: dict[str,Any] ):
    #     super().__init__(actionName=actionName, doAction=doAction, id=id, content=content)
    #     self.actionName = actionName
    #     self.doAction = doAction
    #     self.id = id
    #     self.content = content


class ReviewContxtInfo:
    """ 审核请求响应上下文信息 """
    #= Field(description="审核请求信息",default={})
    # = Field(description="审核响应信息", default={})

    reviewRequestMap: dict[str, dict[str, ReviewRequest | None]] = {}

    reviewResponseMap: dict[str, dict[str, ReviewResponse | None]] = {}

    # reviewRequestMap = {}
    # reviewResponseMap = {}

    @classmethod
    def putRequest(cls, user_id: str, key: str, reviewRequest: ReviewRequest) -> bool:
        request_map = cls.reviewRequestMap.get(user_id, None)
        if not request_map:
            request_map = cls.reviewRequestMap[user_id] = {}
        request_map.setdefault(key, reviewRequest)
        # cls.reviewResponseMap[id] = reviewResponse
        return True

    @classmethod
    def putResponse(cls, user_id: str, key: str, reviewResponse: ReviewResponse) -> bool:
        response_map = cls.reviewResponseMap.get(user_id, None)
        if not response_map:
            response_map = cls.reviewResponseMap[user_id] = {}
        response_map.setdefault(key, reviewResponse)
        # cls.reviewResponseMap[id] = reviewResponse
        return True

    @classmethod
    def getReviewRequest(cls, user_id: str, key: str = None) -> ReviewRequest | dict[str, ReviewRequest]:
        '''
        根据指定的用户ID和 关键字 key，查询指定的数据并返回，
        如果Key 没有传，默认返回user_id 下的所有数据。
        如果用户ID 为空，或者 数据不存在，则返回None
        :param user_id:
        :param key:
        :return:
        '''
        if not user_id:
            return None

        if key:
            user_map = cls.reviewRequestMap.get(user_id, None)
            if user_map:
                return user_map.get(key, None)
            else:
                return None

        else:
            return cls.reviewRequestMap.get(user_id, None)

    @classmethod
    def getReviewResponse(cls, user_id: str, key: str = None) -> ReviewResponse | dict[str,ReviewResponse]:
        '''
        根据指定的用户ID和 关键字 key，查询指定的数据并返回，
        如果Key 没有传，默认返回user_id 下的所有数据。
        如果用户ID 为空，或者 数据不存在，则返回None
        :param user_id:
        :param key:
        :return:
        '''
        if not user_id:
            return None

        if key:
            user_map = cls.reviewResponseMap.get(user_id, None)
            if user_map:
                return user_map.get(key, None)
            else:
                return None

        else:
            return cls.reviewResponseMap.get(user_id, None)


    @classmethod
    def removeReviewMessage(cls, user_id: str, key: str = None) -> bool:
        '''
        根据指定的用户ID 和 指定的 key , 从当前存储中移除指定元素。
        如果 key 没有传，则默认移除所有的 user_id 数据。
        成功返回True, 失败 返回False, 如果数据不存在默认返回： True
        :param user_id:
        :param key:
        :return:
        '''
        if not user_id:
            raise Exception("Type key user_id can't be null!")

        if not key:
            cls.reviewRequestMap.pop(user_id, None)
            return True

        else:
            user_map = cls.reviewRequestMap.get(user_id, None)
            if not user_map:
                return True

            user_map.pop(key, None)

        return True

    @classmethod
    def removeResponseMessage(cls, user_id: str, key: str = None) -> bool:
        '''
        根据指定的用户ID 和 指定的 key , 从当前存储中移除指定元素。
        如果 key 没有传，则默认移除所有的 user_id 数据。
        成功返回True, 失败 返回False, 如果数据不存在默认返回： True
        :param user_id:
        :param key:
        :return:
        '''
        if not user_id:
            raise Exception("Type key user_id can't be null!")

        if not key:
            cls.reviewResponseMap.pop(user_id, None)
            return True

        else:
            user_map = cls.reviewResponseMap.get(user_id, None)
            if not user_map:
                return True

            user_map.pop(key, None)

        return True



if __name__ == "__main__":
    print(f"Atrtrbute: {dir(ReviewContxtInfo)}")
    mutilMap = {}
    result = mutilMap.get("first")
    if not result:
         mutilMap["first"] = result = {}

    result.setdefault("name","Hi")


    # mutilMap["first"] = "Hi"
    print(f"Multi map: {mutilMap}")
