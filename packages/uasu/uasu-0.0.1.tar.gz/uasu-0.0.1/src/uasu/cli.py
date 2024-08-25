#!/usr/bin/env python
import argparse
import datetime
from google.cloud import storage
from google.oauth2 import service_account


def main(source_file, bucket_name, service_account_key_file, link_expiration_days):
    if not 1 <= link_expiration_days <= 7:
        raise ValueError("Expiration days must be between 1 and 7")

    blob_name = source_file.split("/")[-1]

    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(blob_name)
    blob.upload_from_filename(source_file)

    credentials = service_account.Credentials.from_service_account_file(service_account_key_file)
    storage_client = storage.Client(credentials=credentials)
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(blob_name)

    url = blob.generate_signed_url(
        version="v4",
        expiration=datetime.timedelta(days=link_expiration_days),
        method="GET",
    )

    print(url)


def run():
    parser = argparse.ArgumentParser(description='Uploads files to Google Cloud Storage (GCS) and generates a time-limited signed URL.')
    parser.add_argument('source_file', type=str, help='the path to the file to upload')
    parser.add_argument('-b', '--bucket-name', type=str, help='the name of the GCS bucket where the file will be uploaded')
    parser.add_argument('-k', '--service-account-key-file', type=str, help='the path to the file containing the credentials of the GCP service account used to sign the URL')
    parser.add_argument('-e', '--link-expiration-days', type=int, default=7, help='the number of days during which the link will be valid')
    args = parser.parse_args()

    main(args.source_file, args.bucket_name, args.service_account_key_file, args.link_expiration_days)


if __name__ == '__main__':
    run()
