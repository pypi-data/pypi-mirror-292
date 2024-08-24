"""Galileo Observe"""

# flake8: noqa: F401
# ruff: noqa: F401

from galileo_core.helpers.dependencies import is_dependency_available
from galileo_core.helpers.group import add_users_to_group, create_group, list_groups
from galileo_core.helpers.user import invite_users, list_users
from galileo_core.schemas.core.group import (
    AddGroupMemberRequest,
    AddGroupMemberResponse,
    CreateGroupRequest,
    CreateGroupResponse,
)
from galileo_core.schemas.core.group_role import GroupRole
from galileo_core.schemas.core.group_visibility import GroupVisibility
from galileo_core.schemas.core.user import InviteUsersRequest, User
from galileo_core.schemas.core.user_role import UserRole

from galileo_observe.monitor import GalileoObserve

if is_dependency_available("langchain_core"):
    from galileo_observe.async_handlers import GalileoObserveAsyncCallback
    from galileo_observe.handlers import GalileoObserveCallback


__version__ = "1.6.1"
