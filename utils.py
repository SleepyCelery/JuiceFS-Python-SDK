import os
import re
import json
import time


def jfs2system(relative_path):
    """
    Convert a path in JuiceFS to a path in the system.
    :param relative_path: a path in JuiceFS
    :return: a path in the system
    """
    mount_point = os.getenv("JFS_MOUNTPOINT")
    relative_path = os.path.normpath(relative_path)
    while relative_path.startswith("/"):
        relative_path = relative_path[1:]
    result_path = os.path.realpath(os.path.join(mount_point, relative_path)).rstrip(os.sep)
    if is_child_dir(mount_point, result_path):
        return result_path
    return mount_point


def is_child_dir(parent_dir, child_dir):
    """
    Check if a directory is a child directory of another directory.
    :param parent_dir:
    :param child_dir:
    :return:
    """
    parent_dir = os.path.normpath(parent_dir)
    child_dir = os.path.normpath(child_dir)
    if not parent_dir.endswith(os.sep):
        parent_dir += os.sep
    if not child_dir.endswith(os.sep):
        child_dir += os.sep
    return child_dir.startswith(parent_dir)


def parse_quota_table(quota_table):
    """
    Parse JuiceFS quota table.
    :param quota_table: str
    :return: dict
    """
    pattern = re.compile(r'\|(.*?)\|(.*?)\|(.*?)\|(.*?)\|(.*?)\|(.*?)\|(.*?)\|')
    rows = re.findall(pattern, quota_table)
    header = list(rows[0])
    header_list = []
    for i in range(len(header)):
        header_list.append(header[i].strip())
    quota_details = rows[1:]
    quota_dict = {}
    for quota_detail in quota_details:
        quota_dict[quota_detail[0].strip()] = dict(zip(header_list, map(lambda a: a.strip(), quota_detail)))
    return quota_dict


def get_json_from_output(output):
    """
    Get json from output.
    :param output:
    :return: dict
    """
    output = output[output.find('{'):output.rfind('}') + 1]
    return json.loads(output)


# 获取某一个目录下的所有文件和文件夹的名称、大小、修改日期、权限等信息，返回一个字典
def list_dir_details(path):
    """
    List directory details.
    :param path:
    :return: detail dict
    """
    result = {}
    for obj in os.listdir(path):
        if os.path.isdir(os.path.join(path, obj)):
            result[obj] = {'type': 'dir',
                           'mtime': time.strftime("%Y-%m-%d %H:%M:%S",
                                                  time.localtime(os.path.getmtime(os.path.join(path, obj))))}
        else:
            result[obj] = {'type': 'file', 'size': os.path.getsize(os.path.join(path, obj)),
                           'mtime': time.strftime("%Y-%m-%d %H:%M:%S",
                                                  time.localtime(os.path.getmtime(os.path.join(path, obj))))}
    return result
