import io
import os
import json
import time
import logging
import tempfile
from typing import IO, Any, Dict, Tuple, Union, Callable, Optional

import requests

logger = logging.getLogger("utils")
logger.setLevel("DEBUG")


def format_body(body) -> str:
    if isinstance(body, str):
        # assume string is json formatted
        return body
    elif isinstance(body, dict) or isinstance(body, list):
        return json.dumps(body)
    elif isinstance(body, list):
        # allow list of objects
        return json.dumps([b.to_dict() if hasattr(body, "to_dict") else b for b in body])
    elif hasattr(body, "to_dict"):
        # assume body is a request object
        return json.dumps(body.to_dict())
    else:
        raise RuntimeError(f"Unsupported body type: {type(body)}")


def extract_body(resp):
    try:
        # responses with bodies have json method
        if hasattr(resp, "json") and callable(resp.json):
            return resp.json()
        # ApiException just has raw body
        elif hasattr(resp, "body"):
            # json can deserialize bytes or str
            return json.loads(resp.body)
    except Exception:
        raise ValueError(f"Only JSON bodies supported. Received: {resp.text if resp else 'None'}")


# copied from ozone-backend
def get_value(obj: Any, path: Union[str, list], default_value: Optional[Any] = None) -> Any:
    field_path = []
    if isinstance(path, list):
        field_path = path or []
    elif isinstance(path, str):
        field_path = path.split(".")
    # to ensure the value of the field is returned regardless of what it is,
    # as long as it exists, don't depend on truthiness of value, use a separate flag
    found_field = False
    for field_name in field_path:
        # each nested field must be found
        found_field = False
        if not field_name:
            return default_value
        if type(obj) is dict:
            if field_name in obj:
                found_field = True
                obj = {field_name: obj[field_name]}
            else:
                obj = None
                break
        elif hasattr(obj, field_name):
            found_field = True
            obj = getattr(obj, field_name)
        else:
            obj = None
            break
    if found_field:
        return obj
    else:
        # the default value might need to be calculated from another field that only exists
        # in the default case and therefore can only be evaluated at that time. therefore,
        # check to see if the default is callable, in which case execute it to calc the value.
        return default_value() if isinstance(default_value, Callable) else default_value


def get_file_size(file: Union[str, IO, io.BufferedRandom]) -> int:
    # Some file-like objects do not inherit from a common IO interface
    if isinstance(file, str):
        filename = file
    else:
        try:
            filename = file.name
        except AttributeError:
            raise AttributeError(f"{file} is not a valid file-like object or path")

    pathname = os.path.abspath(filename)
    return os.path.getsize(pathname)


def ns_to_sec(ns: int) -> float:
    """Nanoseconds to floating point seconds with accuracy to milliseconds"""
    return round(ns / (10e6)) / 1000


class TransferProgress:
    _start_time_ns: int = time.time_ns()

    def __init__(
        self,
        total_length: int,
        progress_cb: Optional[Callable] = None,
        upload: bool = True,
        target: Optional[str] = None,
        increment: None = None,
        verbose: bool = False,
    ) -> None:
        if total_length in [None, 0]:
            raise RuntimeError(f"total_length({total_length}) required for tracking transfer progress")

        self._cb = progress_cb
        self._total_length = total_length
        self._upload = upload
        self._bytes_transferred = 0
        self._pct_complete = -1
        self._target = target or ""
        self._inc = increment or 10
        self._verbose = verbose
        self._start_time_ns = time.time_ns()
        self._end_time_ns = None
        # log immediately to show start, don't wait for first chunk (_pct_complete must be negative)
        self.monitor_progress(0)

    @property
    def elapsed_ns(self) -> int:
        return time.time_ns() - self._start_time_ns

    @property
    def total_ns(self) -> Optional[int]:
        return (self._end_time_ns - self._start_time_ns) if self._end_time_ns else None

    @property
    def mode(self) -> str:
        return "Uploading" if self._upload else "Downloading"

    @property
    def target_path(self) -> Optional[str]:
        return os.path.abspath(self._target) if self._target else None

    @property
    def transfer_size(self) -> float:
        """
        :return: Size of file to transfer in units of MBs (rounded to the nearest KB)
        :rtype: float
        """
        return round(self._total_length / (1024 * 1024), 3)

    def monitor_progress(self, chunk: int) -> None:
        self._bytes_transferred += chunk

        pct = int(100 * self._bytes_transferred / self._total_length)
        # wait for progress to increase a full percent
        if pct == self._pct_complete:
            return
        self._pct_complete = pct

        if self._pct_complete == 0:
            self.begin_progress()

        if self._pct_complete % self._inc == 0 or self._pct_complete >= 100:
            self.log_progress()

        if self._pct_complete >= 100:
            self.end_progress()

        # execute callback with new percentage TODO: make async
        if self._cb:
            self._cb(pct)

    def begin_progress(self) -> None:
        if self._start_time_ns:
            return
        self._start_time_ns = time.time_ns()
        if self._verbose:
            logger.info(f"{self.mode}: {self.target_path} ({self.transfer_size:,} MB)")
        else:
            logger.debug(f"{self.mode}: {self.target_path} {self.transfer_size:,} MB")

    def log_progress(self) -> None:
        if self._verbose:
            logger.info(
                f"\t\t{self._pct_complete}% {'uploaded' if self._upload else 'downloaded'} "
                f"({round(self.elapsed_ns / 10e6) / 1000} secs)"
            )

    def end_progress(self) -> None:
        # only record/log end once
        if self._end_time_ns:
            return
        self._end_time_ns = time.time_ns()
        if self.total_ns:
            if self._verbose:
                logger.info(f"{self.mode} Complete: {self.target_path} ({ns_to_sec(self.total_ns)} secs)")
            else:
                logger.debug(f"{self.mode} Complete: {self.target_path} {ns_to_sec(self.total_ns)} secs")


def upload_media(
    file: Union[str, tempfile._TemporaryFileWrapper, io.BufferedRandom, io.BufferedReader, io.BufferedWriter],
    bucket: str,
    object_name: Optional[str] = None,
    storage: str = "store",
    progress: Optional[Callable] = None,
) -> Optional[Dict[str, Any]]:
    """Upload a file to an S3 bucket
    :param progress:
    :param storage: `cache` or `store`. cache is only used for direct upload flow, not needed for backend currently
    :param file: File to upload
    :param bucket: Bucket to upload to
    :param object_name: S3 object name. If not specified then file_name is used
    :return: True if file was uploaded, else False
    """
    local_open = False
    if not file:
        logger.error(f"File not specified for upload")
        return None
    elif isinstance(file, str):
        filename = file
        file = open(filename, "rb")
        local_open = True
    else:
        filename = file.name
    if not os.path.exists(filename):
        logger.error(f"Unable to upload {filename} that doesnt exist")
        return None

    # If S3 object_name was not specified, use file_name
    bucket_key = object_name or os.path.basename(filename)

    try:
        import boto3

        logger.debug(
            f"Uploading {file.name} to {bucket}/{bucket_key}, " f"{os.path.getsize(filename) / (1024 * 1024):6.2f} MB"
        )
        boto3.set_stream_logger("boto3.resources", "DEBUG")  # type: ignore
        region = os.environ.get("AWS_REGION", "us-east-1")
        s3_client = boto3.client("s3", region_name=region)

        tp = TransferProgress(get_file_size(file), progress_cb=progress, target=bucket_key)
        s3_client.upload_file(filename, bucket, bucket_key, Callback=tp.monitor_progress)
        return {
            "id": bucket_key,
            "storage": storage,
            "size": get_file_size(file),
        }
    except Exception as e:
        logger.error(f"Failed to upload {bucket_key} to bucket {bucket}: {e}")
        return None
    finally:
        if local_open:
            file.close()


def upload_file_to_presigned_s3(file_path: str, presigned_url: str) -> Optional[Dict]:
    bucket_key = s3_attrs_from_url(presigned_url)
    if not bucket_key:
        logger.error(f"Unable to extract S3 data from presigned URL {presigned_url}")
        return None

    meta = {"id": bucket_key[0], "name": bucket_key[1], "presigned_url": presigned_url}
    with open(file_path, "rb") as file:
        meta["size"] = get_file_size(file)  # type: ignore
        file_content = file.read()

    upload_response = requests.put(presigned_url, data=file_content)
    if upload_response.status_code != 200:
        logger.error(f"Failed to upload {file_path} to presigned URL {presigned_url}: {upload_response.text}")
        return None

    return meta


def upload_file_to_s3(
    file_path: str, s3_bucket_name, s3_object_name, progress_cb: Optional[Callable[[int], None]] = None
) -> Optional[Dict]:
    meta = upload_media(
        file=file_path,
        bucket=s3_bucket_name,
        object_name=s3_object_name,
        storage="cache",
        progress=progress_cb,
    )
    if meta:
        meta["url"] = f"https://{s3_bucket_name}.s3.amazonaws.com/{s3_object_name}"
    return meta


def s3_attrs_from_url(url: str) -> Optional[Tuple[str, str]]:
    """
    Extracts bucket, key, and storage from a url with the following format:
    `https://<bucket_name>.s3.amazonaws.com/<key>`
    :param url:
    :return: (bucket name, item key). If url can't be parsed, None is returned.
    """
    # from urllib.parse import urlparse
    import re

    #
    # uri = urlparse(url)
    groups = re.search(r"^https://([\w.-]+)\.s3\.amazonaws\.com/([^?]+)", url)
    if not groups:
        logger.error(f"Unable find S3 tokens in {url}")
        return None
    bucket, key = groups[1], groups[2]
    return bucket, key
