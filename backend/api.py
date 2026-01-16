from fastapi import FastAPI, APIRouter, Request, HTTPException, status, Depends
from fastapi.responses import StreamingResponse, JSONResponse, Response, RedirectResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer

from jose import jwt

from urllib.parse import urlencode

import psycopg2
import psycopg2.extras

from sqlmodel import Field, SQLModel, create_engine, Session, select, Relationship
from sqlalchemy import Column
from sqlalchemy.orm import selectinload, joinedload

from pydantic import BaseModel
from pydantic.generics import GenericModel

import httpx
import base64
import hashlib
import secrets
import csv
import json
import io

from datetime import date, datetime, time, timedelta
from pydantic import Field as PydanticField
from typing import List, Generic, TypeVar, Optional, Annotated
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

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

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
authrouter = APIRouter()

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
        content=ResponseWrapper( response=None, errors=[str(exc)] ).dict(),
        headers = exc.headers )

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

######################### OAUTH ######################### 

AUTH0_DOMAIN = "dev-jwwezawel3fx5fi3.us.auth0.com"
ALGORITHMS = ["RS256"]
AUTH0_AUTHORIZE_URL = f"https://{AUTH0_DOMAIN}/authorize"
TOKEN_URL = f"https://{AUTH0_DOMAIN}/oauth/token"
REDIRECT_URI = "http://localhost:8000/api/v1/callback"
CLIENT_ID = "2serRACHH06czdEmSKSXRRRL434ChbQe"
CLIENT_SECRET = "7FdCOntzDvJmshp-5sTsRMkNPAmspw0KQmVDq-Ka-zFbG8Ojvl2mEmjMKFXrpJyi" # if you find this on github, good for you
AUDIENCE = "https://dev-jwwezawel3fx5fi3.us.auth0.com/api/v2/"
API_AUDIENCE = "http://localhost:8000"
SCOPE = "openid profile email"

@authrouter.get("/authorize")
def get_current_user(request: Request):
    auth_header = request.headers.get("Authorization")

    if not auth_header:
        # Redirect instead of 401
        raise HTTPException(
            status_code=302,
            headers={"Location": f"https://{AUTH0_DOMAIN}/authorize"},
        )

    token = auth_header.split(" ")[1]

    try:
        payload = jwt.decode(
            token,
            key="PUBLIC_KEY_OR_JWKS",
            audience=API_AUDIENCE,
            issuer=f"https://{AUTH0_DOMAIN}/",
            algorithms=ALGORITHMS,
        )
        return payload

    except JWTError:
        raise HTTPException(
            status_code=302,
            headers={"Location": "/login"},
        )
    return 0;

def generate_pkce():
    code_verifier = secrets.token_urlsafe(64)
    challenge = hashlib.sha256(code_verifier.encode()).digest()
    code_challenge = base64.urlsafe_b64encode(challenge).rstrip(b"=").decode()
    return code_verifier, code_challenge

@authrouter.get("/login")
def login(request: Request):
    # --- CSRF protection ---
    state = secrets.token_urlsafe(32)

    # --- PKCE ---
    code_verifier, code_challenge = generate_pkce()

    # Store state + verifier in a secure cookie or server-side session
    response = RedirectResponse(
        url=f"{AUTH0_AUTHORIZE_URL}?{urlencode({
            'response_type': 'code',
            'client_id': CLIENT_ID,
            'redirect_uri': REDIRECT_URI,
            'scope': SCOPE,
            'audience': AUDIENCE,
            'state': state,
            'code_challenge': code_challenge,
            'code_challenge_method': 'S256',
        })}",
        status_code=302,
    )
    print(f" url: ");
    print(f"{AUTH0_AUTHORIZE_URL}?{urlencode({
            'response_type': 'code',
            'client_id': CLIENT_ID,
            'redirect_uri': REDIRECT_URI,
            'scope': SCOPE,
            'audience': AUDIENCE,
            'state': state,
            'code_challenge': code_challenge,
            'code_challenge_method': 'S256',
        })}");

    # --- Required security headers ---
    response.headers["Cache-Control"] = "no-store"
    response.headers["Pragma"] = "no-cache"

    # --- Store temporary auth data ---
    response.set_cookie(
        key="auth_state",
        value=state,
        httponly=True,
        secure=True,
        samesite="lax",
        max_age=300,
    )
    response.set_cookie(
        key="pkce_verifier",
        value=code_verifier,
        httponly=True,
        secure=True,
        samesite="lax",
        max_age=300,
    )

    return response



@authrouter.get("/callback")
async def callback(request: Request, code: str = None, state: str = None):
    # 6️⃣ Raw body (usually empty for GET callback)
    body = await request.body()
    print("Body:", body)

    # 1️⃣ Verify state
    saved_state = request.cookies.get("auth_state")
    if state != saved_state:
        print(f"state does not match saved state. state: {state}; saved_state: {saved_state}");
        return RedirectResponse(url="/login")  # or error page

    # 2️⃣ Get PKCE verifier
    code_verifier = request.cookies.get("pkce_verifier")
    print(request);
    # 3️⃣ Exchange code for tokens
    async with httpx.AsyncClient() as client:
        token_resp = await client.post(
            TOKEN_URL,
            data={
                "grant_type": "authorization_code",
                "client_id": CLIENT_ID,
                "client_secret": CLIENT_SECRET,  # required for Web App
                "code": code,
                "redirect_uri": REDIRECT_URI,
                "code_verifier": code_verifier,
            },
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        )
        token_data = token_resp.json()
        print(token_resp.status_code)
        print(token_resp.text)
    # 4️⃣ Save tokens in secure cookie / session
    response = RedirectResponse(url="/dashboard")
    response.set_cookie(
        key="access_token",
        value=token_data["access_token"],
        httponly=True,
        secure=True,
        samesite="lax",
    )
    response.set_cookie(
        key="id_token",
        value=token_data["id_token"],
        httponly=True,
        secure=True,
        samesite="lax",
    )

    # Optional: remove temporary cookies
    response.delete_cookie("auth_state")
    response.delete_cookie("pkce_verifier")

    return response

@restapirouter.get("/protected")
async def protected(token: Annotated[str, Depends(oauth2_scheme)]) :
    return {"token": token}; 

SECRET_KEY = "CHANGE_ME"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 15
def create_access_token(subject: str, expires_delta: timedelta | None = None):
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=15))
    payload = {
        "sub": subject,
        "exp": expire,
        "iat": datetime.utcnow(),
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

app.include_router(apirouter, prefix="/v2", include_in_schema=False);
app.include_router(restapirouter, prefix="/api/v1");
app.include_router(authrouter, prefix="/api/v1");
