from .utils import load_embeddings, chunk_text, cosine_similarity
import PyPDF2
from langchain_community.vectorstores import FAISS
from langchain.schema import Document
import numpy as np

def process_pdf_internal(pdf_path, query):
    # Load PDF
    with open(pdf_path, 'rb') as pdf_file:
        reader = PyPDF2.PdfReader(pdf_file)
        text = ''
        for page in reader.pages:
            text += page.extract_text()
    
    # Chunk text
    chunks = chunk_text(text)
    documents = [Document(page_content=chunk) for chunk in chunks]
    
    # Get embeddings
    embeddings = load_embeddings()

    if not chunks:
        raise ValueError("No chunks to process")

    # Create FAISS index from chunks and embeddings
    vectorstore = FAISS.from_documents(documents=documents, embedding=embeddings)
    
    # Process the query and search the FAISS index
    query_embedding = embeddings.embed_query(query)
    
    # Get all document embeddings from the FAISS index
    document_embeddings = vectorstore.index.reconstruct_n(0, vectorstore.index.ntotal)
    
    # Compute cosine similarities between the query and each document embedding
    similarities = [cosine_similarity(query_embedding, doc_embedding) for doc_embedding in document_embeddings]

    # Get the top 5 most similar documents
    top_k_indices = np.argsort(similarities)[-5:][::-1]
    
    # Fetch the top 5 results
    results = [(vectorstore.docstore.search(vectorstore.index_to_docstore_id[i]), similarities[i]) for i in top_k_indices]
    
    # Return results in the format [(chunks[i], score) for i, score in results]
    return [(chunks[i], score) for i, score in [(top_k_indices[j], similarities[top_k_indices[j]]) for j in range(len(top_k_indices))]]
