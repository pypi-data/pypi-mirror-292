# -*- coding: utf-8 -*-
# @Author: Erin & Joanne
# @Date:   2024-02-11 13:26:17
# @Last Modified by:   Vivian Li
# @Last Modified time: 2024-02-18 14:53:37
# @Description: Provides method retrieve metadata from aws buckets and objects.

import boto3
from cryptography.fernet import Fernet
from gailbot.configs import PLUGIN_CONFIG


class S3BucketManager:
    fernet = Fernet(PLUGIN_CONFIG.EN_KEY)
    aws_api_key = fernet.decrypt(PLUGIN_CONFIG.ENCRYPTED_API_KEY).decode()
    aws_api_id = fernet.decrypt(PLUGIN_CONFIG.ENCRYPTED_API_ID).decode()

    def __init__(self):
        pass

    # Retrieve and return the version of the bucket
    # TODO: exceptions are not catched here. Caller expected to catch exceptions
    def get_remote_version(self, bucket_name, object_name) -> str:
        """
        If bucket_name and object_name identifies an existing object in aws s3 bucket, and the
        object has s3 remote metadata for version, returns the updated version of the object

        Parameters
        ----------
        bucket_name
        object_name

        Returns
        -------
        str

        Raises
        -------

        """
        s3 = boto3.client(
            "s3",
            aws_access_key_id=S3BucketManager.aws_api_id,
            aws_secret_access_key=S3BucketManager.aws_api_key,
        )

        s3_object = s3.head_object(Bucket=bucket_name, Key=object_name)
        object_metadata = s3_object["Metadata"]

        return object_metadata["version"]
