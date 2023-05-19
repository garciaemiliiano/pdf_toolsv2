import sys, os, os.path, pypdf, pdfreader, uuid, coloredlogs, logging, unidecode, shutil, aiofiles, aiofile, asyncio
from fastapi import FastAPI, File, UploadFile
from fastapi.responses import FileResponse
from pypdf import PdfMerger, PdfFileReader
from pdfreader import PDFDocument
from classes import _Error
from aiofile import AIOFile, LineReader, Writer

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
                # logging.warning(">>> EOF found...")
                # logging.warning(">>> EOF fixed")
                return pdf_stream_in[:actual_line]
        logging.warning(">>> EOF not found...")
    except BaseException as exception:
        logging.error("Exception occurred", exc_info=True)
        raise exception


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
        logging.error("Exception occurred", exc_info=True)
        raise exception


async def format_file_name(string: str):
    filename = (unidecode.unidecode(string)).replace(" ", "_")
    return filename


async def _count_pages(file_path: str):
    try:
        pdfFileObj = open(file_path, "rb")
        pdf = pypdf.PdfReader(pdfFileObj)
        return len(pdf.pages)
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
                p.close()
            task_reset_eof = asyncio.create_task(reset_eof_of_pdf_return_stream(txt))
            txtx = await reset_eof_of_pdf_return_stream(txt)
            async with aiofiles.open(os.path.join(root_path, f), "wb") as f:
                await f.writelines(txtx)
                f.close()
        return files
    except BaseException as exception:
        logging.error("Exception occurred", exc_info=True)
        raise exception


async def merger_append(root_path, pdf, merger):
    return merger.append(os.path.join(root_path, pdf))


async def merger_write(merger, output_merge_path):
    merger.write(output_merge_path)
    return merger.close()


async def merge_files(files: list(), root_path: str):
    """Merge files async."""
    try:
        # Inicio del merge
        logging.info(">>> Realizando merge...")
        merger = PdfMerger(strict=False)
        for pdf in files:
            task_merger = asyncio.create_task(merger_append(root_path, pdf, merger))
            await task_merger
        random_uuid = str(uuid.uuid4())
        output_merge_path = f"{os.path.join(root_path, random_uuid)}_result-merge.pdf"
        task_merger_write = asyncio.create_task(merger_write(merger, output_merge_path))
        await task_merger_write
        logging.info(">>> Successful merge ✓")
        return output_merge_path
    except BaseException as exception:
        logging.error("ErrorMerge occurred", exc_info=True)
        raise exception


async def download_files(files: list[UploadFile], root_path: str):
    try:
        logging.info(">>> Descargando pdfs...")
        arr_files = []
        for file in files:
            filename = file.filename
            # logging.info(">>> CHANGE FILENAME ACTUAL...")
            task_new_file_name = asyncio.create_task(format_file_name(filename))
            new_file_name = await task_new_file_name
            # logging.info(">>> FINISH FILENAME...")
            async with aiofile.async_open(
                os.path.join(root_path, new_file_name), "wb"
            ) as out_file:
                content = await file.read()
                await out_file.write(content)
            arr_files.append(new_file_name)
        logging.info(">>> Downloads finish ✓")
        return arr_files
    except BaseException as exception:
        logging.error("Exception occurred", exc_info=True)
        raise exception


async def _merge(files: list[UploadFile], root_path: str):
    try:
        task_download_files = asyncio.create_task(download_files(files, root_path))
        arr_files = await task_download_files
        task_fix_eof = asyncio.create_task(fix_EOF(arr_files, root_path))
        await task_fix_eof
        task_merge = asyncio.create_task(merge_files(arr_files, root_path))
        output_merge_path = await task_merge
        logging.info(">>> RETURNING...")
        return FileResponse(output_merge_path)
    except BaseException as exception:
        logging.error("Exception occurred", exc_info=True)
        raise exception
