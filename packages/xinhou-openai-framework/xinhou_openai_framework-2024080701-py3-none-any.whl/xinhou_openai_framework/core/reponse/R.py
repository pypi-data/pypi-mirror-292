# !/usr/bin/python3
# -*- coding: utf-8 -*-
"""
全局响应模型
----------------------------------------------------
@Project :   xinhou-openai-framework
@File    :   R.py
@Contact :   sp_hrz@qq.com

@Modify Time      @Author    @Version    @Desciption
------------      -------    --------    -----------
2021/7/12 12:55   shenpeng   1.0         None
"""
import base64
import json
from datetime import datetime
from typing import Optional

from fastapi import Request
from starlette.responses import JSONResponse, StreamingResponse
from starlette.templating import Jinja2Templates

from xinhou_openai_framework.core.exception.CodeEnum import CodeEnum
from xinhou_openai_framework.core.reponse.ReturnData import ReturnData
from xinhou_openai_framework.pages.Paginate import Paginate
from xinhou_openai_framework.utils.QueryUtil import QueryUtil


class CustomJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, bytes):
            return base64.b64encode(obj).decode('utf-8')
        if isinstance(obj, datetime):
            return obj.isoformat()
        return super().default(obj)


class R:
    """
    返回响应对象
    """

    @staticmethod
    def SUCCESS(data: Optional[dict] = None):
        return R.jsonify(CodeEnum.SUCCESS, data=data)

    @staticmethod
    def NO_PARAMETER():
        return R.jsonify(CodeEnum.NO_PARAMETER)

    @staticmethod
    def PARAMETER_ERR(data=None):
        return R.jsonify(CodeEnum.PARAMETER_ERROR, data=data)

    @staticmethod
    def OTHER_LOGIN():
        return R.jsonify(CodeEnum.OTHER_LOGIN)

    @staticmethod
    def AUTH_ERR():
        return R.jsonify(CodeEnum.UNAUTHORIZED)

    @staticmethod
    def TOKEN_ERROR():
        return R.jsonify(CodeEnum.ERROR_TOKEN)

    @staticmethod
    def REQUEST_ERROR():
        return R.jsonify(CodeEnum.BAD_REQUEST)

    @staticmethod
    def ID_NOT_FOUND():
        return R.jsonify(CodeEnum.ID_NOT_FOUND)

    @staticmethod
    def SAVE_ERROR():
        return R.jsonify(CodeEnum.DB_ERROR)

    @staticmethod
    def UPDATE_ERROR():
        return R.jsonify(CodeEnum.DB_ERROR)

    @staticmethod
    def DELETE_ERROR():
        return R.jsonify(CodeEnum.DB_ERROR)

    @staticmethod
    def FILE_NO_FOUND():
        return R.jsonify(CodeEnum.FILE_NOT_FOUND)

    @staticmethod
    def ERROR_FILE_TYPE():
        return R.jsonify(CodeEnum.ERROR_FILE_TYPE)

    @staticmethod
    def UPLOAD_FAILD():
        return R.jsonify(CodeEnum.UPLOAD_FAILED)

    @staticmethod
    def OVER_SIZE():
        return R.jsonify(CodeEnum.OVER_SIZE)

    @staticmethod
    def SERVER_ERROR():
        return R.jsonify(CodeEnum.INTERNAL_SERVER_ERROR)

    @staticmethod
    def template(request: Request, dir_name, tpl_file, data=None):
        templates = Jinja2Templates(directory="templates/default/" + dir_name)
        if data is not None:
            if isinstance(data, Paginate):
                data = ReturnData.page_to_dict(data)
            else:
                data = QueryUtil.query_set_to_dict(data)
        return templates.TemplateResponse(
            tpl_file, {
                "request": request,
                "base_url": request.base_url,  # 基本请求路径
                "data": data
            })

    @staticmethod
    def jsonify(code_enum: CodeEnum, data=None):
        if data is not None:
            if isinstance(data, Paginate):
                data = ReturnData.page_to_dict(data)
            elif isinstance(data, bool):
                data = data
            else:
                data = QueryUtil.query_set_to_dict(data)

        content = {
            "code": code_enum.value['code'],
            "msg": code_enum.value['msg'],
            "data": data
        }

        # 使用 CustomJSONEncoder 序列化内容
        json_str = json.dumps(content, cls=CustomJSONEncoder)

        # 将序列化后的字符串解析回 Python 对象
        json_data = json.loads(json_str)

        # 使用处理后的数据创建 JSONResponse
        return JSONResponse(content=json_data)

    @staticmethod
    def Streaming(auto_generate_function):
        return StreamingResponse(auto_generate_function(), headers={
            "Content-Type": "text/event-stream",
            "Cache-Control": "no-cache",
        }, media_type="text/event-stream")
