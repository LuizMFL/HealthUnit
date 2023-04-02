from fastapi import FastAPI, Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from datetime import datetime, timedelta
from client import pedir
app = FastAPI()

@app.post('/login')
async def login():
    HTTP
@app.get('/protected')
async def protected_route(credentials: HTTPAuthorizationCredentials = Depends(HTTPBearer())):
    print('oi')
    response = pedir(credentials.credentials)
    print('oi')
    # do something with payload, like fetch user data from database
    return response