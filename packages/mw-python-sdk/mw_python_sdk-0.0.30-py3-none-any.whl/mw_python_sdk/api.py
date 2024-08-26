# TODO: token 相关的初始化可以通过 default Callable 来实现
import logging
import os
import random
import string
import time
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from urllib.parse import quote
from typing import BinaryIO, Dict, List, Optional, Set, Union


import boto3
import requests
import requests_unixsocket
from botocore.exceptions import ClientError, NoCredentialsError, PartialCredentialsError

from .dataset import Dataset, DatasetCommit, DatasetFile, DatasetList, UploadInfo

# Create a logger for your library
logger = logging.getLogger(__name__)

HEYWHALE_SITE = os.getenv("HEYWHALE_HOST", "https://www.heywhale.com")
HEYWHALE_DS_BUCKET = os.getenv("HEYWHALE_DS_BUCKET", "kesci")


@dataclass(frozen=True)
class DatasetFileForUpload:
    """This is dataclass for file to upload.

    Args:
        local_path (str): local file path.
        remote_path (str): remote file path in the dataset.

    """

    local_path: str
    remote_path: str


@dataclass
class DatasetConstructor:
    """DatasetConstructor
    Args:
        title (str): dataset title
        short_description (str, optional): short description of the dataset. Defaults to "".
        data_files (Set[DatasetFileForUpload], optional): dataset files. Defaults to set().
    """

    title: str
    short_description: str
    data_files: Set[DatasetFileForUpload] = field(default_factory=set)

    def add_file(self, source: str, destination: str):
        """
        将文件添加到待上传的数据集中

        Args:
            source (str): 文件源路径
            destination (str): 文件目标路径

        Returns:
            None
        """
        self.data_files.add(DatasetFileForUpload(source, destination))

    def add_dir(self, local_dir: str, remote_dir: str):
        """
        递归遍历本地目录，将文件添加到远程数据集中。

        Args:
            local_dir (str): 本地目录路径。
            remote_dir (str): 远程数据集目录路径。

        Returns:
            None

        """
        for root, _dirs, files in os.walk(local_dir):
            for file in files:
                file_path = os.path.join(root, file)
                rel_path = os.path.relpath(os.path.join(root, file), local_dir)
                path_in_dataset = os.path.join(remote_dir, rel_path)
                self.add_file(file_path, path_in_dataset)

    def push_dataset(self) -> Dataset:
        """
        将数据集推送到平台并返回数据集对象。

        Args:
            无参数。

        Returns:
            Dataset: 推送到平台后的数据集对象。

        Raises:
            ValueError: 如果创建数据集失败，则抛出该异常。
        """
        dataset = _create_dataset(
            title=self.title,
            files=list(self.data_files),
            short_description=self.short_description,
        )
        if dataset is None:
            raise ValueError("Failed to create dataset")
        return dataset


def parse_datetime(date_string: str) -> datetime:
    """
    Parse a datetime string into a datetime object.

    Args:
        date_string (str): The datetime string to parse.

    Returns:
        datetime: A datetime object.

    """
    if date_string is None:
        return datetime.now()
    return datetime.strptime(date_string, "%Y-%m-%dT%H:%M:%S.%fZ")


def convert_to_dataset_file(files) -> List[DatasetFile]:
    """
    将给定的文件列表转换为 DatasetFile 对象的列表。

    Args:
        files (List[Dict]): 文件列表，每个元素为字典类型，包含 "_id"、"Token"、"Size" 和 "SubPath" 等字段。

    Returns:
        List[DatasetFile]: 转换后的 DatasetFile 对象列表。

    """
    if files is None:
        return []
    dataset_files = [
        DatasetFile(
            file.get("_id"),
            file.get("Token"),
            file.get("Size"),
            "" if file.get("SubPath") is None else file.get("SubPath"),
        )
        for file in files
    ]
    return dataset_files


def get_dataset(dataset_id: str, token: Optional[str] = None) -> Optional[Dataset]:
    """
    Fetches dataset details from Heywhale.

    Args:
        dataset_id (str): The ID of the dataset to fetch.
        token (str, optional): The token for authentication. If not provided, the function will use the 'MW_TOKEN' environment variable.

    Returns:
        Dataset: A Dataset object with the dataset details.

    Raises:
        ValueError: If no token is provided and the 'MW_TOKEN' environment variable is not set.
    """
    if token is None:
        token = os.getenv("MW_TOKEN")
        if not token:
            raise ValueError(
                "No token provided and 'MW_TOKEN' environment variable is not set."
            )

    url = f"{HEYWHALE_SITE}/api/datasets/{dataset_id}"
    headers = {
        "x-kesci-token": token,
        "x-kesci-resource": dataset_id,
    }

    response = requests.get(url, headers=headers, timeout=10)
    if response.status_code == 200:
        # print("get datasets ", response.json())
        files = convert_to_dataset_file(response.json().get("Files"))
        # print("Get Files ", files)
        files_with_subpath = convert_to_dataset_file(
            response.json().get("FilesStructure")
        )
        # print("Get Files with subpath", files_with_subpath)
        # filter the files overlapped with files_with_subpath
        files_key_set = set([file.key for file in files_with_subpath])
        for file in files:
            # print("file", file)
            if file.key not in files_key_set:
                # print("not in")
                files_with_subpath.append(file)
        # print("files_with_subpath", files_with_subpath)
        # files.extend(files_with_subpath)
        # print("return dataset files",files)

        # Files里面不是某个版本的Files
        # 这里用 downloadUrl?Version的方式重新构造一次 files
        return Dataset(
            _id=response.json().get("_id"),
            title=response.json().get("Title"),
            short_description=response.json().get("ShortDescription"),
            folder_name=response.json().get("FolderName"),
            files=files_with_subpath,
            commits=[
                DatasetCommit(
                    commit.get("_id"),
                    commit.get("CommitMessage"),
                    parse_datetime(commit.get("CreateDate")),
                )
                for commit in response.json().get("DatasetVersions")
            ],
            created_at=parse_datetime(response.json().get("CreateDate")),
            updated_at=parse_datetime(response.json().get("UpdateDate")),
        )

    response.raise_for_status()
    return None


def _update_dataset(
    dataset_id: str,
    files: List[DatasetFile],
    commit_message: Optional[str] = None,
    token: Optional[str] = None,
):
    """
    Updates the dataset with the given ID by adding or removing files.

    :param id: The ID of the dataset to update.
    :param files: A list of DatasetFile objects representing the files to add or remove.
    :param token: The token for authentication. If not provided, the function will use the 'MW_TOKEN' environment variable.
    :raises ValueError: If no token is provided and the 'MW_TOKEN' environment variable is not set.
    """
    if token is None:
        token = os.getenv("MW_TOKEN")
        if not token:
            raise ValueError(
                "No token provided and 'MW_TOKEN' environment variable is not set."
            )
    url = f"{HEYWHALE_SITE}/api/datasets/{dataset_id}/files"
    headers = {"x-kesci-token": token, "x-kesci-resource": dataset_id}
    data = {
        "Files": [file.key for file in files],
        "FilesStructure": [
            {"Token": file.key, "SubPath": file.sub_path} for file in files
        ],
    }
    if commit_message is not None:
        data["CommitMessage"] = commit_message
    response = requests.put(
        url,
        json=data,
        headers=headers,
        timeout=10,
    )
    if response.status_code == 200:
        return
    else:
        print(response.text)
        response.raise_for_status()


def _get_update_token(token: Optional[str] = None) -> Optional[UploadInfo]:
    """
    Retrieves the upload token for updating a dataset.

    Args:
        token: The token for authentication. If not provided, the function will use the 'MW_TOKEN' environment variable.

    Returns:
        An UploadInfo object containing the upload token details.

    Raises:
        ValueError: If no token is provided and the 'MW_TOKEN' environment variable is not set.
    """
    if token is None:
        token = os.getenv("MW_TOKEN")
        if not token:
            raise ValueError(
                "No token provided and 'MW_TOKEN' environment variable is not set."
            )
    url = f"{HEYWHALE_SITE}/api/dataset-upload-token"
    headers = {"x-kesci-token": token}
    response = requests.get(url, headers=headers, timeout=10)
    if response.status_code == 200:
        return UploadInfo(
            endpoint=response.json().get("endpoint"),
            ak=response.json().get("accessKeyId"),
            sk=response.json().get("secretAccessKey"),
            token=response.json().get("sessionToken"),
            bucket=response.json().get("bucket"),
            prefix_to_save=response.json().get("prefixToSave"),
            region=response.json().get("region"),
        )
    else:
        response.raise_for_status()
        return None


def generate_timestamped_string(revision: int) -> str:
    """
    Generates a timestamped string based on the current time and a revision number.

    :param revision: The revision number.
    :return: A timestamped string.
    """
    timestamp = int(time.time() * 1000)
    result = f"{timestamp}_{revision}"
    return result


def _upload_file(
    path_or_fileobj: Union[str, Path, bytes, BinaryIO],
    path_in_dataset: Union[str, Path],
    upload_info: UploadInfo,
) -> str:
    """
    Uploads a file to a dataset.

    :param path_or_fileobj: The path or file object of the file to upload.
    :param path_in_dataset: The path to save the file in the dataset.
    :param id: The ID of the dataset.
    :param overwrite: Whether to overwrite an existing file with the same path in the dataset.
    :param token: The token for authentication. If not provided, the function will use the 'MW_TOKEN' environment variable.
    :raises ValueError: If no token is provided and the 'MW_TOKEN' environment variable is not set.
    """

    session = boto3.Session(
        aws_access_key_id=upload_info.ak,
        aws_secret_access_key=upload_info.sk,
        aws_session_token=upload_info.token,
        region_name=upload_info.region,
    )
    s3 = session.client("s3", endpoint_url=upload_info.endpoint)

    bucket_name = upload_info.bucket

    object_key = os.path.join(
        upload_info.prefix_to_save, generate_timestamped_string(1)
    )
    if path_in_dataset != "":
        # get base filename from path_in_dataset
        # 前端是在对象存储中key没有带目录的
        # 目录存在api的SubPath字段里面
        # 这里仿照前端的格式存以防有什么不统一的地方导致错误
        object_key = os.path.join(object_key, os.path.basename(path_in_dataset))
    # print(f"upload object key {object_key}")
    try:
        if isinstance(path_or_fileobj, (str, Path)):
            with open(path_or_fileobj, "rb") as file:
                s3.put_object(Bucket=bucket_name, Key=object_key, Body=file)
        else:
            s3.put_object(Bucket=bucket_name, Key=object_key, Body=path_or_fileobj)
    except Exception as e:
        print(f"Error putting object '{object_key}' from bucket '{bucket_name}': {e}")
    return object_key


def upload_file(
    path_or_fileobj: Union[str, Path, bytes, BinaryIO],
    path_in_dataset: Union[str, Path],
    dataset_id: str,
    overwrite: bool = False,
    token: Optional[str] = None,
):
    """
    Uploads a file to a dataset.

    Args:
        path_or_fileobj (Union[str, Path, bytes, BinaryIO]): The path or file object of the file to upload.
        path_in_dataset (str | Path): The path to save the file in the dataset.
        id (str | Dataset): The ID of the dataset.
        overwrite (bool, optional): Whether to overwrite an existing file with the same path in the dataset. Defaults to False.
        token (Optional[str], optional): The token for authentication. If not provided, the function will use the 'MW_TOKEN'

    Raises:
        ValueError: If no token is provided and the 'MW_TOKEN' environment variable is not set.
    """
    if token is None:
        token = os.getenv("MW_TOKEN")
        if not token:
            raise ValueError(
                "No token provided and 'MW_TOKEN' environment variable is not set."
            )

    upload_info = _get_update_token(token)
    if upload_info is None:
        raise ValueError("Failed to get upload token.")
    object_key = _upload_file(path_or_fileobj, path_in_dataset, upload_info)
    new_dataset_files: List[DatasetFile] = []
    dataset = get_dataset(dataset_id, token)
    if dataset is not None:
        for file in dataset.files:
            if file.path_in_dataset() != path_in_dataset:
                new_dataset_files.append(file)
            elif not overwrite:
                # print("file exists, skip uploading")
                return
        pp = str(Path(path_in_dataset).parent)
        new_dataset_files.append(DatasetFile("", object_key, 0, _norm_path(pp)))
    _update_dataset(
        dataset_id,
        new_dataset_files,
        commit_message=f"添加文件 {path_in_dataset}",
        token=token,
    )


def _norm_path(pp: str) -> str:
    """让目录格式和前端传的一样

    Args:
        path (str): /a/ -> a/ ./ -> "" /a -> a/

    Returns:
        str: 带尾部"/"的相对路径
    """
    # print(f"input pp {pp}")
    # 强加一个 /，按照示例格式来，怕没加没处理好。
    if not pp.endswith("/"):
        pp = pp + "/"
    # 开头的也去掉，避免绝对路径的格式。
    if pp.startswith("/"):
        pp = pp[1:]
    # 本地目录直接忽略
    if pp.startswith("./"):
        pp = pp[2:]
    return pp


def upload_folder(
    folder_path: Union[str, Path],
    folder_in_dataset: str,
    dataset_id: str,
    overwrite: bool = False,
    token: Optional[str] = None,
):
    """
    Upload a local folder to a dataset.

    Args:
        folder_path (str | Path): The path of the local folder to be uploaded.
        folder_in_dataset (str): The path in the dataset where the folder will be uploaded.
        dataset_id (str | Dataset): The ID or instance of the dataset to upload to.
        overwrite (bool, optional): Whether to overwrite existing files in the dataset. Defaults to False.
        token (Optional[str], optional): The authentication token for the dataset. If not provided, it will be retrieved from the 'MW_TOKEN' environment variable. Defaults to None.

    Returns:
        None

    Raises:
        ValueError: If no token is provided and the 'MW_TOKEN' environment variable is not set,
                    or if the folder does not exist,
                    or if the dataset is not found,
                    or if failed to get upload token.
    """
    if token is None:
        token = os.getenv("MW_TOKEN")
        if not token:
            raise ValueError(
                "No token provided and 'MW_TOKEN' environment variable is not set."
            )
    # check folder existence
    if not os.path.isdir(folder_path):
        raise ValueError("Folder does not exist.")
    upload_info = _get_update_token(token)
    if upload_info is None:
        raise ValueError("Failed to get upload token.")
    new_dataset_files: Set[DatasetFile] = set()
    dataset = get_dataset(dataset_id, token)
    if dataset is None:
        raise ValueError(f"Dataset '{dataset_id}' not found.")

    for root, _dirs, files in os.walk(folder_path):
        # print("files")
        for file in files:
            # print(f"file {file}")
            file_path = os.path.join(root, file)
            rel_path = os.path.relpath(os.path.join(root, file), folder_path)
            path_in_dataset = os.path.join(folder_in_dataset, rel_path)
            # print(f"root {root} rel_path {rel_path} upload file {file_path} path in {os.path.join(path_in_dataset,rel_path)} id {id}")
            object_key = _upload_file(file_path, path_in_dataset, upload_info)
            skip_upload = False
            for dfile in dataset.files:
                # print(
                #     f"dfile {dfile.path_in_dataset() } file {path_in_dataset}"
                # )
                if dfile.path_in_dataset() != path_in_dataset:
                    # print(f"add dfile {dfile}")
                    new_dataset_files.add(dfile)
                elif not overwrite:
                    # print("file exists, skip uploading")
                    skip_upload = True
                    break
            if skip_upload:
                break
            else:
                pp = str(Path(path_in_dataset).parent)
                # print(f"Append new file {object_key}, {_norm_path(pp)}")
                new_dataset_files.add(DatasetFile("", object_key, 0, _norm_path(pp)))
    if len(new_dataset_files) == 0:
        # skip update if no files in directory
        return
    # print(new_dataset_files)
    _update_dataset(
        dataset_id,
        list(new_dataset_files),
        commit_message=f"添加目录 {folder_in_dataset}",
        token=token,
    )


def _init_cache(cache_dir: Optional[Union[str, Path]] = None) -> Path:
    """
    Initializes the cache directory for the MW SDK.

    Args:
        cache_dir: The path to the cache directory. If not provided, the default cache directory will be used.

    Returns:
        The path to the cache directory.
    """
    if cache_dir is None:
        cache_dir = Path(os.getenv("MW_CACHE_DIR", "~/.cache/mw"))
    if isinstance(cache_dir, str):
        cache_dir = Path(cache_dir)
    cache_dir.expanduser().mkdir(parents=True, exist_ok=True)
    cache_dir.expanduser().joinpath("blobs").mkdir(exist_ok=True)
    cache_dir.expanduser().joinpath("datasets").mkdir(exist_ok=True)
    return cache_dir


def _download_single_file_by_cached(
    dataset_id: str,
    endpoint: str,
    ak: str,
    sk: str,
    token: str,
    bucket_and_key: str,
    commit: str,
    filename: str,
    cache_dir: Path,
    local_dir: Optional[Union[str, Path]] = None,
    local_path: Optional[Union[str, Path]] = None,
) -> Path:
    """
    Downloads a single file from a dataset.
    Args:
        dataset_id: The ID of the dataset.
        endpoint: The endpoint of the object storage service.
        ak: The access key ID.
        sk: The secret access key.
        token: The session token.
        etag: The ETag of the file.
        commit: The commit id.
        filename: The name of the file.
        cache_dir: The cache directory.
        local_dir: The local directory to save the file to. If not provided, the default cache directory will be used.
        local_path: The path to save the file to. If specified, `local_dir` is ignored.
    Returns:
        The path to the downloaded
    """
    slk_path = (
        Path(cache_dir)
        .expanduser()
        .joinpath("datasets")
        .joinpath(dataset_id)
        .joinpath("snapshots")
        .joinpath(commit)
        .joinpath(filename)
    )
    if local_dir is not None:
        slk_path = Path(local_dir).joinpath(filename)
    if local_path is not None:
        slk_path = Path(local_path)
    if slk_path.exists():
        return slk_path
    mw_cached_root_dir = os.environ.get("MW_CACHED_ROOT_DIR", "/var/mw")
    sock_path = os.path.join(mw_cached_root_dir, "cached.sock")
    session = requests_unixsocket.Session()
    # convert a path to percent-encoded path
    quoted_path = quote(sock_path, safe="")
    logger.debug("connecting to mw-cached at %s", quoted_path)
    r = session.get(
        f"http+unix://{quoted_path}/get/object",
        params={
            "uri": f"s3://{bucket_and_key}",
            "ak": ak,
            "sk": sk,
            "token": token,
            "endpoint": endpoint,
        },
        timeout=3600,
    )
    blob_path = r.json().get("cachedFilePath")
    logger.debug("cached blob file path: %s", blob_path)
    slk_path.parent.mkdir(parents=True, exist_ok=True)
    slk_path.symlink_to(blob_path)
    return slk_path


def _download_single_file(
    download_url: str,
    id: str,
    filename: str,
    etag: str,
    commit: str,
    cache_dir: Path,
    local_dir: Optional[Union[str, Path]] = None,
    local_path: Optional[Union[str, Path]] = None,
) -> Path:
    """
    Downloads a single file from a dataset.

    Args:
        download_url: The URL to download the file from.
        id: The ID of the dataset.
        filename: The name of the file.
        etag: The ETag of the file.
        commit: The commit id.
        cache_dir: The cache directory.
        local_dir: The local directory to save the file to. If not provided, the default cache directory will be used.
        local_path: The path to save the file to. If specified, `local_dir` is ignored.

    Returns:
        The path to the downloaded file.
    """
    response = requests.get(download_url, stream=True, timeout=10)
    total_size = int(response.headers.get("content-length", 0))
    chunk_size = 4096
    slk_path = (
        Path(cache_dir)
        .expanduser()
        .joinpath("datasets")
        .joinpath(id)
        .joinpath("snapshots")
        .joinpath(commit)
        .joinpath(filename)
    )
    if local_dir is not None:
        slk_path = Path(local_dir).joinpath(filename)
    if local_path is not None:
        slk_path = Path(local_path)
    if slk_path.exists():
        return slk_path

    blob_path = Path(cache_dir).expanduser().joinpath("blobs").joinpath(etag)
    if not blob_path.exists():
        file_path = (
            Path(cache_dir).expanduser().joinpath("blobs").joinpath(etag + ".download")
        )
        file_path.parent.mkdir(parents=True, exist_ok=True)
        if file_path.exists():
            raise ValueError(
                f"File '{filename}' is being downloaded, please wait. If the downloading process is interrupted, please delete the lock file '{file_path}' manually."
            )
        with open(file_path, "wb") as file:
            for chunk in response.iter_content(chunk_size=chunk_size):
                file.write(chunk)
        blob_path = file_path.rename(file_path.parent.joinpath(etag))
    slk_path.parent.mkdir(parents=True, exist_ok=True)
    slk_path.symlink_to(blob_path)
    return slk_path


def download_dir(
    id: str,
    commit: Optional[str] = None,
    cache_dir: Optional[Union[str, Path]] = None,
    local_dir: Optional[Union[str, Path]] = None,
    token: Optional[str] = None,
) -> Path:
    """Download a directory from the dataset.

    Args:
        id (str): The dataset id.

    Returns:
        str: The path to the downloaded directory.
    """
    if token is None:
        token = os.getenv("MW_TOKEN")
        if not token:
            raise ValueError(
                "No token provided and 'MW_TOKEN' environment variable is not set."
            )
    cache_dir = _init_cache(cache_dir)
    dataset_detail = get_dataset(id)
    if dataset_detail is None:
        raise ValueError(f"Dataset '{id}' not found.")
    path_to_key: Dict[str, str] = dict()
    # print("files", dataset_detail.files)
    for file in dataset_detail.files:
        # print("pathind ", file.path_in_dataset())
        path_to_key[file.path_in_dataset()] = file.key
    upload_info = _get_update_token(token)
    if upload_info is None:
        raise ValueError("Failed to get upload token.")

    bucket_name = upload_info.bucket
    url = f"{HEYWHALE_SITE}/api/datasets/{id}/downloadUrl"
    headers = {
        "x-kesci-token": token,
    }
    if commit is None:
        commit = dataset_detail.commits[-1]._id
    params = {"Version": commit}
    response = requests.get(url, headers=headers, params=params, timeout=10)
    if response.status_code == 200:
        files = response.json().get("files")
        for file in files:
            download_url = file.get("Url")
            filepath_in_dataset = file.get("Name") + file.get("Ext")
            sub_path = file.get("SubPath")
            if sub_path is not None:
                filepath_in_dataset = os.path.join(sub_path, filepath_in_dataset)
            key = path_to_key[filepath_in_dataset]
            mw_cached_root_dir = os.environ.get("MW_CACHED_ROOT_DIR", "/var/mw")
            sock_path = os.path.join(mw_cached_root_dir, "cached.sock")
            # file exists
            if os.path.exists(sock_path):
                _download_single_file_by_cached(
                    id,
                    upload_info.endpoint,
                    upload_info.ak,
                    upload_info.sk,
                    upload_info.token,
                    os.path.join(bucket_name, key),
                    commit,
                    filepath_in_dataset,
                    cache_dir,
                    local_dir,
                )
            else:
                # get etag
                try:
                    session = boto3.Session(
                        aws_access_key_id=upload_info.ak,
                        aws_secret_access_key=upload_info.sk,
                        aws_session_token=upload_info.token,
                        region_name=upload_info.region,
                    )
                    s3 = session.client("s3", endpoint_url=upload_info.endpoint)
                    # print("Get etag bucket key", bucket_name, key)
                    response = s3.head_object(Bucket=bucket_name, Key=key)
                    # Extract the ETag from the response
                    etag = response["ETag"]
                    # print(f"Etag {etag}")
                    # trim quote
                    etag = etag[1:-1]
                    _download_single_file(
                        download_url,
                        id,
                        filepath_in_dataset,
                        etag,
                        commit,
                        cache_dir,
                        local_dir,
                    )
                except NoCredentialsError:
                    print("Error: AWS credentials not available.")
                except PartialCredentialsError:
                    print("Error: Incomplete AWS credentials.")
                except ClientError as e:
                    # The client error includes more details about the error
                    if e.response["Error"]["Code"] == "404":
                        print(
                            f"Error: The object '{key}' does not exist in the bucket '{bucket_name}'."
                        )
                    elif e.response["Error"]["Code"] == "403":
                        print(
                            f"Error: Access to the object '{key}' in the bucket '{bucket_name}' is forbidden."
                        )
                    else:
                        print(f"Error: {e.response['Error']['Message']}")
                except Exception as e:
                    print(f"An unexpected error occurred: {str(e)}")
    else:
        print(response.text)
        response.raise_for_status()
    if local_dir is None:
        dir = (
            Path(cache_dir)
            .expanduser()
            .joinpath("datasets")
            .joinpath(id)
            .joinpath("snapshots")
            .joinpath(commit)
        )
        return dir
    else:
        dir = Path(local_dir)
        return dir


def download_file(
    dataset_id: str,
    filename: str,
    commit: Optional[str] = None,
    cache_dir: Optional[Union[str, Path]] = None,
    local_dir: Optional[Union[str, Path]] = None,
    token: Optional[Union[str, Path]] = None,
) -> Path:
    """Download a file from the dataset.

    Args:
        id (str): The dataset id.
        filename (str): The file name in the dataset.
        cache_dir (Optional[str | Path], optional): The directory to cache the downloaded file. Defaults to None.
        local_dir (Optional[str | Path], optional): The local directory to save the downloaded file. Defaults to None.

    Returns:
        str: The path to the downloaded file.
    """
    if token is None:
        token = os.getenv("MW_TOKEN")
        if not token:
            raise ValueError(
                "No token provided and 'MW_TOKEN' environment variable is not set."
            )
    cache_dir = _init_cache(cache_dir)
    dataset_detail = get_dataset(dataset_id)
    if dataset_detail is None:
        raise ValueError(f"Dataset '{dataset_id}' not found.")
    path_to_key: Dict[str, str] = dict()
    for file in dataset_detail.files:
        path_to_key[file.path_in_dataset()] = file.key

    if filename not in path_to_key:
        raise ValueError(f"File '{filename}' not found in dataset '{dataset_id}'.")
    upload_info = _get_update_token(token)
    if upload_info is None:
        raise ValueError("Failed to get upload token.")

    bucket_name = upload_info.bucket

    url = f"{HEYWHALE_SITE}/api/datasets/{dataset_id}/downloadUrl"
    headers = {
        "x-kesci-token": token,
    }
    if commit is None:
        commit = dataset_detail.commits[-1].get_id()
    params = {"Version": commit}
    response = requests.get(url, headers=headers, params=params, timeout=10)
    download_url: str = ""
    if response.status_code == 200:
        files = response.json().get("files")
        logger.debug("get dataset files through api: %s", files)
        for file in files:
            sub_path = file.get("SubPath") if file.get("SubPath") is not None else ""
            if os.path.join(sub_path, file.get("Name")) + file.get("Ext") == filename:
                download_url = file.get("Url")
                break
        else:
            raise ValueError(f"File '{filename}' not found in dataset '{id}'.")
    else:
        print(response.text)
        response.raise_for_status()
    key = path_to_key[filename]
    mw_cached_root_dir = os.environ.get("MW_CACHED_ROOT_DIR", "/var/mw")
    sock_path = os.path.join(mw_cached_root_dir, "cached.sock")
    # file exists
    if os.path.exists(sock_path):
        logger.debug("cached socket exists using cached")
        return _download_single_file_by_cached(
            dataset_id,
            upload_info.endpoint,
            upload_info.ak,
            upload_info.sk,
            upload_info.token,
            os.path.join(bucket_name, key),
            commit,
            filename,
            cache_dir,
            local_dir,
        )
    else:
        # get etag
        try:
            session = boto3.Session(
                aws_access_key_id=upload_info.ak,
                aws_secret_access_key=upload_info.sk,
                aws_session_token=upload_info.token,
                region_name=upload_info.region,
            )
            s3 = session.client("s3", endpoint_url=upload_info.endpoint)
            response = s3.head_object(Bucket=bucket_name, Key=key)
            etag = response["ETag"]
            etag = etag[1:-1]
            logger.debug("get object %s etag: %s", os.path.join(bucket_name, key), etag)
            slk_path = _download_single_file(
                download_url, dataset_id, filename, etag, commit, cache_dir, local_dir
            )
        except NoCredentialsError:
            print("Error: AWS credentials not available.")
        except PartialCredentialsError:
            print("Error: Incomplete AWS credentials.")
        except ClientError as e:
            # The client error includes more details about the error
            if e.response["Error"]["Code"] == "404":
                print(
                    f"Error: The object '{key}' does not exist in the bucket '{bucket_name}'."
                )
            elif e.response["Error"]["Code"] == "403":
                print(
                    f"Error: Access to the object '{key}' in the bucket '{bucket_name}' is forbidden."
                )
            else:
                print(f"Error: {e.response['Error']['Message']}")
        except Exception as e:
            print(f"An unexpected error occurred: {str(e)}")
        return slk_path


def delete_file(
    dataset_id: str,
    filepath_in_dataset: str,
    token: Optional[str] = None,
):
    """Delete a file from the dataset."""
    if token is None:
        token = os.getenv("MW_TOKEN")
        if not token:
            raise ValueError(
                "No token provided and 'MW_TOKEN' environment variable is not set."
            )
    dataset = get_dataset(dataset_id, token)
    if dataset is None:
        raise ValueError(f"Dataset '{id}' not found.")
    upload_info = _get_update_token(token)
    if upload_info is None:
        raise ValueError("Failed to get upload token.")
    # print("HHHHH")
    new_dataset_files: List[DatasetFile] = []
    # print("dateset files", dataset.files)
    for file in dataset.files:
        # a = file.path_in_dataset()
        # b = filepath_in_dataset
        # print(f"A {a} B {b}")
        if file.path_in_dataset() != filepath_in_dataset:
            new_dataset_files.append(file)
        else:
            print(f"delete file {file.path_in_dataset()}")
            continue
    _update_dataset(
        dataset_id,
        new_dataset_files,
        commit_message=f"删除文件 {filepath_in_dataset}",
        token=token,
    )
    return


def delete_folder():
    pass


def create_commit(
    dataset_id: str,
    commit_message: str,
    token: Optional[str] = None,
) -> DatasetCommit:
    if token is None:
        token = os.getenv("MW_TOKEN")
        if not token:
            raise ValueError(
                "No token provided and 'MW_TOKEN' environment variable is not set."
            )
    upload_info = _get_update_token(token)
    if upload_info is None:
        raise ValueError("Failed to get upload token.")
    dataset = get_dataset(dataset_id, token)
    if dataset is None:
        raise ValueError(f"Dataset '{dataset_id}' not found.")
    _update_dataset(dataset_id, dataset.files, commit_message, token)
    dataset = get_dataset(dataset_id, token)
    if dataset is None:
        raise ValueError(f"Dataset '{dataset_id}' not found.")
    return dataset.commits[-1]


def create_dataset(
    title: str,
    local_dir: str,
    remote_dir: Optional[str],
    short_description: Optional[str],
) -> Optional[Dataset]:
    """
    根据提供的参数创建数据集对象

    Args:
        title (str): 数据集的标题
        local_dir (str): 数据集在本地存储的目录
        remote_dir (Union[str, None]): 数据集在远程存储的目录，可为空或None
        short_description (Union[str, None]): 数据集的简短描述，可为空或None

    Returns:
        Optional[Dataset]: 创建的数据集对象，若创建失败则返回None
    """
    if short_description is None:
        short_description = title
    dataset_constructor = DatasetConstructor(
        title=title, short_description=short_description, data_files=set()
    )
    if remote_dir is None:
        remote_dir = ""
    dataset_constructor.add_dir(local_dir, remote_dir)

    return _create_dataset(
        title=dataset_constructor.title,
        files=list(dataset_constructor.data_files),
        short_description=dataset_constructor.short_description,
    )


def _create_dataset(
    title: str,
    files: List[DatasetFileForUpload],
    short_description: Optional[str] = None,
    folder_name: Optional[str] = None,
    token: Optional[str] = None,
    enable_download: bool = True,
) -> Optional[Dataset]:
    """Creates a dataset

    Args:
        title (str): The title of the dataset.
        description (str): The description of the dataset.
        folder_name (Optional[str]): The folder name of the dataset, could be empty.

    Returns:
        Dataset: the created dataset
    """
    if token is None:
        token = os.getenv("MW_TOKEN")
        if not token:
            raise ValueError(
                "No token provided and 'MW_TOKEN' environment variable is not set."
            )
    url = f"{HEYWHALE_SITE}/api/datasets"
    headers = {
        "x-kesci-token": token,
    }
    if folder_name is None:
        folder_name = "".join(random.choices(string.ascii_lowercase, k=8))
    if short_description is None:
        short_description = title
    upload_info = _get_update_token(token)
    dataset_files: List[DatasetFile] = list()
    if upload_info is None:
        raise ValueError("Failed to get upload token.")
    for file in files:
        object_key = _upload_file(file.local_path, file.remote_path, upload_info)
        sub_path = _norm_path(str(Path(file.remote_path).parent))
        dataset_files.append(
            DatasetFile(_id="", size=0, key=object_key, sub_path=sub_path)
        )
    data = {
        "Title": title,
        "ShortDescription": short_description,
        "FolderName": folder_name,
        "EnableDownload": enable_download,
        "Type": 0,
        "Files": [file.key for file in dataset_files],
        "FilesStructure": [
            {"Token": file.key, "SubPath": file.sub_path} for file in dataset_files
        ],
    }
    # print(f"data {data}")
    response = requests.post(
        url,
        json=data,
        headers=headers,
        timeout=10,
    )
    if response.status_code == 200:
        document = response.json().get("document")
        return Dataset(
            _id=document.get("_id"),
            title=document.get("Title"),
            short_description=document.get("ShortDescription"),
            folder_name=document.get("FolderName"),
            files=dataset_files,
            commits=[],
            created_at=parse_datetime(document.get("CreateDate")),
            updated_at=parse_datetime(document.get("UpdateDate")),
        )
    else:
        response.raise_for_status()
        return None


def delete_dataset(
    dataset_id: str,
    token: Optional[str] = None,
):
    """
    删除指定的数据集。

    Args:
        id (str or Dataset): 数据集的ID或数据集对象。
        token (Optional[str], optional): 访问数据集的token。如果未提供，则使用环境变量'MW_TOKEN'。默认为None。

    Returns:
        None

    Raises:
        ValueError: 如果未提供token且环境变量'MW_TOKEN'未设置。
        HTTPError: 如果请求失败，则抛出HTTPError异常。

    """
    if token is None:
        token = os.getenv("MW_TOKEN")
        if not token:
            raise ValueError(
                "No token provided and 'MW_TOKEN' environment variable is not set."
            )

    url = f"{HEYWHALE_SITE}/api/datasets/{dataset_id}"
    headers = {
        "x-kesci-token": token,
    }
    response = requests.delete(
        url,
        headers=headers,
        timeout=10,
    )
    if response.status_code == 200:
        return

    print(response.text)
    response.raise_for_status()
    return


def _list_datasets(
    title: str = "",
    limit: int = 10,
    page: int = 1,
    start_date: time = None,
    end_date: time = None,
    token: Optional[str] = None,
):
    if token is None:
        token = os.getenv("MW_TOKEN")
        if not token:
            raise ValueError(
                "No token provided and 'MW_TOKEN' environment variable is not set."
            )
    headers = {
        "x-kesci-token": token,
    }

    url = f"{HEYWHALE_SITE}/api/user/datasets"
    params = {
        "perPage": limit,
        "page": page,
        "Title": title,
        "startDate": start_date,
        "endDate": end_date,
    }

    response = requests.get(
        url,
        headers=headers,
        params=params,
        timeout=10,
    )
    if response.status_code == 200:
        document = response.json()
        datasets: List[Dataset] = []
        for d in document.get("data"):
            files = convert_to_dataset_file(d.get("Files"))
            files_with_subpath = convert_to_dataset_file(d.get("FilesStructure"))
            if len(files) > 0:
                files_key_set = set([file.key for file in files])
                for file in files:
                    if file.key not in files_key_set:
                        files_with_subpath.append(file)
            commits = []
            if d.get("DatasetVersions") is not None:
                commits = [
                    DatasetCommit(
                        commit.get("_id"),
                        commit.get("CommitMessage"),
                        parse_datetime(commit.get("CreateDate")),
                    )
                    for commit in d.get("DatasetVersions")
                ]
            datasets.append(
                Dataset(
                    _id=d.get("_id"),
                    title=d.get("Title"),
                    short_description=d.get("ShortDescription"),
                    folder_name=d.get("FolderName"),
                    files=files_with_subpath,
                    commits=commits,
                    created_at=parse_datetime(d.get("CreateDate")),
                    updated_at=parse_datetime(d.get("UpdateDate")),
                )
            )
        return DatasetList(
            datasets=datasets,
            total=document.get("totalNum"),
            page=document.get("page"),
            limit=document.get("perPage"),
        )
    else:
        print(response.text)
        response.raise_for_status()
        return None


class DatasetIterator:
    """
    DatasetIterator 类

    该类提供了一个迭代器接口，用于遍历数据集。
    它封装了数据集加载、预处理和迭代的逻。
    """

    def __init__(self, title, page=1, limit=10):
        self.title = title
        self.limit = limit
        self.page = page
        self.total = 0
        self.processed_count = 0
        self.current_batch = []
        self.finished = False

    def __iter__(self):
        return self

    def __next__(self):
        if not self.current_batch and not self.finished:
            # Fetch the next page of datasets
            dataset_list = _list_datasets(
                title=self.title,
                page=self.page,
                limit=self.limit,
            )
            self.total = dataset_list.total

            if not dataset_list.datasets:
                self.finished = True
                raise StopIteration

            self.current_batch = dataset_list.datasets
            self.processed_count += len(self.current_batch)
            logger.debug("Processed: %d / Total: %d", self.processed_count, self.total)
            # If all items have been processed, mark as finished
            if self.processed_count >= self.total:
                self.finished = True
            else:
                self.page += 1

        if not self.current_batch:
            raise StopIteration

        # Return the next dataset in the current batch
        return self.current_batch.pop(0)


def list_all_datasets(title: str = "") -> List[Dataset]:
    """
    列出所有满足给定标题的数据集

    Args:
        title (str, optional): 数据集标题，默认为空字符串。

    Returns:
        List[Dataset]: 包含所有满足给定标题的数据集的列表。

    """
    datasets = list()
    for dataset in DatasetIterator(title):
        datasets.append(dataset)
    return datasets


def list_datasets(
    title: str = "",
    limit: int = 10,
    page: int = 1,
) -> DatasetIterator:
    """
    返回数据集的迭代器对象，可指定数据集标题、返回数据条数及页数

    Args:
        title (str, optional): 数据集标题. Defaults to "".
        limit (int, optional): 每页返回的数据条数. Defaults to 10.
        page (int, optional): 页码. Defaults to 1.

    Returns:
        DatasetIterator: 数据集的迭代器对象.

    """
    return DatasetIterator(title, page, limit)
