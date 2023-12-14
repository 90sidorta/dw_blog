from uuid import UUID
from typing import Optional

from fastapi import APIRouter, Depends, status

from dw_blog.schemas.auth import AuthUser
from dw_blog.schemas.common import ErrorModel
from dw_blog.schemas.tag import TagCreate, TagRead, TagUpdate, SortTagBy, ReadTagsPagination
from dw_blog.services.tag import TagService, get_tag_service
from dw_blog.utils.auth import get_current_user
from dw_blog.schemas.common import ErrorModel, Pagination, Sort, SortOrder
from errors import RouteErrorHandler

router = APIRouter(route_class=RouteErrorHandler)