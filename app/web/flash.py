from fastapi import Request


def flash(
    request: Request,
    message: str,
    category: str = "success",
):

    messages = request.session.get(
        "_flash_messages",
        [],
    )

    messages.append(
        {
            "message": message,
            "category": category,
        }
    )

    request.session[
        "_flash_messages"
    ] = messages


def get_flash_messages(
    request: Request,
):

    return request.session.pop(
        "_flash_messages",
        [],
    )