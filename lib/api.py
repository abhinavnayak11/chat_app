from fastapi import FastAPI, HTTPException, status, Form
from fastapi.responses import FileResponse, RedirectResponse, HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles

from . import db

app = FastAPI(default_response_class=JSONResponse)
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory='static/html')
app.mount("/css", StaticFiles(directory="static/css"), name="css")

conn = db.get_conn(db.DB_PATH)
db.create_table(conn)

# login
@app.get('/login', response_class=HTMLResponse)
def get_login():                        # pass error as query parameter and use Jinja to change elements or just in URL & use javascript to 
    return templates.TemplateResponse('login.html', {'request':{}})

@app.post('/login', response_class=RedirectResponse)
def post_login(number: str = Form(...), password: str = Form(...)) -> RedirectResponse:
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
def post_sign_up(name:str = Form(...), number: str = Form(...), password: str = Form(...)):
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
    return templates.TemplateResponse('add-contact.html', {'request':{}, 'user_ids':[user_id]})

@app.post('/add-contacts/{user_id}', response_class=RedirectResponse)
def get_add_contact(user_id: int, name: str = Form(...), contact_number: str = Form(...)):
    if (db.is_not_already_contact(user_id, contact_number)) and (not db.is_new_user(contact_number)):
        db.insert_contact(user_id, contact_number, name)
        return RedirectResponse(f'/add-contacts/{user_id}', status_code= status.HTTP_302_FOUND)   
    else:
        return RedirectResponse(f'/add-contacts/{user_id}?error=True', status_code= status.HTTP_302_FOUND)  # how to keep form filled

# show chat messages
@app.get('/chat/{user_id}{user_contact_id}', response_class=HTMLResponse)
def get_chat_message(user_id: int, user_contact_id: int):
    messages = db.get_chat_message(user_id, user_contact_id)                                               # each message is a dict(from, to, message, timestamp)
    return templates.TemplateResponse('chat-message.html', 
                                      {'request':{}, 
                                       'user_id': user_id, 
                                       'user_contact_id': user_contact_id,
                                       'messages': messages})

# check this
@app.post('/send-message', response_class=RedirectResponse)
def post_chat_message(user_id: int, user_contact_id: int, message: str, message_timestamp: str):
    print("works")
    db.insert_chat_message(user_id, user_contact_id, message, message_timestamp)





# ALL APIS (done)
# testing for api & db (see mocking)
# all table if not exists
# sqlflaskalchemy, pydantic
# how to keep
# python web servers. 