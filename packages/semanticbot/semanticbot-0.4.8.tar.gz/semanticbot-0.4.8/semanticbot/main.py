from .pdf_processor import process_pdf_internal
from .web_crawler import crawl_and_query_internal

def process_pdf(pdf_path, query):
    """
    Process a PDF file and answer a query about its content.
    
    :param pdf_path: Path to the PDF file
    :param query: Question about the PDF content
    :return: List of relevant text chunks and their similarity scores
    """
    return process_pdf_internal(pdf_path, query)

def crawl_and_query(url, query):
    """
    Crawl a web page and answer a query about its content.
    
    :param url: URL of the web page to crawl
    :param query: Question about the web page content
    :return: List of relevant text chunks and their similarity scores
    """
    return crawl_and_query_internal(url, query)

