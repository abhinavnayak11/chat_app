from fastapi import FastAPI, HTTPException, status, Form, Depends
from fastapi.responses import FileResponse, RedirectResponse, HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.security import OAuth2PasswordBearer

from . import db, auth

app = FastAPI(default_response_class=JSONResponse)
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory='static/html')
app.mount("/css", StaticFiles(directory="static/css"), name="css")
app.mount("/images", StaticFiles(directory="static/images"), name="images")
app.mount("/js", StaticFiles(directory="static/js"), name="js")

conn = db.get_conn(db.DB_PATH)
db.create_table(conn)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# login
@app.get('/login', response_class=HTMLResponse)
def get_login():                        # pass error as query parameter and use Jinja to change elements or just in URL & use javascript to 
    return templates.TemplateResponse('login.html', {'request':{}})

@app.post('/login', response_class=RedirectResponse)
def post_login(number: str = Form(...), password: str = Form(...)) -> RedirectResponse:
    if db.is_user(number, password):
        return get_chat_response(number)  
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
        return get_chat_response(number)
    else:
        return RedirectResponse("/sign-up?error=True", status_code= status.HTTP_302_FOUND)

# authenticate user
@app.get('/user')
def get_user(token: str = Depends(oauth2_scheme)) -> db.User:
    user = auth.get_user_from_jwt_token(token)
    if user == db.EMPTY_USER:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user

# chats
def get_chat_response(number: str):
    user_id = int(db.get_user_id(number))
    response =  templates.TemplateResponse("chats.html", {"request": {}, "chats": db.get_chats(user_id)})
    response.set_cookie(key="number", value=auth.get_jwt_token_from_number(db.get_number(user_id)))
    return response


@app.get('/chats/{user_id}', response_class=HTMLResponse)
def get_chats(user_id: int):
    response =  templates.TemplateResponse("chats.html", {"request": {}, "chats": db.get_chats(user_id)})
    return response

# contacts
@app.get('/contacts/{user_id}', response_class=HTMLResponse)
def get_contacts(user_id: int):
    print(db.get_contacts(user_id))
    return templates.TemplateResponse("contacts.html", {"request": {}, "contacts": db.get_contacts(user_id)})

# add contact
@app.get('/add-contacts/{user_id}', response_class=HTMLResponse)
def get_add_contact(user_id: int, name: str = None):
    return templates.TemplateResponse('add-contact.html', {'request':{}})

@app.post('/add-contacts/{user_id}')
def post_add_contact(contact: db.Contact, user: db.User = Depends(get_user)):
    print(contact)
    print(user)
    if (db.is_not_already_contact(user.id, contact.contact_number)) and (not db.is_new_user(contact.contact_number)):
        db.insert_contact(user.id, contact.contact_number, contact.name)  
        return {'message':'working'} 
    else:
        return {'message':'error'}

# show chat messages
@app.get('/chat/{user_id}{user_contact_id}', response_class=HTMLResponse)
def get_chat_message(user_id: int, user_contact_id: int):
    messages = db.get_chat_message(user_id, user_contact_id)                                               # each message is a dict(from, to, message, timestamp)
    return templates.TemplateResponse('chat-message.html', 
                                      {'request':{},
                                       'messages': messages})

# check this
@app.post('/send-message')
def post_chat_message(message: db.Message, user: db.User = Depends(get_user)):
    print(message)
    db.insert_chat_message(user.id, message.user_contact_id, message.message_text, message.message_timestamp)






# ALL APIS (done)
# testing for api & db (see mocking)
# all table if not exists
# sqlflaskalchemy, pydantic
# how to keep
# python web servers. 