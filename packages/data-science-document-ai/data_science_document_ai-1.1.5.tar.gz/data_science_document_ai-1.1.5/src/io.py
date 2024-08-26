"""Manage API calls and IO procedures."""

import os
from pathlib import Path

import tempfile
from time import sleep
import logging
import sys

import gspread
import pandas as pd
from google.cloud import bigquery, storage
from tqdm import tqdm

# Set standard output and standard error for the logs
logger = logging.getLogger("__name__")
logger.setLevel(logging.INFO)
logger.propagate = False

logger_format = "%(asctime)s [%(levelname)s] %(message)s"
formatter = logging.Formatter(logger_format)

h1 = logging.StreamHandler(sys.stdout)
h1.setLevel(logging.INFO)
h1.addFilter(lambda record: record.levelno <= logging.WARNING)
h1.setFormatter(formatter)

h2 = logging.StreamHandler(sys.stderr)
h2.setLevel(logging.ERROR)
h2.addFilter(lambda record: record.levelno == logging.ERROR)
h2.setFormatter(formatter)
logger.addHandler(h1)
logger.addHandler(h2)


from src.tms import download_document_api



def auth_gsheets(params):
    """Authenticate within Google Spreadsheet."""
    try:
        return gspread.service_account(params["path_g_app_cred"])
    except FileNotFoundError:
        return gspread.service_account()


def read_from_sheet(params):
    """Insert data to Google Spreadsheet."""
    # Authenticate to Google Spreadsheet
    gsheet = auth_gsheets(params)

    # Identify file and sheet
    sheet_file = gsheet.open_by_key(params[f"gsheet_file"])
    sheet = sheet_file.worksheet(params[f"gsheet_sheet"])

    shipment_filter_sheet = sheet.get_all_values()

    shipment_filter_df = pd.DataFrame(
        shipment_filter_sheet[1:], columns=shipment_filter_sheet[0]
    )

    return shipment_filter_df


def get_bq_client(params):
    """Get Google BigQuery client."""
    bq_client = bigquery.Client(project=params["bq_project_id"])
    job_config = bigquery.QueryJobConfig(
        allow_large_results=True,
        # flatten_results=True,
        labels={"project-name": params["project_name"]},
    )
    return bq_client, job_config


def query_dwh(params, query):
    """Query data from DWH."""
    client, job_config = get_bq_client(params)

    df = client.query(query=query, job_config=job_config).to_dataframe(
        progress_bar_type="tqdm"
    )
    return df


def select_samples_and_log(df_doc_meta_data, meta_folder_path, role, n_samples):
    """Select a sample of documents that are not downloaded.

    Add their IDs to metadata files.

     Args:
         df_doc_meta_data (pd.DataFrame): dataframe containing document IDs
         meta_folder_path (str): path to folder containing metadata file
         role (str): file type
         n_samples (int): number of samples to select
    """
    meta_data_path = os.path.join(meta_folder_path, f"{role}.csv")
    if os.path.isfile(meta_data_path):
        df_doc_meta_data_old = pd.read_csv(meta_data_path)
        df_doc_meta_data = df_doc_meta_data.loc[
            ~df_doc_meta_data["shipment_id"].isin(df_doc_meta_data_old["shipment_id"])
        ]
        df_doc_meta_data = df_doc_meta_data.sample(n=n_samples)
        df_doc_meta_data_old = pd.concat(
            [df_doc_meta_data_old, df_doc_meta_data], ignore_index=True, sort=False
        )
        df_doc_meta_data_old.to_csv(meta_data_path, index=False)
    else:
        df_doc_meta_data = df_doc_meta_data.sample(n=n_samples)
        df_doc_meta_data.to_csv(meta_data_path, index=False)

    return df_doc_meta_data


def download_documents(
    df_doc_meta_data, folder_path, meta_folder_path, role, n_samples=100
):
    """Download documents from TMS."""
    try:
        df_doc_meta_data = select_samples_and_log(
            df_doc_meta_data, meta_folder_path, role, n_samples
        )

        with tqdm(total=len(df_doc_meta_data)) as pbar:
            for _, row in df_doc_meta_data.iterrows():
                for i, dc_id in enumerate(row["doc_ids"].split("|")[:1]):
                    pdf_content = download_document_api(row["shipment_id"], dc_id)
                    destination_file_path = (
                        # f"{folder_path}/{role}-{row['shipment_id']}-{i}.pdf"
                        f"{folder_path}/{role}-{row['shipment_id']}.pdf"
                    )
                    with open(destination_file_path, "wb") as file:
                        file.write(pdf_content)

                    sleep(0.5)
                    pbar.update(1)

    except Exception as e:
        logger.info(f"Error downloading {role} documents: {e}")


def upload_documents_to_bucket(params):
    """Upload file to Google blob storage.

    Args:
        params (dict): parameters dictionary
    """
    # Get the storage client and the bucket
    client = get_storage_client(params)
    bucket = client.bucket(params["doc_ai_bucket_name"])

    # Select only the specified folder
    if len(params["document_name"]) == 1:
        params[
            "folder_documents"
        ] = f"{params['folder_documents']}/{params['document_name'][0]}"

    for root, dirs, files in os.walk(params["folder_documents"]):
        # Upload the files inside subdirectories
        for dir_name in dirs:
            for rt, dir, pdf_files in os.walk(f"{root}/{dir_name}"):
                upload_files_to_bucket(bucket, pdf_files, rt)

        # Upload the files (if not in a subdirectory)
        upload_files_to_bucket(bucket, files, root)

    return


def upload_pdf_to_bucket(params, content, file_name):
    """Upload bytes content to GCS bucket.

    Args:
        params (dict): Parameters dictionary containing project ID and bucket name.
        content (bytes): Content of the file to be uploaded.
        file_name (str): Name of the file to be uploaded.
    """
    try:
        # Create a temporary file to store the content
        temp_dir = tempfile.mkdtemp()
        temp_file_path = os.path.join(temp_dir, file_name)

        # Write the content to the temporary file
        with open(temp_file_path, "wb") as temp_file:
            temp_file.write(content)

        # Upload the temporary file to the bucket
        client = storage.Client(project=params["g_ai_project_name"])
        bucket = client.bucket(params["doc_ai_bucket_batch_input"])

        blob = bucket.blob(file_name)
        blob.upload_from_filename(temp_file_path)

        # Delete the temporary file
        os.remove(temp_file_path)
        os.rmdir(temp_dir)

        return f"gs://{params['doc_ai_bucket_batch_input']}/{file_name}", client  # noqa

    except Exception as e:
        print(
            f"Error uploading {file_name} to bucket {params['doc_ai_bucket_batch_input']}: {e}"
        )
        return None, None


def delete_folder_from_bucket(bucket_name, folder_name):
    """Delete a folder (prefix) and its contents from a GCS bucket.

    Args:
        bucket_name (str): Name of the GCS bucket.
        folder_name (str): Name of the folder (prefix) to delete.
    """
    try:
        client = storage.Client()
        bucket = client.get_bucket(bucket_name)

        # List all objects with the given prefix (folder name)
        blobs = bucket.list_blobs(prefix=folder_name)

        # Delete each object
        for blob in blobs:
            blob.delete()

    except Exception as e:
        logger.error(
            f"Error deleting folder {folder_name} from bucket {bucket_name}: {e}"
        )

def get_storage_client(params) -> storage.Client:
    """Get Google Storage client."""
    return storage.Client(project=params["g_ai_project_name"])


def upload_files_to_bucket(bucket, files, root):
    """Upload files to Google blob storage.

    Args:
        bucket: Google Storage bucket object
        files: list of files to upload
        root: root directory
    """
    with tqdm(total=len(files)) as pbar:
        for file_name in files:
            local_file_path = os.path.join(root, file_name)

            # Upload the file to the bucket
            blob = bucket.blob(local_file_path)
            blob.upload_from_filename(local_file_path)
            pbar.update(1)


def download_dir_from_bucket(bucket, directory_cloud, directory_local) -> bool:
    """Download file from Google blob storage.

    Args:
        bucket: Google Storage bucket object
        directory_cloud: directory to download
        directory_local: directory where to download

    Returns:
        bool: True if folder is not exists and not empty
    """
    result = False
    blobs = bucket.list_blobs(prefix=directory_cloud)  # Get list of files
    for blob in blobs:
        result = True
        if blob.name.endswith("/"):
            continue
        file_split = blob.name.split("/")
        directory = "/".join(file_split[0:-1])
        directory = directory_local / Path(directory)
        Path(directory).mkdir(parents=True, exist_ok=True)
        blob.download_to_filename(directory_local / Path(blob.name))
    return result

