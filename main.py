import datetime

from fastapi import Depends, FastAPI
from starlette.requests import Request
from starlette.responses import HTMLResponse, RedirectResponse
from starlette.status import (
    HTTP_201_CREATED,
    HTTP_204_NO_CONTENT,
    HTTP_303_SEE_OTHER,
    HTTP_403_FORBIDDEN,
    HTTP_404_NOT_FOUND,
    HTTP_409_CONFLICT,
)
from uvicorn import run

from unlink.consts import MONGO_CONNECTION_STRING
from unlink.mongo_shortcuts_db import MongoShortcutsDB
from unlink.shortcuts_db import ShortcutsDB, StatusCodes
from unlink.url import PartialUrl, Url

app = FastAPI()
SHORTCUTS_DB: ShortcutsDB = MongoShortcutsDB(MONGO_CONNECTION_STRING)


@app.get("/")
async def stats_url(item: PartialUrl = Depends()):
    expanded_response = SHORTCUTS_DB.get_url_stats(item)

    if expanded_response == StatusCodes.NOT_EXIST:
        return HTMLResponse(
            f"{item.shortcut} Not Found", status_code=HTTP_404_NOT_FOUND
        )

    if expanded_response == StatusCodes.WRONG_OWNER:
        return HTMLResponse(f"Wrong owner", status_code=HTTP_403_FORBIDDEN)

    formated_visitors = [
        (str(ip), time.isoformat()) for ip, time in expanded_response.visitors
    ]

    return HTMLResponse(f"{formated_visitors}")


@app.get("/{shortcut}")
async def expand_url(request: Request, shortcut: str):
    expanded_response = SHORTCUTS_DB.expand_url(shortcut)

    if not expanded_response:
        return HTMLResponse(
            f"{shortcut} Not Found", status_code=HTTP_404_NOT_FOUND
        )

    SHORTCUTS_DB.log_entry(shortcut, request.client.host)
    return RedirectResponse(
        expanded_response.url,
        status_code=HTTP_303_SEE_OTHER,
    )


@app.post("/create")
async def create_url(item: Url = Depends()):
    create_response = SHORTCUTS_DB.create(item)

    if create_response == StatusCodes.NOT_EXIST:
        return HTMLResponse(
            "Shortcut already exists!", status_code=HTTP_409_CONFLICT
        )

    return HTMLResponse("", status_code=HTTP_201_CREATED)


@app.put("/update")
async def update_url(item: Url = Depends()):
    update_response = SHORTCUTS_DB.update(item)

    if update_response == StatusCodes.NOT_EXIST:
        return HTMLResponse(
            f"{item.shortcut} Not Found", status_code=HTTP_404_NOT_FOUND
        )

    if update_response == StatusCodes.WRONG_OWNER:
        return HTMLResponse(f"Wrong owner", status_code=HTTP_403_FORBIDDEN)

    return HTMLResponse(status_code=HTTP_204_NO_CONTENT)


@app.delete("/delete")
async def delete_url(item: PartialUrl = Depends()):
    delete_response = SHORTCUTS_DB.delete(item)

    if delete_response == StatusCodes.NOT_EXIST:
        return HTMLResponse(
            f"{item.shortcut} Not Found", status_code=HTTP_404_NOT_FOUND
        )

    if delete_response == StatusCodes.WRONG_OWNER:
        return HTMLResponse(f"Wrong owner", status_code=HTTP_403_FORBIDDEN)

    return HTMLResponse(status_code=HTTP_204_NO_CONTENT)


if __name__ == "__main__":
    run(app="main:app", host="0.0.0.0", port=80, reload=True)
