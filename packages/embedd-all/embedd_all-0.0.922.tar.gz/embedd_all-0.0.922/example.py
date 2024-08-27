from src.embedd_all.index import modify_excel_for_embedding, process_pdf, pinecone_embeddings_with_voyage_ai
from src.embedd_all.rag_query import rag_and_query, context_and_query
import os

ANTHROPIC_API_KEY = os.environ['ANTHROPIC_API_KEY']
PINECONE_KEY = os.environ['PINECONE_KEY']
VOYAGE_API_KEY = os.environ['VOYAGE_API_KEY']

def create_rag_for_pdfs():
    paths = ['/Users/arnabbhattachargya/Desktop/flamingo_english_book.pdf']
    vector_db_name = 'arnab-test'
    voyage_embed_model = 'voyage-2'
    # dimensions of embed model
    embed_dimension=1024
    pinecone_embeddings_with_voyage_ai(paths, PINECONE_KEY, VOYAGE_API_KEY, vector_db_name, voyage_embed_model, embed_dimension)

def query_with_context():
    CLAUDE_MODEL = "claude-3-5-sonnet-20240620"
    SYSTEM_PROMPT = "You are a world-class medicine expert. Respond only with detailed information"
    TEMPERATURE = 0
    MAX_TOKENS = 4000
    QUERY = 'what medications to take when we feel sick'
    CONTEXT = """
       Medicine related context
    """
    answer = context_and_query(ANTHROPIC_API_KEY, SYSTEM_PROMPT, CLAUDE_MODEL, QUERY, MAX_TOKENS, TEMPERATURE, CONTEXT)
    print(answer)



def rag_query():
    CLAUDE_MODEL = "claude-3-5-sonnet-20240620"
    #inddex name for pine_cone vector db
    INDEX_NAME = 'index_name'
    TEMPERATURE = 0
    MAX_TOKENS = 4000
    QUERY = 'How to configure UI'
    SYSTEM_PROMPT = "You are a world-class document writer. Respond only with detailed description and implementation. Use bullet points if neccessary"
    VOYAGE_EMBED_MODEL = 'voyage-2'

    resp = rag_and_query(
        temperature=TEMPERATURE,
        max_tokens=MAX_TOKENS,
        anthropic_api_key=ANTHROPIC_API_KEY,
        claude_model=CLAUDE_MODEL, 
        index_name=INDEX_NAME, 
        pinecone_key=PINECONE_KEY, 
        query=QUERY, 
        system_prompt=SYSTEM_PROMPT,
        voyage_api_key=VOYAGE_API_KEY,
        voyage_embed_model=VOYAGE_EMBED_MODEL
        )
    
    # print("resp: ", resp["text"])

    for text_block in resp:
        print(text_block.text)

if __name__ == '__main__':
    # Example usage
    # file_path = '/Users/arnabbhattachargya/Desktop/data.xlsx'
    # file_path = '/Users/arnabbhattachargya/Desktop/setu-product/UMAP.pdf'
    # context = "data"
    # dfs = modify_excel_for_embedding(file_path=file_path, context=context)
    # print(dfs[2].head(3))

    # texts = process_pdf(file_path)
    # print("Text Length: ", len(texts))
    # print("Text process: ", texts)
    # rag_query()
    # create_rag_for_pdfs()
    query_with_context()