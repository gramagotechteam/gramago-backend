import csv
import io

from fastapi.responses import (
    StreamingResponse,
)


def csv_response(
    *,
    filename: str,
    headers: list[str],
    rows: list[list],
):

    stream = io.StringIO()

    writer = csv.writer(stream)

    writer.writerow(headers)

    writer.writerows(rows)

    stream.seek(0)

    return StreamingResponse(
        iter([stream.getvalue()]),
        media_type="text/csv",
        headers={
            "Content-Disposition":
                f'attachment; filename="{filename}"'
        },
    )