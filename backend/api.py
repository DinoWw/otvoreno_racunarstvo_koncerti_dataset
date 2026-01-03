from fastapi import FastAPI, APIRouter, Request, HTTPException, status
from fastapi.responses import StreamingResponse, JSONResponse, Response
from fastapi.middleware.cors import CORSMiddleware

import psycopg2
import psycopg2.extras

from sqlmodel import Field, SQLModel, create_engine, Session, select, Relationship
from sqlalchemy import Column
from sqlalchemy.orm import selectinload, joinedload

from pydantic import BaseModel
from pydantic.generics import GenericModel

import csv
import json
import io

from datetime import date, datetime, time
from pydantic import Field as PydanticField
from typing import List, Generic, TypeVar, Optional

app = FastAPI(
    contact= {
        "name": "Dino Plečko",
        "email": "dino.plecko@fer.hr",
    },
    license_info= {
        "name": "CC BY-SA 4.0",
        "info": "https://creativecommons.org/licenses/by-sa/4.0/"
    }
)

origins = [
    "http://localhost:3000",
    "http://localhost:5500",
    "null",
]

app.add_middleware(CORSMiddleware, 
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],         # Allow all HTTP methods
    allow_headers=["*"],         # Allow all headers
                   )


conn = psycopg2.connect(
    dbname='koncert',
    user='postgres',
    password='1234', #TODO put in env
    host='localhost',
    port=5432
)
conn.autocommit = True
cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)



def json_default(obj):
    if isinstance(obj, (date, datetime)):
        return obj.isoformat()
    elif isinstance(obj, time):
        return obj.strftime("%H:%M:%S")
    raise TypeError(f"Type {type(obj)} not serializable")

def sanitize(input: str) :
    return psycopg2.extensions.adapt(input).getquoted()


def raw_koncert(filter_by: str = "", filter_for: str = ""):
    #wild = sanitize(wild);
    #zanr = sanitize(zanr);
    #naziv = sanitize(naziv);
    command = f"SELECT * FROM Concerts c"
    command += " JOIN Concert_Izvodaci ci ON c.ID = ci.ConcertID "
    command += "JOIN Izvodaci i "
    command += "on i.izvodacId = ci.IzvodacID "
    if filter_for != "" and filter_by == "wild":
        columns = ["naziv", "datum", "vrijeme", "lokacija", 
                   "unutarnjivanjski", "glazbenagrupa", "zanr", "trajanjemin"]
        conditions = " OR ".join([f"c.{col}::text LIKE '%{filter_for}%'" for col in columns])
        command += f" WHERE ({conditions}) "
    elif filter_for != "" and filter_by != "":
        command += f" WHERE {filter_by} LIKE '%{filter_for}%' "
    else:
        command += ""
    command += "GROUP BY    "
    command += "ci.ConcertId,   "
    command += "ci.izvodacId,   "
    command += "i.izvodacId,   "
    command += "c.ID,   "
    command += "c.Naziv "

    command += ";"
    cur.execute(command)
    records = cur.fetchall()
    return records

apirouter = APIRouter()
restapirouter = APIRouter()

@apirouter.get("/koncert")
async def koncert(draw:int = 0, filter_by: str = "", filter_for: str = ""):
    records = raw_koncert(filter_by, filter_for)
    res = {
            "draw":draw,
            "recordsTotal":len(records),
            "recordsFiltered":len(records),
            "data": records,
            }
    return res;

@apirouter.get("/koncert_json")
async def koncert_json(filter_by: str = "", filter_for: str = ""):
    data = raw_koncert(filter_by, filter_for)
    json_content = json.dumps(data, default=json_default, ensure_ascii=False, indent=2)
    
    headers = {
        "Content-Disposition": "attachment; filename=export.json"
    }
    
    return Response(content=json_content, media_type="application/json", headers=headers)

@apirouter.get("/koncert_csv")
async def koncert_csv(filter_by: str = "", filter_for: str = ""):
    data = raw_koncert(filter_by, filter_for);

    fieldnames = list(data[0].keys())

    output = io.StringIO()
    writer = csv.DictWriter(output, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(data)
    output.seek(0)  # Reset cursor to start of stream

    headers = {
        "Content-Disposition": "attachment; filename=export.csv"
    }

    return StreamingResponse(output, media_type="text/csv", headers=headers)

## REST API

# dialect+driver://username:password@host:port/database
eng = create_engine("postgresql://postgres:1234@localhost:5432/koncert");

class ConcertPerformerLink(SQLModel, table=True):
    __tablename__ = "concert_izvodaci"

    concertid: int | None = Field(
        default=None,
        foreign_key="concerts.id",
        primary_key=True
    )
    izvodacid: int | None = Field(
        default=None,
        foreign_key="izvodaci.izvodacid",
        primary_key=True
    )

class Concert(SQLModel, table=True):
    __tablename__ = "concerts"

    id: int | None = Field(default=None, primary_key=True)
    naziv: str
    datum: date
    vrijeme: time
    lokacija: str
    unutarnjivanjski: str
    glazbenagrupa: str
    zanr: str
    trajanjemin: int

    izvodaci: List["Performer"] = Relationship(
        back_populates="koncerti",
        link_model=ConcertPerformerLink
    )

class ConcertCreate(SQLModel):
    naziv: str
    datum: date
    vrijeme: time
    lokacija: str
    unutarnjivanjski: str
    glazbenagrupa: str
    zanr: str
    trajanjemin: int

class ConcertUnlinkedOutput(SQLModel):
    id: int | None = Field(default=None, primary_key=True)
    naziv: str
    datum: date
    vrijeme: time
    lokacija: str
    unutarnjivanjski: str
    glazbenagrupa: str
    zanr: str
    trajanjemin: int

class ConcertOutput(SQLModel):
    id: int | None = Field(default=None, primary_key=True)
    naziv: str
    datum: date
    vrijeme: time
    lokacija: str
    unutarnjivanjski: str
    glazbenagrupa: str
    zanr: str
    trajanjemin: int
    izvodaci: List["Performer"]

class Performer(SQLModel, table=True):
    __tablename__ = "izvodaci"

    izvodacid: int | None = Field(default=None, primary_key=True)
    ime: str
    prezime: str

    koncerti: List["Concert"] = Relationship(
        back_populates="izvodaci",
        link_model = ConcertPerformerLink
    )

class PerformerUnlinkedOutput(SQLModel):
    izvodacid: int | None = Field(default=None, primary_key=True)
    ime: str
    prezime: str

class PerformerOutput(SQLModel):
    izvodacid: int | None = Field(default=None, primary_key=True)
    ime: str
    prezime: str
    koncerti: List["Concert"]

DataT = TypeVar("DataT")

class ResponseWrapper(GenericModel, Generic[DataT]):
    response: Optional[DataT]
    errors: List[str] = []

ERROR_RESPONSES = {
    404: {"model": ResponseWrapper[None], "description": "Not found"},
    422: {"model": ResponseWrapper[None], "description": "Validation error"},
    500: {"model": ResponseWrapper[None], "description": "Server error"},
}

def wrap(obj):
    return ResponseWrapper(response=obj)

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content=ResponseWrapper(response=None, errors=["Internal server error"]).dict()
    )

@app.exception_handler(HTTPException)
async def http_exception_handler(
    request: Request,
    exc: HTTPException,
):
    return JSONResponse(
        status_code=exc.status_code,
        content=ResponseWrapper( response=None, errors=[str(exc)] ).dict())

@restapirouter.get("/performers", response_model=ResponseWrapper[List[PerformerOutput]], responses = ERROR_RESPONSES)
async def rest_performers_all():
    with Session(eng) as session:
        statement = select(Performer).options(joinedload(Performer.koncerti))
        performers = session.exec(statement).unique().all()
        return ResponseWrapper(response=performers)


@restapirouter.get("/performers/{pid}", response_model=ResponseWrapper[PerformerOutput], responses = ERROR_RESPONSES)
async def rest_performers_all(pid):
    with Session(eng) as session:
        statement = select(Performer).where(Performer.izvodacid == pid).options(joinedload(Performer.koncerti))
        performer = session.exec(statement).unique().one_or_none()
        return ResponseWrapper(response=performer)

@restapirouter.get("/concerts", response_model=ResponseWrapper[List[ConcertOutput]], responses = ERROR_RESPONSES)
async def rest_concerts_all():
    with Session(eng) as session:
        statement = select(Concert).options(joinedload(Concert.izvodaci));
        concerts = session.exec(statement).unique().all()
        return ResponseWrapper(response=concerts)

@restapirouter.get("/concerts/{cid}", response_model=ResponseWrapper[ConcertOutput], responses = ERROR_RESPONSES)
async def rest_concert_by_id(cid: int):
    with Session(eng) as session:
        statement = select(Concert).where(Concert.id == cid).options(joinedload(Concert.izvodaci))

        concert = session.exec(statement).unique().one_or_none()
        if(concert is None) :
            raise HTTPException(status_code=404, detail="Not found")
        return ResponseWrapper(response=concert)

@restapirouter.post("/concerts", response_model=ResponseWrapper[ConcertUnlinkedOutput], 
    status_code=status.HTTP_201_CREATED, responses = ERROR_RESPONSES)
async def rest_concert_add(concert: ConcertCreate):
    # validate concert
    if(concert.unutarnjivanjski != "unutarnji" and concert.unutarnjivanjski != "vanjski"):
        raise HTTPException(status_code=400, detail="field unutarnjivanjski must be either 'unutarnji' or 'vanjski'")

    with Session(eng) as session:
        db_concert = Concert(**concert.dict())
        session.add(db_concert)
        session.commit()
        session.refresh(db_concert)
        return wrap(db_concert)

@restapirouter.delete(
    "/concerts/{cid}",
    response_model=ResponseWrapper[ConcertOutput],
    responses=ERROR_RESPONSES,
    status_code=200,
)
async def delete_concert(cid: int):
    with Session(eng) as session:
        concert = session.get(Concert, cid)
        if concert is None:
            raise HTTPException(status_code=404, detail="Not found")
        
        session.delete(concert)
        session.commit()

        return wrap(concert)


@restapirouter.put(
    "/concerts/{cid}",
    response_model=ResponseWrapper[ConcertUnlinkedOutput],
    responses=ERROR_RESPONSES,
)
async def update_concert(cid: int, concert_update: ConcertCreate):
    with Session(eng) as session:
        concert = session.get(Concert, cid)
        if concert is None:
            raise HTTPException(status_code=404, detail="Not found")
        
        for key, value in concert_update.dict(exclude_unset=True).items():
            setattr(concert, key, value)
        
        session.add(concert)
        session.commit()
        session.refresh(concert)

        return wrap(concert)

@restapirouter.get(
    "/concerts/{cid}/izvodaci",
    response_model=ResponseWrapper[List[PerformerUnlinkedOutput]],
    responses=ERROR_RESPONSES,
)
async def list_performers_in_concert(cid: int):
    with Session(eng) as session:
        statement = select(Concert).where(Concert.id == cid).options(joinedload(Concert.izvodaci))
        concert = session.exec(statement).unique().one_or_none()
        
        if concert is None:
            raise HTTPException(status_code=404, detail="Concert not found")
        
        return wrap(concert.izvodaci)

@restapirouter.get("/openapi.json")
async def openapi_json():
    return app.openapi()

app.include_router(apirouter, prefix="/v2", include_in_schema=False);
app.include_router(restapirouter, prefix="/api/v1");
