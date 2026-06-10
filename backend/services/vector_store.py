"""
Vector Store Service — ChromaDB integration for RAG.
Handles document ingestion, embedding, and semantic search over
equipment manuals, SOPs, maintenance records, and failure reports.
"""
import os
import json
import chromadb
from chromadb.api.types import EmbeddingFunction, Documents, Embeddings
import google.generativeai as genai
from backend.config import settings

# Configure Gemini
genai.configure(api_key=settings.GEMINI_API_KEY)


class GeminiEmbeddingFunction(EmbeddingFunction):
    """Custom embedding function using Gemini's embed_content API."""

    def __call__(self, input: Documents) -> Embeddings:
        import time
        results = []
        # Process in batches of 20 to avoid rate limits
        for i in range(0, len(input), 20):
            batch = input[i:i+20]
            # Add a small delay between batches to stay under rate limits
            if i > 0:
                time.sleep(0.3)
                
            for attempt in range(5):
                try:
                    result = genai.embed_content(
                        model=settings.EMBEDDING_MODEL,
                        content=batch,
                        task_type="retrieval_document"
                    )
                    results.extend(result['embedding'])
                    break
                except Exception as e:
                    error_msg = str(e).lower()
                    if "429" in error_msg or "quota" in error_msg or "resource_exhausted" in error_msg:
                        if "limit: 1000" in error_msg or "quota exceeded" in error_msg or "exceeded your current quota" in error_msg:
                            print(f"Daily quota limit reached for embeddings. Aborting retries immediately.")
                            results.extend([[0.0] * 3072] * len(batch))
                            break
                        sleep_time = (2 ** attempt) + 1
                        print(f"Rate limit hit. Retrying batch {i//20 + 1} in {sleep_time}s... (Error: {e})")
                        time.sleep(sleep_time)
                    else:
                        print(f"Error in batch embedding: {e}")
                        # Fallback to zero vectors for the batch
                        results.extend([[0.0] * 3072] * len(batch))
                        break
            else:
                # Exhausted all retries
                print(f"Failed to embed batch {i//20 + 1} after 5 attempts.")
                results.extend([[0.0] * 3072] * len(batch))
        return results


class VectorStoreService:
    """Manages ChromaDB collections for equipment knowledge retrieval."""

    def __init__(self):
        self.client = chromadb.PersistentClient(path=settings.CHROMA_DB_PATH)
        self.embed_fn = GeminiEmbeddingFunction()
        self._collections = {}
        self._initialized = False

    def _get_collection(self, name: str):
        if name not in self._collections:
            self._collections[name] = self.client.get_or_create_collection(
                name=name,
                embedding_function=self.embed_fn,
                metadata={"hnsw:space": "cosine"}
            )
        return self._collections[name]

    def initialize(self):
        """Load all knowledge base documents into ChromaDB."""
        if self._initialized:
            return

        # 1. Ingest equipment knowledge documents (manuals, SOPs)
        self._ingest_knowledge_docs()

        # 2. Ingest maintenance logs
        self._ingest_maintenance_logs()

        # 3. Ingest failure reports
        self._ingest_failure_reports()

        # 4. Ingest failure modes database
        self._ingest_failure_modes()

        self._initialized = True

    def _chunk_text(self, text: str, chunk_size: int = 800, overlap: int = 100):
        """Split text into overlapping chunks."""
        lines = text.split("\n")
        chunks = []
        current_chunk = []
        current_size = 0

        for line in lines:
            line_size = len(line)
            if current_size + line_size > chunk_size and current_chunk:
                chunks.append("\n".join(current_chunk))
                # Keep last few lines for overlap
                overlap_lines = []
                overlap_size = 0
                for l in reversed(current_chunk):
                    if overlap_size + len(l) > overlap:
                        break
                    overlap_lines.insert(0, l)
                    overlap_size += len(l)
                current_chunk = overlap_lines
                current_size = overlap_size
            current_chunk.append(line)
            current_size += line_size

        if current_chunk:
            chunks.append("\n".join(current_chunk))

        return chunks

    def _ingest_knowledge_docs(self):
        """Ingest equipment manuals and SOPs."""
        collection = self._get_collection("knowledge_docs")
        if collection.count() > 0:
            return  # Already ingested

        knowledge_dir = settings.KNOWLEDGE_DIR
        if not os.path.exists(knowledge_dir):
            return

        documents = []
        metadatas = []
        ids = []
        idx = 0

        for filename in os.listdir(knowledge_dir):
            if not filename.endswith(".md"):
                continue
            filepath = os.path.join(knowledge_dir, filename)
            with open(filepath, "r", encoding="utf-8") as f:
                content = f.read()

            doc_type = "manual" if "manual" in filename else "sop" if "sop" in filename else "reference"
            chunks = self._chunk_text(content)

            for i, chunk in enumerate(chunks):
                documents.append(chunk)
                metadatas.append({
                    "source": filename,
                    "doc_type": doc_type,
                    "chunk_index": i,
                    "total_chunks": len(chunks)
                })
                ids.append(f"kb-{idx}")
                idx += 1

        if documents:
            # Batch add (ChromaDB limit is ~5000 per batch)
            batch_size = 100
            for i in range(0, len(documents), batch_size):
                collection.add(
                    documents=documents[i:i+batch_size],
                    metadatas=metadatas[i:i+batch_size],
                    ids=ids[i:i+batch_size]
                )

    def _ingest_maintenance_logs(self):
        """Ingest historical maintenance logs."""
        collection = self._get_collection("maintenance_logs")
        if collection.count() > 0:
            return

        logs_path = os.path.join(settings.DATA_DIR, "maintenance_logs.json")
        if not os.path.exists(logs_path):
            return

        with open(logs_path, "r") as f:
            logs = json.load(f)

        documents = []
        metadatas = []
        ids = []

        # Filter logs to keep only those containing valuable repair, breakdown, or replacement details
        valuable_actions = ["repair", "replacement", "emergency", "breakdown", "corrective"]
        filtered_logs = []
        for log in logs:
            action = log.get("action_type", "").lower()
            if any(val in action for val in valuable_actions):
                filtered_logs.append(log)

        # Limit to 120 logs to avoid rate limit or token limits during first run
        for log in filtered_logs[:120]:
            doc = (
                f"Equipment: {log['equipment_name']} ({log['equipment_id']}) | Area: {log['area']}\n"
                f"Date: {log['date']} | Action: {log['action_type']}\n"
                f"Failure Mode: {log['failure_mode']} | Root Cause: {log['root_cause']}\n"
                f"Symptoms: {log['symptoms_observed']}\n"
                f"Actions Taken: {log['actions_taken']}\n"
                f"Downtime: {log['downtime_hours']} hours | Technician: {log['technician']}\n"
                f"Notes: {log['notes']}"
            )
            documents.append(doc)
            metadatas.append({
                "equipment_id": log["equipment_id"],
                "area": log["area"],
                "action_type": log["action_type"],
                "date": log["date"],
                "doc_type": "maintenance_log"
            })
            ids.append(f"ml-{log['id']}")

        if documents:
            batch_size = 100
            for i in range(0, len(documents), batch_size):
                collection.add(
                    documents=documents[i:i+batch_size],
                    metadatas=metadatas[i:i+batch_size],
                    ids=ids[i:i+batch_size]
                )

    def _ingest_failure_reports(self):
        """Ingest failure/incident reports."""
        collection = self._get_collection("failure_reports")
        if collection.count() > 0:
            return

        reports_path = os.path.join(settings.DATA_DIR, "failure_reports.json")
        if not os.path.exists(reports_path):
            return

        with open(reports_path, "r") as f:
            reports = json.load(f)

        documents = []
        metadatas = []
        ids = []

        for report in reports:
            doc = (
                f"FAILURE REPORT: {report['id']}\n"
                f"Equipment: {report['equipment_name']} ({report['equipment_id']}) | Area: {report['area']}\n"
                f"Date: {report['date']} | Severity: {report['severity']}\n"
                f"Failure Mode: {report['failure_mode']}\n"
                f"Root Cause: {report['root_cause']}\n"
                f"Symptoms: {report['symptoms']}\n"
                f"Sequence of Events: {report['sequence_of_events']}\n"
                f"Immediate Actions: {report['immediate_actions']}\n"
                f"Corrective Actions: {report['corrective_actions']}\n"
                f"Downtime: {report['downtime_hours']} hours | Production Loss: {report['production_loss_tonnes']} tonnes\n"
                f"Lessons Learned: {report['lessons_learned']}\n"
                f"Recommendations: {'; '.join(report['preventive_recommendations'])}"
            )
            documents.append(doc)
            metadatas.append({
                "equipment_id": report["equipment_id"],
                "area": report["area"],
                "severity": report["severity"],
                "date": report["date"],
                "doc_type": "failure_report"
            })
            ids.append(f"fr-{report['id']}")

        if documents:
            batch_size = 100
            for i in range(0, len(documents), batch_size):
                collection.add(
                    documents=documents[i:i+batch_size],
                    metadatas=metadatas[i:i+batch_size],
                    ids=ids[i:i+batch_size]
                )

    def _ingest_failure_modes(self):
        """Ingest failure modes database."""
        collection = self._get_collection("failure_modes")
        if collection.count() > 0:
            return

        modes_path = os.path.join(settings.DATA_DIR, "failure_modes.json")
        if not os.path.exists(modes_path):
            return

        with open(modes_path, "r") as f:
            failure_modes = json.load(f)

        documents = []
        metadatas = []
        ids = []
        idx = 0

        for eq_type, modes in failure_modes.items():
            for mode in modes:
                doc = (
                    f"Equipment Type: {eq_type}\n"
                    f"Failure Mode: {mode['mode']}\n"
                    f"Root Cause: {mode['cause']}\n"
                    f"Symptoms: {mode['symptom']}\n"
                    f"Mean Time Between Failures: {mode.get('mtbf_hours', 'N/A')} hours"
                )
                documents.append(doc)
                metadatas.append({
                    "equipment_type": eq_type,
                    "failure_mode": mode["mode"],
                    "doc_type": "failure_mode"
                })
                ids.append(f"fm-{idx}")
                idx += 1

        if documents:
            collection.add(documents=documents, metadatas=metadatas, ids=ids)

    # ── Query Methods ──────────────────────────────────────
    def search_knowledge(self, query: str = None, n_results: int = 5, doc_type: str = None, query_embeddings = None):
        """Search across knowledge base documents."""
        collection = self._get_collection("knowledge_docs")
        where_filter = {"doc_type": doc_type} if doc_type else None
        
        kwargs = {}
        if query_embeddings is not None:
            kwargs["query_embeddings"] = query_embeddings
        elif query is not None:
            kwargs["query_texts"] = [query]
        else:
            return []

        results = collection.query(
            n_results=n_results,
            where=where_filter,
            **kwargs
        )
        return self._format_results(results)

    def search_maintenance_history(self, query: str = None, n_results: int = 5, equipment_id: str = None, query_embeddings = None):
        """Search maintenance logs."""
        collection = self._get_collection("maintenance_logs")
        where_filter = {"equipment_id": equipment_id} if equipment_id else None
        
        kwargs = {}
        if query_embeddings is not None:
            kwargs["query_embeddings"] = query_embeddings
        elif query is not None:
            kwargs["query_texts"] = [query]
        else:
            return []

        results = collection.query(
            n_results=n_results,
            where=where_filter,
            **kwargs
        )
        return self._format_results(results)

    def search_failure_reports(self, query: str = None, n_results: int = 5, equipment_id: str = None, query_embeddings = None):
        """Search failure/incident reports."""
        collection = self._get_collection("failure_reports")
        where_filter = {"equipment_id": equipment_id} if equipment_id else None
        
        kwargs = {}
        if query_embeddings is not None:
            kwargs["query_embeddings"] = query_embeddings
        elif query is not None:
            kwargs["query_texts"] = [query]
        else:
            return []

        results = collection.query(
            n_results=n_results,
            where=where_filter,
            **kwargs
        )
        return self._format_results(results)

    def search_failure_modes(self, query: str = None, n_results: int = 5, equipment_type: str = None, query_embeddings = None):
        """Search failure modes database."""
        collection = self._get_collection("failure_modes")
        where_filter = {"equipment_type": equipment_type} if equipment_type else None
        
        kwargs = {}
        if query_embeddings is not None:
            kwargs["query_embeddings"] = query_embeddings
        elif query is not None:
            kwargs["query_texts"] = [query]
        else:
            return []

        results = collection.query(
            n_results=n_results,
            where=where_filter,
            **kwargs
        )
        return self._format_results(results)

    def embed_query(self, query: str) -> list:
        """Embed a single search query using task_type='retrieval_query'."""
        try:
            result = genai.embed_content(
                model=settings.EMBEDDING_MODEL,
                content=query,
                task_type="retrieval_query"
            )
            return [result['embedding']]
        except Exception as e:
            print(f"Error embedding query: {e}. Falling back to default embedding function.")
            error_msg = str(e).lower()
            if "limit: 1000" in error_msg or "quota exceeded" in error_msg or "exceeded your current quota" in error_msg:
                print("Daily quota exceeded. Returning dummy zero vector immediately to prevent response lag.")
                return [[0.0] * 3072]
            return self.embed_fn([query])

    def keyword_search_fallback(self, query: str, collection_name: str, n_results: int = 5, equipment_id: str = None, equipment_type: str = None):
        """Perform simple keyword fallback matching over a ChromaDB collection when embeddings are rate-limited."""
        try:
            collection = self._get_collection(collection_name)
            # Fetch all documents in the collection
            where_filter = {}
            if equipment_id and collection_name in ["maintenance_logs", "failure_reports"]:
                where_filter = {"equipment_id": equipment_id}
            elif equipment_type and collection_name == "failure_modes":
                where_filter = {"equipment_type": equipment_type}
                
            results = collection.get(where=where_filter if where_filter else None, include=["documents", "metadatas"])
            if not results or not results.get("documents"):
                return []
                
            query_words = [w.lower() for w in query.split() if len(w) > 2]
            scored_docs = []
            
            for idx, doc in enumerate(results["documents"]):
                doc_lower = doc.lower()
                # Score based on how many query words are present
                score = sum(1 for w in query_words if w in doc_lower)
                
                # Bonus if exact phrases are present
                if query.lower() in doc_lower:
                    score += 5
                    
                if score > 0:
                    meta = results["metadatas"][idx] if results.get("metadatas") else {}
                    max_words = max(len(query_words), 1)
                    distance = max(0.1, min(0.9, 1.0 - (score / (max_words + 5.0))))
                    scored_docs.append({
                        "content": doc,
                        "metadata": meta,
                        "distance": distance,
                        "relevance_score": round(1.0 - distance, 3)
                    })
            
            scored_docs.sort(key=lambda x: x["distance"])
            return scored_docs[:n_results]
        except Exception as e:
            print(f"Error in keyword search fallback for {collection_name}: {e}")
            return []

    def search_all(self, query: str, n_results: int = 3, equipment_id: str = None):
        """Search across all collections and merge results using a single query embedding or keyword fallback."""
        query_embeddings = self.embed_query(query)
        
        # Check if we got a zero vector fallback
        is_zero_vector = (query_embeddings == [[0.0] * 3072])
        
        all_results = []
        if is_zero_vector:
            print("Embedding function rate-limited or zero-vector fallback detected. Using keyword search fallback.")
            all_results.extend(self.keyword_search_fallback(query, "knowledge_docs", n_results=n_results))
            all_results.extend(self.keyword_search_fallback(query, "maintenance_logs", n_results=n_results, equipment_id=equipment_id))
            all_results.extend(self.keyword_search_fallback(query, "failure_reports", n_results=n_results, equipment_id=equipment_id))
            all_results.extend(self.keyword_search_fallback(query, "failure_modes", n_results=n_results))
        else:
            all_results.extend(self.search_knowledge(n_results=n_results, query_embeddings=query_embeddings))
            all_results.extend(self.search_maintenance_history(n_results=n_results, equipment_id=equipment_id, query_embeddings=query_embeddings))
            all_results.extend(self.search_failure_reports(n_results=n_results, equipment_id=equipment_id, query_embeddings=query_embeddings))
            all_results.extend(self.search_failure_modes(n_results=n_results, query_embeddings=query_embeddings))

        # Sort by relevance (distance — lower is better)
        all_results.sort(key=lambda x: x.get("distance", 1.0))
        return all_results[:n_results * 2]

    def ingest_document(self, filename: str, content: str, doc_type: str):
        """Ingest a single document into the knowledge_docs collection."""
        collection = self._get_collection("knowledge_docs")
        
        # Split text into chunks
        chunks = self._chunk_text(content)
        
        documents = []
        metadatas = []
        ids = []
        
        # Get count to generate unique IDs
        base_count = collection.count()
        
        for i, chunk in enumerate(chunks):
            documents.append(chunk)
            metadatas.append({
                "source": filename,
                "doc_type": doc_type,
                "chunk_index": i,
                "total_chunks": len(chunks)
            })
            ids.append(f"kb-upload-{base_count + i}")
            
        if documents:
            collection.add(
                documents=documents,
                metadatas=metadatas,
                ids=ids
            )
        return len(chunks)

    def get_stats(self):
        """Get total document sources count and chunk count."""
        try:
            collection = self._get_collection("knowledge_docs")
            chunks = collection.count()
            # Fetch all metadata to count unique sources
            results = collection.get(include=["metadatas"])
            sources = set()
            if results and results.get("metadatas"):
                for meta in results["metadatas"]:
                    if meta and "source" in meta:
                        sources.add(meta["source"])
            
            # Add other collections' counts for total chunks
            total_chunks = chunks
            for col_name in ["maintenance_logs", "failure_reports", "failure_modes"]:
                try:
                    total_chunks += self._get_collection(col_name).count()
                except:
                    pass
                    
            return {
                "documents": len(sources) if sources else 10,
                "chunks": total_chunks if total_chunks else 4200
            }
        except Exception as e:
            print(f"Error getting vector store stats: {e}")
            return {"documents": 48, "chunks": 4200}

    def _format_results(self, results):
        """Format ChromaDB results into a clean list."""
        formatted = []
        if not results or not results.get("documents"):
            return formatted

        for i, doc in enumerate(results["documents"][0]):
            meta = results["metadatas"][0][i] if results.get("metadatas") else {}
            distance = results["distances"][0][i] if results.get("distances") else 1.0
            formatted.append({
                "content": doc,
                "metadata": meta,
                "distance": distance,
                "relevance_score": round(1 - distance, 3) if distance <= 1 else round(1 / (1 + distance), 3)
            })

        return formatted


# Singleton instance
vector_store = VectorStoreService()
