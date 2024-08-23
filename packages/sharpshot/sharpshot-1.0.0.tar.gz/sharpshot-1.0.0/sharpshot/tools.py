#!/usr/bin/python
# encoding=utf-8

"""
@Author  :  Lijiawei
@Date    :  2024/7/26 11:01 AM
@Desc    :  tools line.
"""
import argparse
import base64

import requests
from urllib.parse import urlparse
from pprint import pprint


def get_branch_name(pr, access_token):
    """
    get branch name according to pr
    :param access_token: gitlab access token
    :param pr:
    :return:
    """
    parsed_url = urlparse(pr.rstrip('/'))
    hostname = parsed_url.hostname
    path_parts = parsed_url.path.split('/')
    project_path = '%2F'.join(path_parts[1:3])
    merge_request_id = path_parts[-1]
    repository_url = f"https://{hostname}/{project_path.replace('%2F', '/')}.git"

    base_url = f"https://{hostname}/api/v4/projects/{project_path}/merge_requests/{merge_request_id}"
    print(base_url)
    headers = {"PRIVATE-TOKEN": access_token}

    response = requests.get(base_url, headers=headers)
    data = response.json()

    target_branch = data.get("target_branch")
    source_branch = data.get("source_branch")
    state = data.get("state")

    print("Target Branch:", target_branch)
    print("Source Branch:", source_branch)
    print("Repository URL:", repository_url)
    print("State:", state)

    return {"repository_url": repository_url, "target_branch": target_branch, "source_branch": source_branch,
            "state": state}


def cli_env_new(*args, **kwargs):
    """
    the parameters currently used are as follows：

    device, platform, wda, init, duration, whitelist, widget, package, filename, times, name, is_all,
    record, proxy, cases, username, password, phone_numbers_api, save_mark_api, data, phone

    :param kwargs: additional parameters
    :return: param dict
    """
    parser = argparse.ArgumentParser(description="manual to this script.")
    args, unknown = parser.parse_known_args()
    # make sure that all the parameters are stored in a dictionary
    cli_result = vars(args)

    # handle undefined parameters
    for arg in unknown:
        arg_name, arg_value = arg.split("=")
        cli_result[arg_name.lstrip("-")] = arg_value

    # handle the undefined parameters passed in
    for key, value in kwargs.items():
        cli_result[key] = value

    pprint(cli_result)
    return cli_result


def encryption(value):
    bytes_url = value.encode("utf-8")
    str_url = base64.b64encode(bytes_url)
    return str_url


def decryption(value):
    str_url = base64.b64decode(value).decode("utf-8")
    return str_url
