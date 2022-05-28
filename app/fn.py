import sys
import os
import os.path
import PyPDF2
import pdfreader
import uuid
import unidecode
import shutil
import aiofiles
import traceback
from os import path
from fastapi import FastAPI, File, UploadFile
from fastapi.responses import FileResponse
from PyPDF2 import PdfFileMerger, PdfFileReader
from pdfreader import PDFDocument
from classes import _Error


def _formatError():
    exc_type, exc_obj, exc_tb = sys.exc_info()
    fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
    return exc_type, fname, exc_tb.tb_lineno


async def download_file(file: UploadFile, root_path: str, filename: str):
    try:
        new_file_name = await format_file_name(filename)
        async with aiofiles.open(
            os.path.join(root_path, new_file_name), "wb"
        ) as out_file:
            content = await file.read()
            await out_file.write(content)
        return new_file_name
    except BaseException as exception:
        raise exception


async def format_file_name(string: str):
    filename = (unidecode.unidecode(string)).replace(" ", "_")
    return filename


async def _count_pages(file_path: str):
    try:
        pdfFileObj = open(file_path, "rb")
        pdfReader = PyPDF2.PdfFileReader(pdfFileObj)
        return pdfReader.numPages
    except BaseException as exception:
        raise exception


async def delete_file(file_path: str):
    try:
        if os.path.isfile(file_path):
            return os.remove(file_path)
        raise Exception("error file to delete not found")
    except BaseException as exception:
        raise exception


async def _merge(files: list[UploadFile], root_path: str):
    try:
        # Descargar pdfs en el root_path
        arr_files = []
        print("Se estan descargando los pdfs...")
        for file in files:
            # print(f"Descargando...  {file.filename}")
            await download_file(file, root_path, file.filename)
            arr_files.append(await format_file_name(file.filename))
        merger = PdfFileMerger()
        # Inicio del merge
        print("Realizando merge...")
        for pdf in arr_files:
            # print(f"{os.path.join(root_path, pdf)}")
            merger.append(os.path.join(root_path, pdf))
        random_uuid = str(uuid.uuid4())
        output_merge_path = f"{os.path.join(root_path, random_uuid)}_result-merge.pdf"
        merger.write(output_merge_path)
        print("Successful merge.")
        return FileResponse(output_merge_path)
    except BaseException as exception:
        raise exception
