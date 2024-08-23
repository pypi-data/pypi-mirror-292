#!/usr/bin/python
# encoding=utf-8

"""
@Author  :  Lijiawei
@Date    :  2024/7/26 4:28 PM
@Desc    :  report line.
"""
import os
from jinja2 import Environment
from jinja2 import FileSystemLoader
from pathlib import Path

CONCURRENT_HTML_TPL = "analyze_template.html"
CUSTOM_STATIC_DIR = os.path.dirname(__file__)


def gen_summary(impacted_api_list=None, data=None, pr="", warn="", report_path=None, report_name="analyze.html"):
    """
    Build summary test report
    :param warn:
    :param pr:
    :param impacted_api_list:
    :param data: test data
    :param report_path: report path
    :param report_name: report name
    :return:
    """
    if impacted_api_list is None:
        impacted_api_list = []
    if data is None:
        data = []
    env = Environment(loader=FileSystemLoader(CUSTOM_STATIC_DIR), trim_blocks=True)
    html = env.get_template(CONCURRENT_HTML_TPL, CUSTOM_STATIC_DIR).render(
        impacted_api=impacted_api_list, summary=data, pr=pr, warn=warn
    )
    path = Path(report_path).expanduser().resolve(strict=False)
    output_file = os.path.join(path, report_name)
    if not os.path.exists(path):
        os.makedirs(path)
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(html)
    print(output_file)
