from enum import Enum


class HttpMethods(str, Enum):
    DELETE = "DELETE"
    GET = "GET"
    POST = "POST"
    PUT = "PUT"


class AuthType(str, Enum):
    BOT = "Bot"


class DiscordHeaders(str, Enum):
    AUDIT_LOG_REASON = "X-Audit-Log-Reason"
