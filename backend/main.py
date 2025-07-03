
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
import fitz  # PyMuPDF
import os
import json

app = FastAPI()

# Mount the frontend directory to serve static files
app.mount("/static", StaticFiles(directory=os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "frontend"))), name="static")

PDF_PATH = "sample.pdf"
POSITION_FILE = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "position.json"))
doc = fitz.open(PDF_PATH)

def get_last_position():
    if os.path.exists(POSITION_FILE):
        try:
            with open(POSITION_FILE, "r") as f:
                data = json.load(f)
                return int(data.get("page_index", 0))
        except (json.JSONDecodeError, ValueError):
            return 0
    return 0

def save_position(page_index):
    with open(POSITION_FILE, "w") as f:
        json.dump({"page_index": page_index}, f)

@app.get("/")
async def read_root():
    return FileResponse('/home/hba/Documents/book_reader/frontend/index.html')

@app.get("/api/page/{page_number}")
async def get_page(page_number: int):
    if not (0 <= page_number < len(doc)):
        raise HTTPException(status_code=404, detail="Page not found")

    zoom = 2.0
    mat = fitz.Matrix(zoom, zoom)
    page = doc[page_number]
    pix = page.get_pixmap(matrix=mat, alpha=False)
    
    # Save to a temporary file to send
    output_path = f"/tmp/page_{page_number}.png"
    pix.save(output_path)
    
    return FileResponse(output_path, media_type="image/png")


@app.get("/api/position")
async def get_position():
    return JSONResponse(content={"page_index": get_last_position()})

@app.post("/api/position")
async def update_position(data: dict):
    try:
        page_index = int(data.get("page_index"))
        if 0 <= page_index < len(doc):
            save_position(page_index)
            return JSONResponse(content={"status": "success"})
        else:
            raise HTTPException(status_code=400, detail="Invalid page index")
    except (TypeError, ValueError):
        raise HTTPException(status_code=400, detail="Invalid data")

@app.get("/api/total_pages")
async def get_total_pages():
    return JSONResponse(content={"total_pages": len(doc)})
