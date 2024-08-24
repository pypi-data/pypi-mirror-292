# GCP LangChain Package

This package uses GCP services to create a vector db to store the embeddings of structured and unstructured data 

## Installation

```bash
pip install lv-vectordb-gcp
```


#How to use
**Create a Vector Store:** Use the VectorStore class to create a vector store. Ensure you pass the necessary parameters when initializing the class.

**Ingest Data:** Utilize the DataIngestor class to convert raw data, such as PDFs or structured data, into embeddings. These embeddings can then be uploaded to a BigQuery vector store table.

**Store different types of data:** A single vector store table is capable of containing both structured and unstructured data, offering flexibility in your data storage.

**Authentication:** Ensure you have your GCP service key credentials ready, as they are required to access GCP services.
