from fastapi import FastAPI

a = FastAPI()
@a.get('/')
async def hello():
    return {'message': 'Hello meus nobres!'}
