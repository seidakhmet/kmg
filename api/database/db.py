import datetime as dt

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import IntegrityError
from sqlalchemy.sql import text

from .models import Base, Field, FieldData

engine = create_engine("postgresql+psycopg2://kmg:qwerty123@127.0.0.1:10001/kmg")
Session = sessionmaker(bind=engine)
session = Session()


class BadRequest(Exception):
    pass


def initialize_database():
    Base.metadata.create_all(engine)


def drop_database():
    Base.metadata.drop_all(engine)


def add_field(name: str) -> int:
    field = session.query(Field).filter(Field.name == name).first()
    if not field:
        field = Field(name=name)
        session.add(field)
        session.commit()
    return field.id


def save_field_data(instances: list, path: str, update: bool = False) -> dict:
    session.add_all(instances)
    try:
        session.commit()
    except IntegrityError:
        session.rollback()
        if not update:
            print(path, "file parsing rolled back. One or more of the rows is already exists in database.")
            return {
                "status": "Fail",
                "message": path if type(
                    path) is str else "File" + " file parsing rolled back. One or more of the rows is already exists in database."
            }
        return update_exists_rows(instances, path)
    return {"status": "Success", "message": "Success"}


def update_exists_rows(instances: list, path: str) -> dict:
    print("Argument \"-u\" or \"--update\" was set. Trying to update rows that already exists in database...")
    for instance in instances:
        row = session.query(FieldData).filter(FieldData.start_datetime == instance.start_datetime,
                                              FieldData.field_id == instance.field_id).first()
        if not row:
            row = instance
        session.add(row)
    try:
        session.commit()
    except Exception as e:
        print("Error:", e)
        print("Can't to update exist rows in the database. File:", path)
        return {"status": "Fail", "message": "Can't to update exist rows in the database"}
    return {"status": "Success", "message": "Success"}


def get_fields() -> list:
    return session.query(Field).all()


def get_field_by_id(field_id: int) -> (Field, None):
    return session.query(Field).get(field_id)


def get_positive_field_data(field_id: int, start, finish: dt.datetime) -> list:
    result = []
    with engine.begin() as conn:
        sql = text("""select *
                        from field_data t
                        where t.field_id = :field_id
                            and t.start_datetime >= to_timestamp(:start, 'YYYY-MM-DD hh24:mi:ss')::timestamp
                            and t.start_datetime <= to_timestamp(:finish, 'YYYY-MM-DD hh24:mi:ss')::timestamp"""
                   )
        data = conn.execute(sql, {"field_id": field_id, "start": start.strftime("%Y-%m-%d %H:%M:%S"),
                                  "finish": finish.strftime("%Y-%m-%d %H:%M:%S")}).mappings().all()

        for item in data:
            result.append(FieldData(**item))
    return result


def get_negative_field_data(field_id: int, start, finish: dt.datetime) -> list:
    result = []
    with engine.begin() as conn:
        sql = text("""select 
                        null                      as id,
                        start_datetime::timestamp as start_datetime,
                        0                         as value,
                        '00:00:00'::time          as duration,
                        :field_id                 as field_id
                        from generate_series(
                                     to_timestamp(:start, 'YYYY-MM-DD hh24:mi:ss')::timestamp,
                                     to_timestamp(:finish, 'YYYY-MM-DD hh24:mi:ss')::timestamp,
                                     '1 second'
                                 ) as gs(start_datetime)
                        where start_datetime not in (
                            select start_datetime
                            from field_data t
                            where t.field_id = :field_id
                                and t.start_datetime >= to_timestamp(:start, 'YYYY-MM-DD hh24:mi:ss')::timestamp
                                and t.start_datetime <= to_timestamp(:finish, 'YYYY-MM-DD hh24:mi:ss')::timestamp)"""
                   )
        data = conn.execute(sql, {"field_id": field_id, "start": start.strftime("%Y-%m-%d %H:%M:%S"),
                                  "finish": finish.strftime("%Y-%m-%d %H:%M:%S")}).mappings().all()

        for item in data:
            result.append(FieldData(**item))
    return result


def get_export_data(field_id: int, date: dt.datetime) -> dict:
    x = []
    y = []
    str_date = date.strftime("%Y-%m-%d")
    start = str_date + " 00:00:00"
    finish = str_date + " 23:59:59"
    with engine.begin() as conn:
        sql = text("""with s1 as (select 
                                    start_datetime::timestamp as start_datetime
                                  from generate_series(
                                         to_timestamp(:start, 'YYYY-MM-DD hh24:mi:ss')::timestamp,
                                         to_timestamp(:finish, 'YYYY-MM-DD hh24:mi:ss')::timestamp,
                                         '1 second'
                                       ) as gs(start_datetime))
                    select t.start_datetime,
                           coalesce(fd.value, 0.0) as value
                    from s1 as t
                             left join field_data fd ON fd.field_id = :field_id and fd.start_datetime = t.start_datetime"""
                   )
        data = conn.execute(sql, {"field_id": field_id, "start": start,
                                  "finish": finish}).mappings().all()

        for item in data:
            x.append(item.start_datetime)
            y.append(item.value)
    return {'x': x, 'y': y}
