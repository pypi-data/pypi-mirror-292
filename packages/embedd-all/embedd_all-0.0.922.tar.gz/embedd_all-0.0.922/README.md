# embedd-all

`embedd-all` is a Python package designed to convert any Excel or PDF file into a format that can be used to create an embedding vector using embedding models. The package extracts text from PDFs, summarizes data from Excel files, and now includes functionality to create RAG (Retrieval-Augmented Generation) for PDFs using Voyage AI embedding models and Pinecone vector database.

## Features

- **PDF Processing**: Extracts text from each page of a PDF and returns it as an array.
- **Excel Processing**: Summarizes the data in each sheet by concatenating column names and their respective values, creating a new column `df["summarized"]`. If the Excel file contains multiple sheets, it processes each sheet and returns all summaries.
- **RAG Creation**: Creates RAG for PDFs using Voyage AI embedding models and stores them in a Pinecone vector database.

## Installation

Install the package via pip:

```bash
pip install embedd-all
```

## Usage

### Import the package

```python
from embedd_all.index import modify_excel_for_embedding, process_pdf, pinecone_embeddings_with_voyage_ai
```

### Example Usage

#### Processing an Excel File

The `modify_excel_for_embedding` function processes an Excel file, summarizes each row, and returns the summaries.

```python
import pandas as pd
from embedd_all.index import modify_excel_for_embedding

if __name__ == '__main__':
    # Path to the Excel file
    file_path = '/path/to/your/data.xlsx'
    context = "data"

    # Process the Excel file
    dfs = modify_excel_for_embedding(file_path=file_path, context=context)

    # Display the summarized data from the second sheet (if exists)
    if len(dfs) > 1:
        print(dfs[1].head(3))
```

#### Processing a PDF File

The `process_pdf` function extracts text from each page of a PDF file and returns it as an array.

```python
from embedd_all.index import process_pdf

if __name__ == '__main__':
    # Path to the PDF file
    file_path = '/path/to/your/document.pdf'

    # Process the PDF file
    texts = process_pdf(file_path)

    # Display the processed text
    print("Number of pages processed: ", len(texts))
    print("Sample text from the first page: ", texts[0])
```

#### Creating RAG for PDFs

The `pinecone_embeddings_with_voyage_ai` function creates RAG for PDFs using Voyage AI embedding models and stores them in a Pinecone vector database.

```python
from embedd_all.index import pinecone_embeddings_with_voyage_ai

def create_rag_for_pdfs():
    paths = ['/path/to/your/document.pdf']
    vector_db_name = 'your-vector-db-name'
    voyage_embed_model = 'voyage-2'
    embed_dimension = 1024
    pinecone_embeddings_with_voyage_ai(paths, PINECONE_KEY, VOYAGE_API_KEY, vector_db_name, voyage_embed_model, embed_dimension)

if __name__ == '__main__':
    create_rag_for_pdfs()
```

## Functions

### `modify_excel_for_embedding(file_path: str, context: str) -> list`

Processes an Excel file and summarizes the data in each sheet.

- **Parameters:**
  - `file_path` (str): Path to the Excel file.
  - `context` (str): Additional context to be added to each summary.

- **Returns:**
  - `list`: A list of DataFrames, each containing the summarized data for each sheet.

### `process_pdf(file_path: str) -> list`

Extracts text from each page of a PDF file.

- **Parameters:**
  - `file_path` (str): Path to the PDF file.

- **Returns:**
  - `list`: A list of strings, each representing the text extracted from a page.

### `pinecone_embeddings_with_voyage_ai(paths: list, PINECONE_KEY: str, VOYAGE_API_KEY: str, vector_db_name: str, voyage_embed_model: str, embed_dimension: int)`

Creates RAG for PDFs using Voyage AI embedding models and stores them in a Pinecone vector database.

- **Parameters:**
  - `paths` (list): List of paths to PDF files.
  - `PINECONE_KEY` (str): Pinecone API key.
  - `VOYAGE_API_KEY` (str): Voyage AI API key.
  - `vector_db_name` (str): Name of the Pinecone vector database.
  - `voyage_embed_model` (str): Name of the Voyage AI embedding model to use.
  - `embed_dimension` (int): Dimension of the embedding vectors.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Contact

If you have any questions or suggestions, please open an issue or contact the maintainer.

---

Happy embedding with `embedd-all`!