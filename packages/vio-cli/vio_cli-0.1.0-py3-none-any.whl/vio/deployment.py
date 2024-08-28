import logging
import os
import subprocess

from vio.clients import VioAPIClient, VioS3Client
from vio.exceptions import ImproperlyConfigured
from vio.utils import encode_file, encode_templates_to_dict

logger = logging.getLogger(__name__)


class Deployment:
    def __init__(
        self,
        theme: str,
        template_dir=None,
        static_dir=None,
        custom_css=None,
        custom_js=None,
        api_key=None,
        version=None,
        *args,
        **kwargs,
    ):
        self.theme = theme
        self.template_dir = template_dir
        self.static_dir = static_dir
        self.custom_css = custom_css
        self.custom_js = custom_js
        self.api_key = api_key if api_key else self.get_api_key()
        self.version = version if version else self.get_version()
        self.api_client = self.get_api_client()

    def run(self):
        encoded_templates = []

        if self.static_dir:
            credentials = self.api_client.get_credentials(self.theme)
            s3_client = VioS3Client(
                credentials["s3_access_key_id"],
                credentials["s3_secret_access_key"],
                credentials["s3_prefix"],
                credentials["s3_bucket"],
            )
            s3_client.sync(self.theme, self.static_dir)
            logger.info("Successfully updated static files")

        if self.template_dir:
            encoded_templates = encode_templates_to_dict(self.template_dir)

        self.api_client.update_themes(self.theme, encoded_templates, self.version)
        logger.info("Successfully updated templates")

        if self.custom_css or self.custom_js:
            settings = {}
            if self.custom_css:
                settings["custom_css"] = encode_file(self.custom_css)
            if self.custom_js:
                settings["custom_js"] = encode_file(self.custom_js)
            self.api_client.update_settings(self.theme, settings)
            logger.info("Successfully updated settings")

        logger.info(f"Deployment finished (version {self.version})")

    def get_api_client(self):
        client = VioAPIClient(self.api_key)
        return client

    def get_s3_client(self):
        client = VioS3Client()
        return client

    def get_api_key(self):
        api_key = os.getenv("VIO_API_KEY")
        if not api_key:
            raise ImproperlyConfigured(
                "The VIO_API_KEY environment variable must be set."
            )
        return api_key

    def get_version(self):
        process = subprocess.Popen(
            ["git", "rev-parse", "--short", "HEAD"],
            shell=False,
            stdout=subprocess.PIPE,
        )
        git_short_hash = process.communicate()[0].strip()
        version = git_short_hash.decode()
        return version
