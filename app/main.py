import uvicorn
import fastapi
import traceback
import sys, os
from fastapi import FastAPI, File, UploadFile, APIRouter, status, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from tags_docs import tags_metadata
from classes import _Error
from settings import settings
from fn import download_file, delete_file, _merge, _count_pages, _formatError


app = FastAPI(openapi_tags=tags_metadata)
app.mount("/tmp", StaticFiles(directory="/tmp"), name="temp")


@app.post("/count_pages/", status_code=status.HTTP_200_OK, tags=["count_pages"])
async def count_pages(file: UploadFile):
    root_path = settings.upload_folder
    filename = file.filename
    file_content = file.file
    if file_content:
        try:
            filename = await download_file(file, root_path, filename)
            pages = await _count_pages(os.path.join(root_path, filename))
            await delete_file(os.path.join(root_path, filename))
            return {"nombre_archivo": filename, "cantidad_paginas": pages}
        except BaseException as exception:
            error_type, file_error, line_error = _formatError()
            error = _Error(exception, error_type, file_error, line_error)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=error.returnError(),
            ) from exception
    else:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="error_file_missing",
        )


@app.post("/merge_files/", status_code=status.HTTP_201_CREATED, tags=["merge"])
async def merge(files: list[UploadFile]):
    try:
        root_path = settings.upload_folder
        if len(files):
            return await _merge(files, root_path)
        else:
            raise Exception("error_missing_file")
    except BaseException as exception:
        error_type, file_error, line_error = _formatError()
        error = _Error(exception, error_type, file_error, line_error)
        print(error.returnError())
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=error.returnError(),
        ) from exception


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
