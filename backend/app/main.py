import os
import shutil
import uuid
from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from app.services.rag_service import RAGPipeline
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Multimodal RAG Chatbot API")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize RAG Pipeline
# Note: In a production environment, we might want to use a singleton pattern or dependency injection
rag_pipeline = RAGPipeline()

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@app.get("/")
def read_root():
    return {"status": "ok", "message": "Multimodal RAG Chatbot API is running"}

@app.post("/chat")
async def chat(
    text_query: str = Form(None),
    image: UploadFile = File(None),
    voice: UploadFile = File(None)
):
    image_path = None
    voice_path = None
    
    try:
        if image:
            image_ext = os.path.splitext(image.filename)[1]
            image_path = os.path.join(UPLOAD_DIR, f"{uuid.uuid4()}{image_ext}")
            with open(image_path, "wb") as buffer:
                shutil.copyfileobj(image.file, buffer)
        
        if voice:
            # For voice, we might want to handle common formats like .wav, .mp3, .m4a
            voice_ext = os.path.splitext(voice.filename)[1]
            voice_path = os.path.join(UPLOAD_DIR, f"{uuid.uuid4()}{voice_ext}")
            with open(voice_path, "wb") as buffer:
                shutil.copyfileobj(voice.file, buffer)

        print("Image path passed to RAG:", image_path)
        print("Voice path passed to RAG:", voice_path)
        print("Text query:", text_query)

        result = rag_pipeline.process_query(
            text_query=text_query,
            image_path=image_path,
            voice_path=voice_path
        )
        
        return result

    except Exception as e:
        logger.error(f"Error in /chat endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        # Cleanup files after processing (optional but good for local storage)
        # In production, we might store them in S3 or clean them periodically
        if image_path and os.path.exists(image_path):
            os.remove(image_path)
        if voice_path and os.path.exists(voice_path):
            os.remove(voice_path)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)


