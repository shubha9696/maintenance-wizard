"""Knowledge Router — API endpoints for document uploads, stats, and metadata list."""
import json
import pypdf
from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from backend.services.vector_store import vector_store

router = APIRouter(prefix="/api/knowledge", tags=["Knowledge"])


@router.get("/stats")
async def get_stats():
    """Get active database statistics (document count and chunk count)."""
    return vector_store.get_stats()


@router.get("/documents")
async def get_documents():
    """Get list of all ingested documents in vector database."""
    try:
        collection = vector_store._get_collection("knowledge_docs")
        results = collection.get(include=["metadatas"])
        docs = []
        seen = set()
        
        # Include initial docs if DB is clean
        default_docs = [
            {"id": "1", "name": "general_maintenance_manual.md", "type": "Manual", "chunks": 14, "date": "2026-06-08", "size": "11.2 KB"},
            {"id": "2", "name": "sop_centrifugal_pump_maintenance.md", "type": "SOP", "chunks": 6, "date": "2026-06-08", "size": "5.4 KB"},
            {"id": "3", "name": "sop_gearbox_maintenance.md", "type": "SOP", "chunks": 6, "date": "2026-06-08", "size": "3.2 KB"},
            {"id": "4", "name": "sop_motor_maintenance.md", "type": "SOP", "chunks": 6, "date": "2026-06-08", "size": "3.5 KB"},
            {"id": "5", "name": "sop_steam_turbine.md", "type": "SOP", "chunks": 10, "date": "2026-06-08", "size": "6.0 KB"},
        ]
        
        if results and results.get("metadatas"):
            for meta in results["metadatas"]:
                if meta and "source" in meta and meta["source"] not in seen:
                    seen.add(meta["source"])
                    docs.append({
                        "id": meta.get("source"),
                        "name": meta.get("source"),
                        "type": meta.get("doc_type", "Manual"),
                        "chunks": meta.get("total_chunks", 1),
                        "date": "2026-06-08",
                        "size": "Dynamic"
                    })
                    
        # Merge defaults
        for d in default_docs:
            if d["name"] not in seen:
                docs.append(d)
                
        return docs
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/upload")
async def upload_document(
    file: UploadFile = File(...),
    doc_type: str = Form("SOP")
):
    """Upload and ingest a document (PDF, TXT, MD, JSON) into RAG vector database."""
    try:
        content = ""
        filename = file.filename
        
        # Parse PDF
        if filename.endswith(".pdf"):
            pdf_reader = pypdf.PdfReader(file.file)
            text_parts = []
            for page in pdf_reader.pages:
                text_parts.append(page.extract_text() or "")
            content = "\n".join(text_parts)
            if not content.strip():
                raise ValueError("Could not extract any text from the PDF file.")
                
        # Parse text/markdown
        elif filename.endswith((".txt", ".md")):
            file_bytes = await file.read()
            content = file_bytes.decode("utf-8", errors="ignore")
            
        # Parse JSON
        elif filename.endswith(".json"):
            file_bytes = await file.read()
            json_data = json.loads(file_bytes.decode("utf-8", errors="ignore"))
            content = json.dumps(json_data, indent=2)
            
        else:
            raise ValueError("Unsupported file format. Please upload PDF, TXT, MD, or JSON files.")

        if not content.strip():
            raise ValueError("Uploaded file is empty.")

        # Ingest document into vector store
        chunks_count = vector_store.ingest_document(
            filename=filename,
            content=content,
            doc_type=doc_type
        )
        
        return {
            "status": "success",
            "filename": filename,
            "doc_type": doc_type,
            "chunks": chunks_count,
            "message": f"Successfully ingested {filename} and generated {chunks_count} vector chunks in ChromaDB."
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
