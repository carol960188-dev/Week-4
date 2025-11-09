
HOTELS = {
    "101": {"name": "Blue Ocean Hotel", "city": "Taipei", "stars": 4, "price": 2800},
    "102": {"name": "Mountain View Inn", "city": "Taichung", "stars": 3, "price": 1800},
    "103": {"name": "Sunshine Resort", "city": "Kaohsiung", "stars": 5, "price": 5200},
}

from fastapi import FastAPI, Request, Form
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse
from starlette.middleware.sessions import SessionMiddleware

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

app.add_middleware(SessionMiddleware, secret_key="fastapi_session_secret_2025")

@app.get("/")
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

CORRECT_EMAIL = "abc@abc.com"
CORRECT_PASSWORD = "abc"

@app.post("/login")
async def login(
    request: Request,
    email: str = Form(""),
    password: str = Form(""),
    agree: str | None = Form(None),  
):
    if not email.strip() or not password.strip():
        return RedirectResponse("/ohoh?msg=請輸入信箱和密碼", status_code=303)

    if email.strip() == CORRECT_EMAIL and password == CORRECT_PASSWORD:
        request.session["LOGGED-IN"] = True
        request.session["user"] = email.strip()
        return RedirectResponse("/member", status_code=303)

    return RedirectResponse("/ohoh?msg=信箱或密碼輸入錯誤", status_code=303)

@app.get("/member")
async def member(request: Request):
    if not request.session.get("LOGGED-IN"):
        return RedirectResponse("/", status_code=303)

    user = request.session.get("user")
    return templates.TemplateResponse("member.html", {"request": request, "user": user})

@app.get("/ohoh")
async def ohoh(request: Request):
    msg = request.query_params.get("msg", "發生未知錯誤")
    return templates.TemplateResponse("ohoh.html", {"request": request, "msg": msg})

@app.get("/logout")
async def logout(request: Request):
    
    request.session["LOGGED-IN"] = False
    request.session.pop("user", None)
    return RedirectResponse("/", status_code=303)
from fastapi import Path

@app.get("/hotel/{hotel_id}")
async def hotel_page(
    request: Request,
    hotel_id: str = Path(..., description="Hotel ID (e.g., 101)")
):
    hotel = HOTELS.get(hotel_id)
    if not hotel:
        return RedirectResponse(f"/ohoh?msg=查無此飯店（ID:{hotel_id}）", status_code=303)

    return templates.TemplateResponse(
        "hotel.html",
        {"request": request, "hotel_id": hotel_id, "hotel": hotel}
    )
