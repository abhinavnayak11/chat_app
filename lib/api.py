from fastapi import FastAPI, HTTPException, status
from fastapi.responses import FileResponse, RedirectResponse, HTMLResponse

app = FastAPI()

# login
@app.get('/login', response_class=HTMLResponse)
def get_login():
    FileResponse('login')

@app.post('/login', response_class=RedirectResponse)
def post_login(number: int, password: str) -> RedirectResponse:
    raise HTTPException(status.HTTP_501_NOT_IMPLEMENTED)

# sign-up
@app.get('/sign-up', response_class=HTMLResponse)
def get_sign_up():
    raise HTTPException(status.HTTP_501_NOT_IMPLEMENTED)

@app.post('/sign-up', response_class=RedirectResponse)
def post_sign_up(name: int, number: int, password: str):
    raise HTTPException(status.HTTP_501_NOT_IMPLEMENTED)

# chats
@app.get('/chats/{user_id}', response_class=HTMLResponse)
def get_chats(user_id: int):
    raise HTTPException(status.HTTP_501_NOT_IMPLEMENTED)

# contacts
@app.get('/contacts/{user_id}', response_class=HTMLResponse)
def get_contacts(user_id: int):
    raise HTTPException(status.HTTP_501_NOT_IMPLEMENTED)

# add contact
@app.get('/add-contacts/{user_id}', response_class=HTMLResponse)
def get_add_contact(user_id: int):
    raise HTTPException(status.HTTP_501_NOT_IMPLEMENTED)

@app.post('/add-contacts/{user_id}', response_class=RedirectResponse)
def get_add_contact(user_id: int, name: str, contact_number: int):
    raise HTTPException(status.HTTP_501_NOT_IMPLEMENTED)
