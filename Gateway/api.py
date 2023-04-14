from fastapi import FastAPI #Importação da FastAPI
healthunit = FastAPI()
#Instalar com 'pip install fastapi' e depois 'pip install unicorn'
#Usar 'uvicorn arquivo:nome --reload', por exemplo: 'uvicorn api:healthunit --reload"
#Necessário criar as rotas para cada caminho de link que pode ser acessa