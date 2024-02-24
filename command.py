#TODO： 添加文件和文件夹克隆命令
import subprocess
import os
import platform
from .utils import jfs2system, parse_quota_table, get_json_from_output, list_dir_details
import shutil


def check_jfs_installation():
    """
    Check if JuiceFS is installed.
    :return: True if JuiceFS is installed, False otherwise.
    """
    p = subprocess.Popen(['juicefs', '--version'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    p.wait()
    stdout, _ = p.communicate()
    if 'juicefs version' in stdout.decode():
        return True
    else:
        return False


def get_jfs_config():
    """
    Get JuiceFS config.
    :return: JuiceFS Config Dict.
    """
    p = subprocess.Popen(['juicefs', 'config', os.getenv("JFS_METAURL")], stdout=subprocess.PIPE,
                         stderr=subprocess.PIPE)
    p.wait()
    stdout, _ = p.communicate()
    return get_json_from_output(stdout.decode())


def enable_dir_stats():
    """
    Enable JuiceFS directory stats.
    :return: JuiceFS Config Dict.
    """
    p = subprocess.Popen(['juicefs', 'config', os.getenv("JFS_METAURL"), '--dir-stats'], stdout=subprocess.PIPE,
                         stderr=subprocess.PIPE)
    p.wait()
    jfs_config = get_jfs_config()
    if jfs_config['DirStats']:
        return True
    return False


def mount_jfs():
    """
    Mount JuiceFS.
    :return: Mount point.
    """
    mount_dir = os.getenv("JFS_MOUNTPOINT")
    metaurl = os.getenv("JFS_METAURL")
    if platform.system() == "Linux":
        p = subprocess.Popen(["juicefs", "mount", "-o", "allow_other,writeback_cache", "-d", metaurl, mount_dir],
                             stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    elif platform.system() == "Darwin":
        p = subprocess.Popen(["juicefs", "mount", metaurl, mount_dir, "-d"], stdout=subprocess.PIPE,
                             stderr=subprocess.PIPE)
    else:
        raise RuntimeError("Unsupported platform")
    p.wait()
    stdout, stderr = p.communicate()
    # print('stdout:', stdout.decode())
    # print('stderr:', stderr.decode())
    if 'ready' in stderr.decode():
        return os.path.abspath(mount_dir)
    else:
        raise RuntimeError(f"JuiceFS mount failed: {stderr.decode()}")


def umount_jfs(need_mounted=False):
    """
    Unmount JuiceFS.
    :param need_mounted:
    :return: Mount point.
    """
    mount_dir = os.getenv('JFS_MOUNTPOINT')
    p = subprocess.Popen(['juicefs', 'umount', mount_dir], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    p.wait()
    stdout, stderr = p.communicate()
    # print('stdout:', stdout.decode())
    # print('stderr:', stderr.decode())
    if stderr.decode():
        if need_mounted:
            raise RuntimeError(f"JuiceFS umount failed: {stderr.decode()}")
    return os.path.abspath(mount_dir)


def set_quota(path, quota):
    """
    Set quota for a directory.
    :param path: relative path in JuiceFS
    :param quota: quota in GigaBytes
    :return:
    """
    p = subprocess.Popen(
        ['juicefs', 'quota', 'set', os.getenv("JFS_METAURL"), '--path', path, '--capacity', str(quota)],
        stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    p.wait()
    stdout, stderr = p.communicate()
    if stdout.decode():
        return parse_quota_table(stdout.decode())
    # print('stdout:', stdout.decode())
    # print('stderr:', stderr.decode())
    if stderr.decode():
        raise RuntimeError(f"JuiceFS set quota failed: {stderr.decode()}")


def get_quota(path):
    """
    Get quota info for specific directory
    :param path:
    :return: quota dict
    """
    p = subprocess.Popen(
        ['juicefs', 'quota', 'get', os.getenv("JFS_METAURL"), '--path', path],
        stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    p.wait()
    stdout, stderr = p.communicate()
    if stdout.decode():
        return parse_quota_table(stdout.decode())
    # print('stdout:', stdout.decode())
    # print('stderr:', stderr.decode())
    if stderr.decode():
        raise RuntimeError(f"JuiceFS get quota failed: {stderr.decode()}")


def delete_quota(path):
    """
    Delete quota info for specific directory
    :param path:
    :return: path
    """
    p = subprocess.Popen(
        ['juicefs', 'quota', 'delete', os.getenv("JFS_METAURL"), '--path', path],
        stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    p.wait()
    stdout, stderr = p.communicate()
    # print('stdout:', stdout.decode())
    # print('stderr:', stderr.decode())
    if "FATAL" in stderr.decode():
        if "FATAL" in stderr.decode():
            raise RuntimeError(f"JuiceFS delete quota failed: {stderr.decode()}")


def get_all_quota():
    """
    Get all quota info in JuiceFS
    :return: quota dict
    """
    p = subprocess.Popen(
        ['juicefs', 'quota', 'ls', os.getenv("JFS_METAURL")],
        stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    p.wait()
    stdout, stderr = p.communicate()
    if stdout.decode():
        return parse_quota_table(stdout.decode())
    # print('stdout:', stdout.decode())
    # print('stderr:', stderr.decode())
    if stderr.decode():
        raise RuntimeError(f"JuiceFS get quota failed: {stderr.decode()}")


def check_quota(path, repair=False):
    """
    Check JuiceFS quota for specific directory
    :param path: relative path in JuiceFS
    :param repair: Boolean
    :return: quota_dict
    """
    if repair:
        p = subprocess.Popen(
            ['juicefs', 'quota', 'check', os.getenv("JFS_METAURL"), '--path', path, '--repair'],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    else:
        p = subprocess.Popen(
            ['juicefs', 'quota', 'check', os.getenv("JFS_METAURL"), '--path', path],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    p.wait()
    stdout, stderr = p.communicate()
    # print('stdout:', stdout.decode())
    # print('stderr:', stderr.decode())
    if parse_quota_table(stdout.decode()):
        return True
    if 'FATAL' in stderr.decode():
        raise RuntimeError(f"JuiceFS check quota failed: {stderr.decode()}")


def lsdir(path, detail=False):
    """
    List files in a directory.
    :param path: relative path in JuiceFS
    :param detail:
    :return:
    """
    path = jfs2system(path)
    if detail:
        return list_dir_details(path)
    return os.listdir(path)


def mkdir(path):
    path = jfs2system(path)
    os.makedirs(path, exist_ok=True)


# 递归强制删除文件夹
def rmdir(path):
    path = jfs2system(path)
    try:
        shutil.rmtree(path)
    except FileNotFoundError:
        pass


def rmfile(path):
    path = jfs2system(path)
    try:
        os.remove(path)
    except FileNotFoundError:
        pass
