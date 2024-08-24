from google.cloud import storage
from langchain.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from google.cloud import bigquery
import os


class DataIngestor:
    def __init__(self, project_id,store,credentials):
        self.project_id = project_id
        self.store = store
        self.bq_client = bigquery.Client(project=project_id,credentials = credentials)
        self.storage_client = storage.Client(project=project_id)

    # def ingest_data(self, source_type):
    #     if source_type == 'pdf':
    #         return self.ingest_pdf_to_vectorstore(gcs_uri,chunk_size,chunk_overlap)
    #     elif source_type == 'bigquery':
    #         return self.ingest_bq_schema_to_vectorstore()
    #     else:
    #         raise ValueError("Unsupported source type. Please use 'pdf' or 'bigquery'.")

    def ingest_pdf_to_vectorstore(self, gcs_uri,chunk_size,chunk_overlap):
        # Download PDF from GCS
        bucket_name, blob_name = self._parse_gcs_uri(gcs_uri)
        bucket = self.storage_client.bucket(bucket_name)
        blob = bucket.blob(blob_name)
        pdf_path = f"/tmp/{os.path.basename(blob_name)}"
        try:
            blob.download_to_filename(pdf_path)
        except Exception as e:
            return f"Failed to download PDF: {e}"

        # Load PDF and process
        try:
            loader = PyPDFLoader(pdf_path)
            documents = loader.load()
        except Exception as e:
            return f"Failed to load PDF: {e}"
        # Split the documents into chunks
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
        docs = text_splitter.split_documents(documents)
        doc_texts = [doc.page_content for doc in docs]
        doc_meta = [{"len": len(t)} for t in doc_texts]

        # Add to vector store
        self.store.add_texts(doc_texts, metadatas=doc_meta)
        return f"PDF data from {gcs_uri} ingested successfully to the vector store."

    def ingest_bq_schema_to_vectorstore(self,query):
        schema_columns = self.bq_client.query(query=query).to_dataframe()

        # Convert schema to markdown (or another format) and ingest
        schema_text = schema_columns.to_markdown(index=False)
        self.store.add_texts([schema_text], metadatas=[{"len": len(schema_text)}])
        return f"BigQuery schema  ingested successfully to the vector store."

    def _parse_gcs_uri(self, gcs_uri):
        # Parse the GCS URI to extract bucket name and blob name
        if not gcs_uri.startswith("gs://"):
            raise ValueError("Invalid GCS URI. It must start with 'gs://'")
        path = gcs_uri[5:].split("/", 1)
        return path[0], path[1]
