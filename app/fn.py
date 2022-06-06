import sys, os, os.path, PyPDF2, pdfreader, uuid, coloredlogs, logging, unidecode, shutil, aiofiles
from fastapi import FastAPI, File, UploadFile
from fastapi.responses import FileResponse
from PyPDF2 import PdfFileMerger, PdfFileReader
from pdfreader import PDFDocument
from classes import _Error

coloredlogs.install()

logging.basicConfig(level=logging.DEBUG)


def _formatError():
    exc_type, exc_obj, exc_tb = sys.exc_info()
    fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
    return exc_type, fname, exc_tb.tb_lineno


async def reset_eof_of_pdf_return_stream(pdf_stream_in: list):
    try:
        for i, x in enumerate(pdf_stream_in[::-1]):
            if b"%%EOF" in x:
                actual_line = len(pdf_stream_in) - i
                logging.warning(">>> EOF found...")
                break
        return pdf_stream_in[:actual_line]
    except BaseException as exception:
        logging.error("Exception occurred", exc_info=True)


async def download_file(file: UploadFile, root_path: str, filename: str):
    try:
        new_file_name = format_file_name(filename)
        async with aiofiles.open(
            os.path.join(root_path, new_file_name), "wb"
        ) as out_file:
            content = await file.read()
            await out_file.write(content)
        return new_file_name
    except BaseException as exception:
        logging.error("Exception occurred", exc_info=True)
        raise exception


def format_file_name(string: str):
    filename = (unidecode.unidecode(string)).replace(" ", "_")
    return filename


async def _count_pages(file_path: str):
    try:
        pdfFileObj = open(file_path, "rb")
        pdfReader = PyPDF2.PdfFileReader(pdfFileObj)
        return pdfReader.numPages
    except BaseException as exception:
        logging.error("Exception occurred", exc_info=True)
        raise exception


async def delete_file(file_path: str):
    try:
        if os.path.isfile(file_path):
            return os.remove(file_path)
        raise Exception("error file to delete not found")
    except BaseException as exception:
        logging.error("Exception occurred", exc_info=True)
        raise exception


async def fix_EOF(files: list, root_path: str):
    try:
        for f in files:
            async with aiofiles.open(os.path.join(root_path, f), "rb") as p:
                txt = await p.readlines()
            txtx = await reset_eof_of_pdf_return_stream(txt)
            async with aiofiles.open(os.path.join(root_path, f), "wb") as f:
                await f.writelines(txtx)
        return files
    except BaseException as exception:
        logging.error("Exception occurred", exc_info=True)
        raise exception


async def _merge(files: list[UploadFile], root_path: str):
    try:
        logging.info(">>> Descargando pdfs...")
        arr_files = []
        for file in files:
            arr_files.append(await download_file(file, root_path, file.filename))
        await fix_EOF(arr_files, root_path)
        merger = PdfFileMerger(strict=False)
        # Inicio del merge
        logging.info(">>> Realizando merge...")
        for pdf in arr_files:
            merger.append(os.path.join(root_path, pdf))
        random_uuid = str(uuid.uuid4())
        output_merge_path = f"{os.path.join(root_path, random_uuid)}_result-merge.pdf"
        merger.write(output_merge_path)
        merger.close()
        logging.info(">>> Successful merge.")
        return FileResponse(output_merge_path)
    except BaseException as exception:
        logging.error("Exception occurred", exc_info=True)
        raise exception
