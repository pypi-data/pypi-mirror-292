from langchain_community.embeddings import HuggingFaceBgeEmbeddings
from langchain_community.vectorstores import FAISS
import numpy as np
from langchain_text_splitters import RecursiveCharacterTextSplitter

def cosine_similarity(a, b):
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))

def load_embeddings():
    return HuggingFaceBgeEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

def chunk_text(text, chunk_size=1024, chunk_overlap=80):
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        length_function=len,
    )
    return text_splitter.split_text(text)


def create_faiss_index(chunks, embeddings):
    return FAISS.from_texts(chunks, embeddings)

def search_faiss_index(index, query, k=5):
    return index.similarity_search_with_score(query, k=k)