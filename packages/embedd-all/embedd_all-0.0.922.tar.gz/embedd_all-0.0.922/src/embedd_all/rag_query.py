import voyageai
import anthropic
import time
from pinecone import Pinecone, ServerlessSpec

def rag_and_query(pinecone_key: str, voyage_api_key: str, voyage_embed_model: str, index_name: str, anthropic_api_key: str, system_prompt: str, claude_model: str, query: str, max_tokens: int, temperature: float) -> str:
    
    pinecone_key = pinecone_key
    voyage_api_key = voyage_api_key
    VOYAGE_EMBED_MODEL = voyage_embed_model

    vo = voyageai.Client(api_key=voyage_api_key)

    query = query

    result = vo.embed(texts=[query], model=VOYAGE_EMBED_MODEL, input_type="document")

    index_name = index_name

    pc = Pinecone(api_key=pinecone_key)

    cloud = 'aws'
    region = 'us-east-1'

    spec = ServerlessSpec(cloud=cloud, region=region)

    if index_name not in pc.list_indexes().names():
    # if does not exist, create index
        pc.create_index(
            index_name,
            dimension=1024,
            metric='cosine',
            spec=spec
    )
    # wait for index to be initialized
    while not pc.describe_index(index_name).status['ready']:
        time.sleep(1)
    
    # connect to index
    index = pc.Index(index_name)
        # view index stats
    index.describe_index_stats()

    # query converted to embedding
    xq = result.embeddings[0]

    res = index.query(vector=xq, top_k=13,  include_metadata=True)

    limit = 100000

    contexts = [
        x['metadata']['content'] for x in res['matches']
    ]

    ANTHROPIC_API_KEY= anthropic_api_key

    client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

    # build our prompt with the retrieved contexts included
    prompt_start = (
        "Answer the question based on the context below.\n\n"+
        "Context:\n"
    )
    prompt_end = (
        f"\n\nQuestion: {query}\nAnswer:"
    )
    # append contexts until hitting limit
    for i in range(1, len(contexts)):
        if len("\n\n---\n\n".join(contexts[:i])) >= limit:
            prompt = (
                prompt_start +
                "\n\n---\n\n".join(contexts[:i-1]) +
                prompt_end
            )
            break
        elif i == len(contexts)-1:
            prompt = (
                prompt_start +
                "\n\n---\n\n".join(contexts) +
                prompt_end
            )

    message = client.messages.create(
        model=claude_model,
        max_tokens=max_tokens,
        temperature=temperature,
        system=system_prompt,
        messages=[
            {
                "role": "user", 
                "content": [
                    {
                        "type": "text",
                        "text": prompt
                    }   
                ]
            }
        ]
    )
    return message.content


def context_and_query(anthropic_api_key: str, system_prompt: str, claude_model: str, query: str, max_tokens: int, temperature: float, context: str) -> str:
    query = query

    ANTHROPIC_API_KEY= anthropic_api_key

    client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

    prompt = "Question: " + query + " \n Context: " + context + '\n Note: Make sure that if Question is not relevant to the given Context do not answer. Say this question is out of scope'

    message = client.messages.create(
        model=claude_model,
        max_tokens=max_tokens,
        temperature=temperature,
        system=system_prompt,
        messages=[
            {
                "role": "user", 
                "content": [
                    {
                        "type": "text",
                        "text": prompt
                    }   
                ]
            }
        ]
    )
    return message.content