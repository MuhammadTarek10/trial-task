from fastapi import FastAPI, BackgroundTasks, HTTPException, Request
from fastapi.templating import Jinja2Templates

templates = Jinja2Templates(directory="src/interface/templates")

app = FastAPI()


@app.get("/")
async def root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.post("/urls")
async def getUrls(request: Request):
    data = await request.form()
    try:
        urls = data["urls"]
    except:
        raise HTTPException(status_code=400, detail="No urls provided")
    return {"urls": urls}
