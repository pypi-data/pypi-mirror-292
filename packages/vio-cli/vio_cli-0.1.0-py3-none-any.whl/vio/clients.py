import json
import logging
import mimetypes
import os

import boto3
import requests

from vio.exceptions import ImproperlyConfigured
from vio.utils import list_static_files

logger = logging.getLogger(__name__)


class VioS3Client:
    def __init__(
        self, access_key_id: str, secret_access_key: str, prefix: str, bucket: str
    ):
        self.access_key_id = access_key_id
        self.secret_access_key = secret_access_key
        self.prefix = prefix
        self.bucket = bucket
        self.client = boto3.client(
            "s3",
            aws_access_key_id=access_key_id,
            aws_secret_access_key=secret_access_key,
        )

    def sync(self, theme: str, static_dir: str):
        static_files = list_static_files(static_dir)
        for path in static_files:
            absolute_path = os.path.join(static_dir, path)
            content_type, encoding = mimetypes.guess_type(absolute_path)
            with open(absolute_path, "rb") as static_file:
                logger.info(f"Uploading static file {self.prefix + path}")
                self.client.put_object(
                    ACL="private",
                    Body=static_file.read(),
                    Bucket=self.bucket,
                    ContentType=content_type,
                    Key=self.prefix + path,
                )

    def get_bucket_from_prefix(prefix: str) -> str:
        return "vicky-themes"


class VioAPIClient:
    def __init__(self, api_key: str, base_url: str = "http"):
        self.api_key = api_key
        self.base_url = self.get_base_url()

    def get_credentials(self, theme: str) -> dict:
        url = f"{self.base_url}/theme-builder/themes/{theme}/credentials/"
        headers = self.get_headers()
        res = requests.get(url, headers=headers)
        return res.json()

    def update_themes(self, theme: str, templates: dict, version: str) -> dict:
        url = f"{self.base_url}/theme-builder/themes/{theme}/"
        headers = self.get_headers()
        data = json.dumps(
            {
                "templates": templates,
                "version": version,
            }
        )
        res = requests.post(url, headers=headers, data=data)
        return res.json()

    def update_settings(self, theme: str, settings: dict) -> dict:
        url = f"{self.base_url}/theme-builder/themes/{theme}/settings/"
        headers = self.get_headers()
        data = json.dumps(settings)
        res = requests.post(url, headers=headers, data=data)
        return res.json()

    def get_headers(self):
        return {
            "x-theme-builder-api-key": self.api_key,
            "Content-Type": "application/json",
        }

    def get_base_url(self):
        base_url = os.getenv("VIO_BASE_URL")
        if not base_url:
            raise ImproperlyConfigured(
                "The VIO_BASE_URL environment variable must be set."
            )
        return base_url
