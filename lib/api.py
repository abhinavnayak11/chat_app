from fastapi import FastAPI, HTTPException, status
from fastapi.responses import FileResponse, RedirectResponse, HTMLResponse
from fastapi.templating import Jinja2Templates

from . import db

app = FastAPI()
templates = Jinja2Templates(directory='static/html')

# login
@app.get('/login', response_class=HTMLResponse)
def get_login():                        # pass error as query parameter and use Jinja to change elements or just in URL & use javascript to 
    return templates.TemplateResponse('login.html', {'request':{}})

@app.post('/login', response_class=RedirectResponse)
def post_login(number: int, password: str) -> RedirectResponse:
    if db.is_user(number, password):
        user_id = db.get_user_id(number)
        return RedirectResponse(f'/chats/{user_id}', status_code = status.HTTP_302_FOUND)  # f strings or no f strings
    else:
        return RedirectResponse("/login?error=True", status_code=status.HTTP_302_FOUND)

# sign-up
@app.get('/sign-up', response_class=HTMLResponse)
def get_sign_up():
    return templates.TemplateResponse('sign-up.html', {'request':{}})

@app.post('/sign-up', response_class=RedirectResponse)
def post_sign_up(name: int, number: int, password: str):
    if db.is_new_user(number):
        db.insert_user(name, number, password)
        user_id = db.get_user_id(number)
        return RedirectResponse(f'/chats/{user_id}', status_code = status.HTTP_302_FOUND)
    else:
        return RedirectResponse("/sign-up?error=True", status_code= status.HTTP_302_FOUND)
    
# chats
@app.get('/chats/{user_id}', response_class=HTMLResponse)
def get_chats(user_id: int):
    return templates.TemplateResponse("chats.html", {"request": {}, "chats": db.get_chats(user_id)})

# contacts
@app.get('/contacts/{user_id}', response_class=HTMLResponse)
def get_contacts(user_id: int):
    return templates.TemplateResponse("contacts.html", {"request": {}, "contacts": db.get_contacts(user_id)})

# add contact
@app.get('/add-contacts/{user_id}', response_class=HTMLResponse)
def get_add_contact(user_id: int):
    return templates.TemplateResponse('add_contact.html', {'request':{}})

@app.post('/add-contacts/{user_id}', response_class=RedirectResponse)
def get_add_contact(user_id: int, name: str, contact_number: int):
    if (db.is_not_already_contact(user_id, contact_number)) and (not db.is_new_user(contact_number)):
        db.insert_contact(user_id, contact_number, name)
        return RedirectResponse(f'/add_contacts/{user_id}', status_code= status.HTTP_302_FOUND)
    else:
        return RedirectResponse(f'/add-contacts/{user_id}?error=True', status_code= status.HTTP_302_FOUND)
