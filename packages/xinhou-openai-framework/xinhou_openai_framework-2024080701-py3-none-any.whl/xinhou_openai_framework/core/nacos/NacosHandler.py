# !/usr/bin/python3
# -*- coding: utf-8 -*-
"""
初始化缓存处理器
----------------------------------------------------
@Project :   xinhou-openai-framework
@File    :   CacheHandler.py
@Contact :   sp_hrz@qq.com

@Modify Time      @Author    @Version    @Desciption
------------      -------    --------    -----------
2023/4/4 17:33   shenpeng   1.0         None
"""

from apscheduler.schedulers.asyncio import AsyncIOScheduler

from xinhou_openai_framework.core.beans.BeansContext import BeansContext
from xinhou_openai_framework.core.contents.AppContents import AppContents
from xinhou_openai_framework.core.context.model.AppContext import AppContext
from xinhou_openai_framework.core.nacos.NacosManager import NacosManager


class NacosHandler:

    @staticmethod
    def init_handler(app, context: AppContext):
        @app.on_event("startup")
        def startup_nacos_manager_event():
            if (hasattr(context.framework, AppContents.CTX_YML_NODE_CLOUD)
                    and context.framework.cloud.nacos.discovery.enabled):
                nacos = NacosManager(
                    server_endpoint=context.framework.cloud.nacos.discovery.server_addr,
                    namespace_id=context.framework.cloud.nacos.discovery.namespace_id,
                    username=context.framework.cloud.nacos.discovery.username,
                    password=context.framework.cloud.nacos.discovery.password
                )
                nacos.set_service(
                    service_name=context.application.name,
                    service_port=context.application.server.post,
                    service_group=context.framework.cloud.nacos.discovery.group
                )
                nacos.register()
                BeansContext.add_instance(NacosManager.__name__, nacos)
                beat_interval = AppContents.CTX_NACOS_BEAT_INTERVAL_DEFAULT_VALUE
                if (hasattr(context.framework.cloud.nacos.discovery, AppContents.CTX_NACOS_BEAT_INTERVAL_KEY)):
                    beat_interval = context.framework.cloud.nacos.discovery.beat_interval if context.framework.cloud.nacos.discovery.beat_interval is not None else AppContents.CTX_NACOS_BEAT_INTERVAL_DEFAULT_VALUE
                scheduler = AsyncIOScheduler()
                scheduler.add_job(nacos.beat_callback, 'interval', seconds=beat_interval)
                scheduler.start()

        @app.on_event("shutdown")
        async def shutdown_nacos_manager_event():
            if BeansContext.get_instance(__name__) is not None:
                BeansContext.get_instance(__name__).unregister()
