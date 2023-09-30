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

from consts import MONGO_CONNECTION_STRING
from mongo_shortcuts_db import MongoShortcutsDB
from shortcuts_db import ShortcutsDB, StatusCodes
from url import DeleteUrl, Url

app = FastAPI()
SHORTCUTS_DB: ShortcutsDB = MongoShortcutsDB(MONGO_CONNECTION_STRING)


@app.get("/{shortcut}")
async def expand_url(request: Request, shortcut: str):
    if not SHORTCUTS_DB.check_exists(shortcut):
        return HTMLResponse(
            f"{shortcut} Not Found", status_code=HTTP_404_NOT_FOUND
        )

    return RedirectResponse(
        SHORTCUTS_DB.expand_url(shortcut, request.client.host).url,
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
async def delete_url(item: DeleteUrl = Depends()):
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
