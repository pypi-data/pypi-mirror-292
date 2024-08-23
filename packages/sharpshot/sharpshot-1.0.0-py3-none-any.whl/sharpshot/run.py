#!/usr/bin/python
# encoding=utf-8

"""
@Author  :  Lijiawei
@Date    :  2024/7/29 2:36 PM
@Desc    :  run line.
"""
from sharpshot.core.analyze import JCCI
from sharpshot.report import gen_summary
from sharpshot.tools import get_branch_name, cli_env_new

cli_param = cli_env_new()


def sharp_shot():
    """
    sharp_shot
    :return:
    """
    pr = cli_param.get("pr")
    access_token = cli_param.get("access_token")
    info = get_branch_name(pr, access_token)

    if info.get("state") != "opened":
        print("The merge request is not opened.")
        gen_summary(pr=pr, warn="Warning: The merge request is not opened.", report_path="report")
        exit(0)

    branch_analyze = JCCI(info.get("repository_url"), cli_param.get("username"))
    res = branch_analyze.analyze_two_branch(info.get("source_branch"), info.get("target_branch"))
    impacted_api_list = [item for item in res.get("impacted_api_list") if item != 'None']
    gen_summary(impacted_api_list, res, pr, report_path="report")


if __name__ == '__main__':
    sharp_shot()
