import os, json, requests, uvicorn, apprise
import shutil, aiofiles
import sys, pyaml, yaml
from collections import OrderedDict
from os import environ, path
from loguru import logger
from fastapi import FastAPI, Request, File, Form, UploadFile
from fastapi.responses import UJSONResponse
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
from starlette.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.encoders import jsonable_encoder

def getNotifires(group):
    logger.info("Loading notifiers for " + group + " group")
    with open("config.yaml", 'r') as stream:
        list = yaml.safe_load(stream)[group]
        logger.info("Notifires: " + str(list))
        return list


def create_apobj(apobj, notifires):
    if len(notifires)!=0:
        logger.info("Setting notifires list") 
        jobs=notifires
        for job in jobs:
            logger.info("Adding: " + job)
            apobj.add(job)
    
    return apobj
   



app = FastAPI(title="Apprise API", description="Send multi channel notification using single endpoint", version="1.0.0")
logger.info("Configuring app")
app = FastAPI(title="Apprise API", description="Send multi channel notification using single endpoint", version="1.0.0")
app.mount("/dist", StaticFiles(directory="dist"), name="dist")
app.mount("/js", StaticFiles(directory="dist/js"), name="js")
app.mount("/css", StaticFiles(directory="dist/css"), name="css")
templates = Jinja2Templates(directory="templates/")


origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/config/load")
def get_config(request: Request):
    logger.info("Loading configuration file")
    with open('config.yaml', 'r') as config:
        return config.read()
 
@app.get("/")
def home(request: Request):
    logger.info("Loadin default page")
    return templates.TemplateResponse('index.html', context={'request': request})


@app.post('/api/config/save')
async def save_config(request: Request ):
    logger.info("Saving configuration to file")
    data = await request.json()
    try:
        with open('config.yaml', 'w') as config: 
            config.write(data['configuration'])
        return JSONResponse(content = '{"message":"Configuration updated","success":"true"}')
    except Exception as e:
        error = "Aw Snap! something went wrong " + str(e)
        logger.error(error)
        return JSONResponse(content = '{"error":"'+error+'","success":"false"}')


@app.get("/api/groups/get")
def get_groups(request: Request):
    logger.info("Loading configuration file")
    groups = []
    with open('config.yaml', 'r') as config:
        dictionary = yaml.load(config)
        for key, value in dictionary.items():
            groups.append(key)
    return JSONResponse(content = groups)
 


@app.post('/api/notifications/push')
async def push(request: Request ):
    logger.info("Pushing notifications")
    data = await request.json()
    try:
        notifires = getNotifires(data['group'])
        apobj = apprise.Apprise()
        create_apobj(apobj,notifires)
        await apobj.async_notify(
            body=str(data["message"]),
            title=str(data["title"]),
            )
        return JSONResponse(content = '{"message":"Configuration updated","success":"true"}')
    except Exception as e:
        error = "Aw Snap! something went wrong " + str(e)
        logger.error(error)
        return JSONResponse(content = '{"error":"'+error+'","success":"false"}')


if __name__ == '__main__':
    uvicorn.run(app, host="0.0.0.0", port=8080)
