import unittest
from . import command
import os
from . import utils


class CommandTestCase(unittest.TestCase):
    def test_010_check_jfs_installation(self):
        self.assertTrue(command.check_jfs_installation())

    def test_011_get_jfs_config(self):
        self.assertEqual(command.get_jfs_config(), {"Name": "bdapuserfiles",
                                                    "UUID": "5be99d4e-bc5e-4a2e-9093-f09b19ecff87",
                                                    "Storage": "minio",
                                                    "Bucket": "http://192.168.5.98:9000/bdapuserfiles",
                                                    "AccessKey": "bdap",
                                                    "SecretKey": "removed",
                                                    "BlockSize": 4096,
                                                    "Compression": "none",
                                                    "Capacity": 10200547328000,
                                                    "EncryptAlgo": "aes256gcm-rsa",
                                                    "KeyEncrypted": True,
                                                    "TrashDays": 1,
                                                    "MetaVersion": 1,
                                                    "MinClientVersion": "1.1.0-A",
                                                    "DirStats": True})

    def test_012_enable_dir_stats(self):
        self.assertTrue(command.enable_dir_stats())

    def test_02_mount_jfs(self):
        self.assertEqual(command.mount_jfs(), os.getenv("JFS_MOUNTPOINT"))

    def test_030_mkdir(self):
        command.mkdir("/tiny_experiments")
        self.assertTrue(os.path.exists(utils.jfs2system("/tiny_experiments")))

    def test_031_set_quota(self):
        set_result = command.set_quota('/tiny_experiments', 100)
        self.assertIn('/tiny_experiments', set_result.keys())
        self.assertEqual(set_result['/tiny_experiments']['Size'], '100 GiB')

    def test_032_get_quota(self):
        get_result = command.get_quota('/tiny_experiments')
        self.assertIn('/tiny_experiments', get_result.keys())
        self.assertEqual(get_result['/tiny_experiments']['Size'], '100 GiB')

    def test_033_get_all_quota(self):
        all_quota = command.get_all_quota()
        self.assertIn('/tiny_experiments', all_quota.keys())

    def test_034_check_quota(self):
        try:
            self.assertTrue(command.check_quota('/tiny_experiments'))
        except RuntimeError:
            print(command.check_quota('/tiny_experiments', repair=True))

    def test_035_delete_quota(self):
        command.delete_quota('/tiny_experiments')
        self.assertNotIn('/tiny_experiments', command.get_all_quota().keys())

    def test_036_create_file(self):
        with open(utils.jfs2system("/tiny_experiments/tiny_experiments.txt"), "w") as f:
            f.write("Hello World!")
        self.assertTrue(os.path.exists(utils.jfs2system("/tiny_experiments/tiny_experiments.txt")))

    def test_040_lsdir(self):
        self.assertEqual(command.lsdir("/"), os.listdir(utils.jfs2system("/")))
        self.assertEqual(command.lsdir("/tiny_experiments"),
                         os.listdir(utils.jfs2system('/tiny_experiments')))
        self.assertEqual(command.lsdir("/tiny_experiments/"),
                         os.listdir(utils.jfs2system('/tiny_experiments/')))
        print(command.lsdir("/tiny_experiments", detail=True))

    def test_042_rmfile(self):
        self.assertTrue(os.path.exists(utils.jfs2system("/tiny_experiments/tiny_experiments.txt")))
        command.rmfile("/tiny_experiments/tiny_experiments.txt")
        self.assertFalse(os.path.exists(utils.jfs2system("/tiny_experiments/tiny_experiments.txt")))

    def test_043_rmdir(self):
        command.rmdir("/tiny_experiments")
        self.assertFalse(os.path.exists(utils.jfs2system("/tiny_experiments")))

    def test_05_umount_jfs(self):
        self.assertEqual(command.umount_jfs(need_mounted=False), os.getenv("JFS_MOUNTPOINT"))


class UtilsTestCase(unittest.TestCase):
    def test_01_jfs_path(self):
        self.assertEqual(utils.jfs2system("/"), os.path.normpath(os.getenv("JFS_MOUNTPOINT")))
        self.assertEqual(utils.jfs2system("/tiny_experiments"), os.path.normpath(os.path.join(os.getenv("JFS_MOUNTPOINT"), "tiny_experiments")))
        self.assertEqual(utils.jfs2system("/tiny_experiments/"),
                         os.path.normpath(os.path.join(os.getenv("JFS_MOUNTPOINT"), "tiny_experiments")))
        self.assertEqual(utils.jfs2system("/../../../../../.."), os.path.normpath(os.getenv("JFS_MOUNTPOINT")))

    def test_02_is_child_dir(self):
        self.assertTrue(utils.is_child_dir("/tiny_experiments", "/tiny_experiments/tiny_experiments"))
        self.assertTrue(utils.is_child_dir("/tiny_experiments", "/tiny_experiments/tiny_experiments/"))
        self.assertTrue(utils.is_child_dir("/tiny_experiments", "/tiny_experiments"))
        self.assertFalse(utils.is_child_dir("/tiny_experiments", "/tiny_experiments/.."))

    def test_03_parse_quota_table(self):
        table_string = """+-----------+---------+--------+------+-----------+-------+-------+
                        |    Path   |   Size  |  Used  | Use% |   Inodes  | IUsed | IUse% |
                        +-----------+---------+--------+------+-----------+-------+-------+
                        | /chaoyihu | 100 GiB | 66 MiB |   0% | unlimited |     7 |       |
                        +-----------+---------+--------+------+-----------+-------+-------+"""
        self.assertEqual(utils.parse_quota_table(table_string), {
            '/chaoyihu': {'Path': '/chaoyihu', 'Size': '100 GiB', 'Used': '66 MiB', 'Use%': '0%', 'Inodes': 'unlimited',
                          'IUsed': '7', 'IUse%': ''}})

    def test_04_get_json_from_output(self):
        output = """2023/09/21 17:06:51.573199 juicefs[26917] <INFO>: Meta address: postgres://bdap:****@192.168.5.98:5432/bdap [interface.go:497]
                    2023/09/21 17:06:51.614393 juicefs[26917] <WARNING>: The latency to database is too high: 41.016125ms [sql.go:240]
                    {
                      "Name": "bdapuserfiles",
                      "UUID": "5be99d4e-bc5e-4a2e-9093-f09b19ecff87",
                      "Storage": "minio",
                      "Bucket": "http://192.168.5.98:9000/bdapuserfiles",
                      "AccessKey": "bdap",
                      "SecretKey": "removed",
                      "BlockSize": 4096,
                      "Compression": "none",
                      "Capacity": 10200547328000,
                      "EncryptAlgo": "aes256gcm-rsa",
                      "KeyEncrypted": true,
                      "TrashDays": 1,
                      "MetaVersion": 1,
                      "MinClientVersion": "1.1.0-A",
                      "DirStats": true
                    }"""
        self.assertEqual(utils.get_json_from_output(output), {"Name": "bdapuserfiles",
                                                              "UUID": "5be99d4e-bc5e-4a2e-9093-f09b19ecff87",
                                                              "Storage": "minio",
                                                              "Bucket": "http://192.168.5.98:9000/bdapuserfiles",
                                                              "AccessKey": "bdap",
                                                              "SecretKey": "removed",
                                                              "BlockSize": 4096,
                                                              "Compression": "none",
                                                              "Capacity": 10200547328000,
                                                              "EncryptAlgo": "aes256gcm-rsa",
                                                              "KeyEncrypted": True,
                                                              "TrashDays": 1,
                                                              "MetaVersion": 1,
                                                              "MinClientVersion": "1.1.0-A",
                                                              "DirStats": True})

    def test_05_list_dir_details(self):
        self.assertTrue(utils.list_dir_details("/Users/sleepycelery/Documents"))


if __name__ == '__main__':
    unittest.main()
