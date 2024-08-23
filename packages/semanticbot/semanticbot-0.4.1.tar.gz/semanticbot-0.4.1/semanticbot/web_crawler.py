import requests
from bs4 import BeautifulSoup
from .utils import load_embeddings, chunk_text, create_faiss_index, search_faiss_index

def crawl_and_query_internal(url, query):
    # Fetch web content
    response = requests.get(url)
    if response.status_code != 200:
        raise Exception(f"Failed to fetch {url} (Status code: {response.status_code})")
    
    # Parse content
    soup = BeautifulSoup(response.content, 'html.parser')
    text = soup.get_text()
    
    # Chunk text
    chunks = chunk_text(text)
    
    # Get embeddings
    embeddings = load_embeddings()
    chunk_embeddings = [embeddings.embed_query(chunk) for chunk in chunks]
    query_embedding = embeddings.embed_query(query)
    
    # Create FAISS index
    index = create_faiss_index(chunk_embeddings)
    
    # Search using FAISS
    results = search_faiss_index(index, query_embedding, k=5)
    
    # Return top results
    return [(chunks[i], score) for i, score in results]