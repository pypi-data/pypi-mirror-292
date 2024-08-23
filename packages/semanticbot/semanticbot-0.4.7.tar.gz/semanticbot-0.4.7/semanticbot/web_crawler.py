import requests
from bs4 import BeautifulSoup
from .utils import load_embeddings, chunk_text, cosine_similarity
from langchain_community.vectorstores import FAISS
import numpy as np

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

    embeddings = load_embeddings() 

    if not chunks:
        raise ValueError("No chunks to process")

    # Process the chunks to create embeddings and a FAISS index
    print("🧠 Creating embeddings and FAISS index...")
    vectorstore = FAISS.from_documents(documents=chunks, embedding=embeddings)
    
    print("Ready for questions!")
    
    # Process the query and search the FAISS index
    query_embedding = embeddings.embed_query(query)
    
    # Get all document embeddings from the FAISS index
    document_embeddings = vectorstore.index.reconstruct_n(0, vectorstore.index.ntotal)
    
    # Compute cosine similarities between the query and each document embedding
    similarities = [cosine_similarity([query_embedding], [doc_embedding])[0][0] for doc_embedding in document_embeddings]
    
    # Get the top k most similar documents
    top_k_indices = np.argsort(similarities)[-5:][::-1]
    
    # Fetch the top k results
    results = [(vectorstore.docstore.search(vectorstore.index_to_docstore_id[i]), similarities[i]) for i in top_k_indices]
    
    if results:
        for i, (doc, score) in enumerate(results, 1):
            print(f"Match {i} - Similarity: {score:.4f}")
            print(f"**Text:** {doc.page_content}")
            print(f"**Source:** {doc.metadata.get('source', 'Unknown')}")
            print()  # Add a blank line for readability
    else:
        print("No matches found.")
    
    # Return the results in the same format as your original function
    return [(doc.page_content, score) for doc, score in results]
   