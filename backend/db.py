import os
os.environ["CHROMA_TELEMETRY_ENABLED"] = "false"

from langchain_community.vectorstores import Chroma  
from langchain_core.documents import Document
from langchain_core.embeddings import Embeddings

from transformers import AutoTokenizer, AutoModel
import torch

CHROMA_DIR = "./chroma_store"

class QwenEmbeddings(Embeddings):
    def __init__(self, model_name="Qwen/Qwen3-Embedding-4B"):
        self.tokenizer = AutoTokenizer.from_pretrained(model_name, trust_remote_code=True)
        self.model = AutoModel.from_pretrained(
            model_name,
            trust_remote_code=True,
            torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32,
            device_map="cuda" if torch.cuda.is_available() else "cpu"
        )
        self.model.eval()

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        return [self._embed(text) for text in texts]

    def embed_query(self, text: str) -> list[float]:
        return self._embed(text)

    def _embed(self, text: str) -> list[float]:
        inputs = self.tokenizer(text, return_tensors="pt", truncation=True, max_length=512)
        inputs = {k: v.to(self.model.device) for k, v in inputs.items()}
        with torch.no_grad():
            outputs = self.model(**inputs)
            embeddings = outputs.last_hidden_state.mean(dim=1).squeeze(0)
        return embeddings.cpu().tolist()

# Initialize embedding model and vector store
embedding_model = QwenEmbeddings()
db = Chroma(persist_directory=CHROMA_DIR, embedding_function=embedding_model)

def search_similar_query(query: str, k: int = 1, threshold: float = 0.6):
    results = db.similarity_search_with_score(query, k=k)
    for doc, score in results:
        if score < (1 - threshold):
            return doc.page_content
    return None

def store_query_and_result(query: str, result: str):
    doc = Document(page_content=result, metadata={"query": query})
    db.add_documents([doc])  # Persist handled automatically
