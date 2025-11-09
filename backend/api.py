from fastapi import FastAPI, APIRouter
from fastapi.middleware.cors import CORSMiddleware
import psycopg2
import psycopg2.extras
from fastapi.responses import StreamingResponse
import csv
from fastapi.responses import Response
import json
import io
from datetime import date, datetime, time

app = FastAPI()

origins = [
    "http://localhost:3000",  # Your frontend URL
    "http://localhost:5500",
    "null",
    # Add other allowed origins here
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
    command += "GROUP BY    "
    command += "ci.ConcertId,   "
    command += "ci.izvodacId,   "
    command += "i.izvodacId,   "
    command += "c.ID,   "
    command += "c.Naziv "
    if filter_for == "wild" and filter_by != "":
        command +="" # TODO
    elif filter_for != "" and filter_by != "":
        command += f" WHERE {filter_by} LIKE '%{filter_for}%' "
    else:
        command += ""

    command += ";"
    cur.execute(command)
    records = cur.fetchall()
    return records

apirouter = APIRouter()

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

app.include_router(apirouter, prefix="/v2");
