# uasu: Upload And Sign URL

`uasu` is a simple but convenient CLI tool that allows you to upload files to cloud-based object storage platforms and generate a signed URL which can be used to safely share them with others.

`uasu` currently supports Google Cloud Storage, with plans to support additional object storage services in the future.

## Installation

Install via `pipx`:

```bash
pipx install uasu
```

## Usage

You must have a Google Cloud service account with the `Storage Object Viewer` role, and a JSON key file present in your local environment.

Then you can invoke `uasu` as follows:

```bash
uasu -b <GCS_BUCKET_NAME> -k <PATH_TO_JSON_KEY_FILE> <PATH_TO_FILE_TO_UPLOAD>
```
