import datetime as dt
from typing import Optional

from fastapi import FastAPI, UploadFile, HTTPException
from fastapi.responses import RedirectResponse

from database.db import get_fields, get_field_by_id, get_positive_field_data, get_negative_field_data, get_export_data
from main import prepare_data, parse_excel_workbook

app = FastAPI()


@app.get("/")
def read_root():
    """Редирект в SWAGGER"""
    return RedirectResponse(url='/docs')


@app.get("/fields")
def get_fields_handle():
    """Получить список месторождений"""
    return get_fields()


@app.get("/fields/{field_id}")
def get_field_by_id_handle(field_id: int):
    """Получить месторождение по идентификатору"""
    field = get_field_by_id(field_id)
    if field is None:
        raise HTTPException(404, "Field not found")
    return field


@app.get("/fields/{field_id}/data")
def get_field_data_handle(field_id: int, negative: Optional[int] = 0,
                          start_time: Optional[str] = dt.datetime(2020, 7, 1).strftime("%Y-%m-%d %H:%M:%S"),
                          finish_time: Optional[str] = dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S")):
    """Получить данные месторождения по идентификатору"""
    start = dt.datetime.strptime(start_time, "%Y-%m-%d %H:%M:%S")
    finish = dt.datetime.strptime(finish_time, "%Y-%m-%d %H:%M:%S")
    if negative > 0:
        return get_negative_field_data(field_id, start, finish)
    return get_positive_field_data(field_id, start, finish)


@app.post("/upload-file")
def upload_excel_handle(file: UploadFile, update: Optional[int] = 0):
    """Загрузить данные из Excel (xlsx) файла в базу данных"""
    field, date = prepare_data(file.filename)
    return parse_excel_workbook(file.file, field, date, update > 0)


@app.get("/export-data")
def export_data_handle(field_id: int,
                       marker_size: Optional[str] = "15",
                       marker_color: Optional[str] = "#EF5350",
                       type_name: Optional[str] = "scatter",
                       date: Optional[str] = dt.datetime.now().strftime("%Y-%m-%d")):
    """Получить данные месторождения за сутки по идентификатору и дате в заданном виде"""
    export_date = dt.datetime.strptime(date, "%Y-%m-%d")
    data = get_export_data(field_id, export_date)
    data["marker"] = {
        "size": marker_size,
        "color": marker_color
    }
    data["type"] = type_name
    return data
