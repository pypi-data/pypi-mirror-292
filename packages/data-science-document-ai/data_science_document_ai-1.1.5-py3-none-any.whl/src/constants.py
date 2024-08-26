"""Config constant params for data science project(s)."""

project_parameters = {
    # Project constants
    "project_name": "document-ai",
    "project_hash": "ceb0ac54",
    # Google related parameters
    "bq_project_id": "data-pipeline-276214",
    "g_ai_project_name": "forto-data-science-production",
    "g_ai_project_id": "738250249861",
    "g_api_endpoint": "eu-documentai.googleapis.com",
    "g_location": "eu",
    "g_region": "europe-west3",
    # Google Cloud Storage
    "doc_ai_bucket_name": "ds-document-capture",
    "doc_ai_bucket_batch_input": "ds-batch-process-docs",
    "doc_ai_bucket_batch_output": "ds-batch-process-output",
    # Paths
    # Download and upload parameters
    "folder_documents": "doc_cap_input/doc_cap_splitter",
    "folder_data": "data",
    "gsheet_input": False,  # Set to True if input is from a g-sheet file
    "gsheet_file": "",  # add g-sheet file id
    "gsheet_sheet": "",  # add worksheet name
    # Big Query
    "g_ai_gbq_db_schema": "document_ai",
    "g_ai_gbq_db_table_out": "document_ai_api_calls_v1",
    # Gold layer
    "gbq_db_schema_g": "gold",
    "gbq_db_table_g": "gsc_shipments",
    # Sem layer
    "gbq_db_schema_s": "sem__common",
    "gbq_db_table_s": "shipment_provided_documents",
    # document types
    "document_types": [
        "arrivalNotice",
        "bookingConfirmation",
        "packingList",
        "commercialInvoice",
        "vgmOnlyExports",
        "finalMbL",
        "draftMbL",
        "finalHbL",
        "partnerInvoice",
        "customsAssessment",
    ],
    # models metadata (confidence),
    "g_model_data_folder": "models",
    "local_model_data_folder": "data"
}
