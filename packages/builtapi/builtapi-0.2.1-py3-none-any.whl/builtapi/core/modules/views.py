from typing import List, Union, Optional, Dict, Any

import requests
from loguru import logger

from builtapi.core.modules.common import BaseModule, api_call
import builtapi.core.schemas.views as views_schemas


class ViewsModule(BaseModule):

    @api_call(url="/trpc/views.list", method="get",
              return_type=views_schemas.ViewsList, schema_class=views_schemas.ListViewsSchema)
    def list(self,
             entity_id: str,
             skip: int = 0,
             take: int = 100,
             search: Optional[Dict[str, Any]] = None,
             orderBy: Optional[List[Dict[str, str]]] = None) -> views_schemas.ViewsList:
        return {
            "entityId": entity_id,
            "skip": skip,
            "take": take,
            "search": search,
            "orderBy": orderBy
        }

    @api_call(url="/trpc/views.listByWorkspace", method="get",
              return_type=views_schemas.ViewsList, schema_class=views_schemas.ListByWorkspaceViewsSchema)
    def list_by_workspace(self,
                          skip: int = 0,
                          take: int = 100,
                          search: Optional[Dict[str, Any]] = None,
                          orderBy: Optional[List[Dict[str, str]]] = None) -> views_schemas.ViewsList:
        return {
            "skip": skip,
            "take": take,
            "search": search,
            "orderBy": orderBy
        }

    @api_call(url="/trpc/views.oneById", method="get",
              return_type=views_schemas.View, schema_class=views_schemas.OneByIdViewSchema)
    def get_one_by_id(self,
                      view_id: str):
        return {
            "viewId": view_id
        }

    @api_call(url="/trpc/views.schema", method="get",
              return_type=views_schemas.ViewSchema, schema_class=views_schemas.SchemaViewSchema)
    def get_schema(self,
                   view_id: str):
        return {
            "viewId": view_id
        }

    @api_call(url="/trpc/views.create", method="post",
              return_type=views_schemas.View, schema_class=views_schemas.CreateViewSchema)
    def create(self,
               entity_id: str,
               name: str,
               pipeline: List[Dict]):
        return {
            "entityId": entity_id,
            "name": name,
            "pipeline": pipeline
        }

    @api_call(url="/trpc/views.update", method="post",
              return_type=views_schemas.View, schema_class=views_schemas.UpdateViewSchema)
    def update(self,
               view_id: str,
               name: str,
               pipeline: List[Dict]):
        return {
            "viewId": view_id,
            "name": name,
            "pipeline": pipeline
        }

    @api_call(url="/trpc/views.remove", method="post",
              return_type=views_schemas.View, schema_class=views_schemas.RemoveViewSchema)
    def remove(self, view_id: str):
        return {
            "viewId": view_id
        }
