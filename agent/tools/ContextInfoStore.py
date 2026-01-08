from typing import List, Any

from pydantic import BaseModel,Field


class ReviewRequest(BaseModel):
    """ 审核请对象 """
    actionName: str = Field(description="审核请求的动作名称")
    actions: List[str] = Field(description="审核请求的动作列表")
    id: str = Field(description="审核请求的id")
    content: dict[str,Any] = Field(description="审核请求的内容")

    # def __init__(self, actionName: str, actions: List[str], id: str, content: dict[str,Any] ):
    #     super().__init__(actionName = actionName, actions = actions, id = id, content = content)
    #     self.actionName = actionName
    #     self.actions = actions
    #     self.id = id
    #     self.content = content


class ReviewResponse(BaseModel):
    """ 审核请对象 """
    actionName: str = Field(description="审核响应的动作名称")
    doAction: str = Field(description="审核响应的动作列表")
    id: str = Field(description="审核响应的id")
    content: dict[str, Any] = Field(description="审核请求的内容")

    # def __init__(self, actionName: str, doAction: str, id: str, content: dict[str,Any] ):
    #     super().__init__(actionName = actionName, doAction = doAction, id = id, content = content)
    #     self.actionName = actionName
    #     self.doAction = doAction
    #     self.id = id
    #     self.content = content


class ReviewContxtInfo:
    """ 审核请求响应上下文信息 """
    #= Field(description="审核请求信息",default={})
    # = Field(description="审核响应信息", default={})

    reviewRequestMap: dict[str, ReviewRequest | None] = {}

    reviewResponseMap: dict[str,ReviewResponse | None] = {}

    # reviewRequestMap = {}
    # reviewResponseMap = {}

    @classmethod
    def putRequest(cls, id: str, reviewRequest: ReviewRequest) -> bool:
        cls.reviewRequestMap[id] = reviewRequest
        return True

    @classmethod
    def putResponse(cls, id: str, reviewResponse: ReviewResponse) -> bool:
        cls.reviewResponseMap[id] = reviewResponse
        return True

    @classmethod
    def getReviewRequest(cls, id: str) -> ReviewRequest:
        if not id:
            return None
        return cls.reviewRequestMap[id]

    @classmethod
    def getReviewRequest(cls, id: str) -> ReviewResponse:
        if not id:
            return None
        return cls.reviewResponseMap[id]


if __name__ == "__main__":
    print(f"Atrtrbute: {dir(ReviewContxtInfo)}")


