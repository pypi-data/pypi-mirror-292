from .utils import load_embeddings, chunk_text, create_faiss_index, search_faiss_index
import PyPDF2

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
    chunk_embeddings = [embeddings.embed_query(chunk) for chunk in chunks]
    query_embedding = embeddings.embed_query(query)
    
    # Create FAISS index
    index = create_faiss_index(chunk_embeddings)
    
    # Search using FAISS
    results = search_faiss_index(index, query_embedding, k=5)
    
    # Return top results
    return [(chunks[i], score) for i, score in results]