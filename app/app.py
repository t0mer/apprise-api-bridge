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
from starlette_exporter import PrometheusMiddleware, handle_metrics

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
   
def GetVersionFromFle():
    with open("VERSION","r") as version:
        v = version.read()
        return v


tags_metadata = [
    {
        "name": "Channels Configuration",
        "description": "Load, Save and update channels configuration",
    },
    {
        "name": "Send Notifications",
        "description": "Send notifications to selected group",
 
        },
     {
        "name": "Groups",
        "description": "Get list of available groups",
 
        },
    
]


app = FastAPI(title="Apprise API", description="Send multi channel notification using single endpoint", version=GetVersionFromFle(), contact={"name":"Tomer Klein","email":"tomer.klein@gmail.com","url":"https://github.com/t0mer/apprise-api-bridge"})
logger.info("Configuring app")
app.mount("/dist", StaticFiles(directory="dist"), name="dist")
app.mount("/js", StaticFiles(directory="dist/js"), name="js")
app.mount("/css", StaticFiles(directory="dist/css"), name="css")
templates = Jinja2Templates(directory="templates/")
app.add_middleware(PrometheusMiddleware)
app.add_route("/metrics", handle_metrics)

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/config/load", tags=["Channels Configuration"])
def get_config(request: Request):
    logger.info("Loading configuration file")
    with open('config.yaml', 'r') as config:
        return config.read()

@app.post('/api/config/save', tags=["Channels Configuration"])
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


@app.get("/")
def home(request: Request):
    logger.info("Loading default page")
    return templates.TemplateResponse('index.html', context={'request': request, 'version':GetVersionFromFle()})




@app.get("/api/groups/get", tags=["Groups"])
def get_groups(request: Request):
    logger.info("Loading configuration file")
    groups = []
    with open('config.yaml', 'r') as config:
        dictionary = yaml.load(config)
        for key, value in dictionary.items():
            groups.append(key)
    return JSONResponse(content = groups)
 


@app.post('/api/notifications/push', tags=["Send Notifications"])
def push(request: Request,group: str = Form(...),message: str = Form(...),title: str = Form(...) ):
    logger.info("Pushing notifications")
    try:
        notifires = getNotifires(group)
        apobj = apprise.Apprise()
        create_apobj(apobj,notifires)
        apobj.notify(
            body=str(message),
            title=str(title),
            )
        return JSONResponse(content = '{"message":"Configuration updated","success":"true"}')
    except Exception as e:
        error = "Aw Snap! something went wrong " + str(e)
        logger.error(error)
        return JSONResponse(content = '{"error":"'+error+'","success":"false"}')


@app.get('/api/notifications/push', tags=["Send Notifications"])
def push(request: Request,group: str="",message: str="", title: str="" ):
    logger.info("Pushing notifications")
    try:
        notifires = getNotifires(group)
        apobj = apprise.Apprise()
        create_apobj(apobj,notifires)
        apobj.notify(
            body=str(message),
            title=str(title),
            )
        return JSONResponse(content = '{"message":"Configuration updated","success":"true"}')
    except Exception as e:
        error = "Aw Snap! something went wrong " + str(e)
        logger.error(error)
        return JSONResponse(content = '{"error":"'+error+'","success":"false"}')



if __name__ == '__main__':
    uvicorn.run(app, host="0.0.0.0", port=8080)
