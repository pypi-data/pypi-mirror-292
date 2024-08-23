import json
from enum import Enum
import logging

import tornado

from sagemaker_jupyterlab_extension_common.clients import get_sagemaker_client

logging.basicConfig(format="%(levelname)s: %(message)s", level=logging.INFO)


class Environment(Enum):
    STUDIO_SSO = "STUDIO_SSO"
    STUDIO_IAM = "STUDIO_IAM"
    MD = "MD"
    UNKNOWN = "UNKNOWN"


class EnvironmentDetector:
    _cached_env = None

    @classmethod
    def get_environment(cls):
        """
        Detects the environment in which the code is running. This is done by checking for the presence of
        certain files and environment variables. The result is cached for subsequent calls.
        :return: Environment - The environment in which the code is running.
        :rtype: Environment
        """

        if cls._cached_env is None:
            cls._cached_env = cls._detect_environment()
            logging.info(f"Detecting environment for the first time: {cls._cached_env}")
        logging.info(f"Environment is {cls._cached_env}")
        return cls._cached_env

    @classmethod
    def _detect_environment(cls):
        try:
            with open("/opt/ml/metadata/resource-metadata.json", "r") as f:
                data = json.load(f)
                if (
                    "AdditionalMetadata" in data
                    and "DataZoneScopeName" in data["AdditionalMetadata"]
                ):
                    return Environment.MD
                elif "ResourceArn" in data:
                    sm_domain_id = data["DomainId"]
                    logging.info(f"DomainId - {sm_domain_id}")
                    sm_client = get_sagemaker_client()
                    domain_details = tornado.ioloop.IOLoop.current().run_sync(
                        lambda: sm_client.describe_domain(sm_domain_id)
                    )
                    logging.debug(f"Studio domain level details: {domain_details}")
                    if (
                        cls.is_q_enabled_studio_domain(domain_details)
                        and domain_details.get("AuthMode") == "SSO"
                    ):
                        return Environment.STUDIO_SSO

                    # always return free tier even if it is SSO mode
                    # admins can control the usage through IAM policy
                    # This should not affect MD as they are already detected and returned
                    return Environment.STUDIO_IAM
        except Exception as e:
            logging.error(f"Error detecting environment: {e}")
        return Environment.UNKNOWN

    @classmethod
    def is_q_enabled_studio_domain(cls, domain_details):
        return (
            domain_details.get("DomainSettings") is not None
            and domain_details.get("DomainSettings").get("AmazonQSettings") is not None
            and domain_details.get("DomainSettings")
            .get("AmazonQSettings")
            .get("Status")
            == "ENABLED"
        )
