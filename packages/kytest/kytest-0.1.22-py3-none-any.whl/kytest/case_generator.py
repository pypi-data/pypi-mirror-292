"""
@Author: kang.yang
@Date: 2024/8/24 09:24
"""
import sys
import os
import requests
from urllib.parse import urljoin


def generate(host: str, project: str, controller: str):
    """
    生成用例
    @param host: tms服务域名
    @param project: tms服务导入的项目
    @param controller: 指定的controller，不指定则生成全部
    @return:
    """
    def create_folder(path):
        os.makedirs(path)
        msg = f"created folder: {path}"
        print(msg)

    def create_file(path, file_content=""):
        with open(path, "w", encoding="utf-8") as f:
            f.write(file_content)
        msg = f"created file: {path}"
        print(msg)

    if not host:
        print('host不能为空')
        sys.exit()
    if not project:
        print('project不能为空')
        sys.exit()

    url = urljoin(host, '/api/api_test/api/get_apis_by_project_and_controller')
    query = {
        "project_name": project,
        "controller": controller
    }
    res = requests.get(url, params=query).json()
    if res["code"] == 0:
        api_list = res["data"]
        # 生成用例
        for api in api_list:
            controller = api["controller"]
            if not os.path.exists(controller):
                create_folder(controller)
            test_name = api["test_name"]
            print(f"生成用例: {test_name}")
            test_script = api["test_script"]
            create_file(os.path.join(controller, test_name), test_script)
    else:
        print("用例生成异常")
        print(res)
        sys.exit()
