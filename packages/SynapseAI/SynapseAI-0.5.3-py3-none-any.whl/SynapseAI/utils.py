from langchain_community.embeddings import HuggingFaceBgeEmbeddings
import numpy as np
from langchain_text_splitters import RecursiveCharacterTextSplitter
from .config import EMBEDDING_MODEL
from .config import CHUNK_OVERLAP
from .config import CHUNK_SIZE

def cosine_similarity(a, b):
    a = np.array(a).flatten()
    b = np.array(b).flatten()
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))

def load_embeddings():
    return HuggingFaceBgeEmbeddings(model_name=EMBEDDING_MODEL)

def chunk_text(text):
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
        length_function=len,
    )
    return text_splitter.split_text(text)
