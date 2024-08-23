from .utils import load_embeddings, chunk_text, create_faiss_index, search_faiss_index,cosine_similarity
import PyPDF2
from langchain_community.vectorstores import FAISS
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
    
    # Get embeddings
    embeddings = load_embeddings()

    if not chunks:
        raise ValueError("No chunks to process")

    vectorstore = FAISS.from_documents(documents=chunks, embedding=embeddings)
    
    
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
            print() 
    else:
        print("No matches found.")
    
    # Return the results in the same format as your original function
    return [(doc.page_content, score) for doc, score in results]
