# # from fastapi.templating import (
# #     Jinja2Templates,
# # )

# # from app.web.csrf import (
# #     get_csrf_token,
# # )


# # templates = Jinja2Templates(
# #     directory="app/templates"
# # )


# # templates.env.globals[
# #     "csrf_token"
# # ] = get_csrf_token



# # from app.web.flash import (
# #     get_flash_messages,
# # )


# # templates.env.globals[
# #     "get_flash_messages"
# # ] = get_flash_messages




# # from datetime import timezone
# # from zoneinfo import ZoneInfo


# # INDIA_TZ = ZoneInfo(
# #     "Asia/Kolkata"
# # )


# # def format_india_time(
# #     value,
# #     format_string=(
# #         "%d %b %Y %I:%M %p"
# #     ),
# # ):

# #     if value is None:
# #         return "—"

# #     if value.tzinfo is None:

# #         value = value.replace(
# #             tzinfo=timezone.utc
# #         )

# #     value = value.astimezone(
# #         INDIA_TZ
# #     )

# #     return value.strftime(
# #         format_string
# #     )


# # templates.env.filters[
# #     "india_time"
# # ] = format_india_time



# from datetime import timezone
# from zoneinfo import ZoneInfo

# from fastapi.templating import Jinja2Templates

# from app.web.csrf import get_csrf_token
# from app.web.flash import get_flash_messages


# templates = Jinja2Templates(
#     directory="app/templates"
# )


# # --------------------------------------------------
# # Jinja globals
# # --------------------------------------------------

# templates.env.globals["csrf_token"] = (
#     get_csrf_token
# )

# templates.env.globals["get_flash_messages"] = (
#     get_flash_messages
# )


# # --------------------------------------------------
# # India time filter
# # --------------------------------------------------

# INDIA_TZ = ZoneInfo(
#     "Asia/Kolkata"
# )


# def format_india_time(
#     value,
#     format_string="%d %b %Y %I:%M %p",
# ):

#     if value is None:
#         return "—"

#     if value.tzinfo is None:

#         value = value.replace(
#             tzinfo=timezone.utc
#         )

#     value = value.astimezone(
#         INDIA_TZ
#     )

#     return value.strftime(
#         format_string
#     )


# templates.env.filters["india_time"] = (
#     format_india_time
# )


from datetime import timezone
from zoneinfo import ZoneInfo

from fastapi.templating import Jinja2Templates

from app.web.csrf import get_csrf_token
from app.web.flash import get_flash_messages


templates = Jinja2Templates(
    directory="app/templates"
)


# --------------------------------------------------
# Jinja globals
# --------------------------------------------------

templates.env.globals["csrf_token"] = (
    get_csrf_token
)

templates.env.globals["get_flash_messages"] = (
    get_flash_messages
)


# --------------------------------------------------
# India Time Filter
# --------------------------------------------------

INDIA_TZ = ZoneInfo(
    "Asia/Kolkata"
)


def format_india_time(
    value,
    format_string="%d %b %Y %I:%M %p",
):

    if value is None:
        return "—"

    if value.tzinfo is None:
        value = value.replace(
            tzinfo=timezone.utc
        )

    value = value.astimezone(
        INDIA_TZ
    )

    return value.strftime(
        format_string
    )


templates.env.filters["india_time"] = (
    format_india_time
)