from enum import Enum


class SecurityScopesHierarchy(Enum):
    user = 1
    moderator = 2
    administrator = 3


class SecurityScopes(str, Enum):
    USER = "user"
    MODERATOR = "moderator"
    ADMINISTRATOR = "administrator"
