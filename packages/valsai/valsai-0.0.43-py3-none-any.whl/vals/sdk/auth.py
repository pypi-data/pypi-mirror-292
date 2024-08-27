import json
import os
import sys
import time

import boto3
import click

PRL_PATH = os.path.expanduser("~/.prl")
CREDS_PATH = os.path.join(PRL_PATH, "creds.json")
VALS_ENV = os.getenv("VALS_ENV")

DEFAULT_REGION = "us-east-1"

global_api_key = None
global_in_eu = None
global_auth_dict = {}


def configure_credentials(api_key: str, in_eu: bool = False):
    """
    Configure the Vals API Key to be used with requests.
    This will take precedence over any credentials set in environment variables, or with vals login.
    """
    global global_api_key, global_in_eu
    global_api_key = api_key.strip()
    global_in_eu = in_eu


def _get_client_id(in_europe: bool, using_api_key: bool):
    if using_api_key:
        if in_europe:
            return "6cv1hchrihac7dtsmjac1dukn6"
        elif VALS_ENV in ["LOCAL", "DEV"]:
            return "7scu563gabte768gtml5v5uids"
        else:
            # Normal Prod user pool
            return "6t1s1a2g43ggqkn8timajdl0nn"
    else:
        if in_europe:
            return "4asi3qr1jga1l1kvc6cqpqdsad"
        elif VALS_ENV in ["LOCAL", "DEV"]:
            return "59blf1klr2lejsd3uanpk3b0r4"
        else:
            # Normal Prod user pool
            return "7r5tn1kic6i262mv86g6etn3oj"


def _get_region():
    global global_in_eu
    if global_in_eu is not None:
        return "eu-north-1" if global_in_eu else "us-east-1"

    if "VALS_REGION" in os.environ:
        vals_region = os.environ["VALS_REGION"].lower()
        if vals_region not in ["europe", "us"]:
            raise ValueError(
                f"Invalid region: {vals_region}. Must be 'europe' or 'us'."
            )

        return "eu-north-1" if vals_region == "europe" else "us-east-1"

    if os.path.exists(CREDS_PATH):
        with open(CREDS_PATH, "r") as f:
            auth_dict = json.load(f)

        if "region" in auth_dict:
            return auth_dict["region"]

    return DEFAULT_REGION


def _get_auth_token():
    global global_api_key, global_in_eu, global_auth_dict

    region_name = _get_region()

    client = boto3.client("cognito-idp", region_name=region_name)

    if global_api_key is not None:
        refresh_token = global_api_key
        client_id = _get_client_id(region_name == "eu-north-1", True)
        method = "sdk"
        auth_dict = global_auth_dict

        # API Key is specified in environment
    elif "VALS_API_KEY" in os.environ:
        refresh_token = os.environ["VALS_API_KEY"]
        client_id = _get_client_id(region_name == "eu-north-1", True)
        auth_dict = global_auth_dict
        method = "env"

    # We're using the `vals login` workflow.
    else:
        if not os.path.exists(CREDS_PATH):
            auth_dict = {}
        else:
            with open(CREDS_PATH, "r") as f:
                auth_dict = json.load(f)

        if "refresh_token" not in auth_dict:
            click.echo(
                "Not authenticated. Run the command: vals login or set the 'VALS_API_KEY' environment variable."
            )
            sys.exit()
        refresh_token = auth_dict["refresh_token"]
        client_id = auth_dict["client_id"]
        method = "cli"

    if "access_expiry" not in auth_dict or time.time() > auth_dict["access_expiry"]:
        # Generate new access token from refresh token
        try:
            response = client.initiate_auth(
                AuthFlow="REFRESH_TOKEN_AUTH",
                AuthParameters={"REFRESH_TOKEN": refresh_token},
                ClientId=client_id,
            )
        except Exception as e:
            click.echo(
                "Either your session has expired or an invalid API Key was provided. Run prl login, or update your VALS_API_KEY environment variable."
            )
            sys.exit()

        auth_dict = {
            **auth_dict,
            "access_token": response["AuthenticationResult"]["AccessToken"],
            "id_token": response["AuthenticationResult"]["IdToken"],
            "access_expiry": int(
                time.time() + response["AuthenticationResult"]["ExpiresIn"] - 10
            ),
        }

        if method == "cli":
            # If using CLI, store the new access token in the FS
            auth_json = json.dumps(auth_dict, indent="\t")

            if not os.path.exists(PRL_PATH):
                os.makedirs(PRL_PATH, mode=0o770)

            # Store the new access token
            with open(CREDS_PATH, "w") as f:
                os.chmod(CREDS_PATH, mode=0o770)
                f.write(auth_json)
        else:
            global_auth_dict = auth_dict

    return auth_dict["access_token"]
