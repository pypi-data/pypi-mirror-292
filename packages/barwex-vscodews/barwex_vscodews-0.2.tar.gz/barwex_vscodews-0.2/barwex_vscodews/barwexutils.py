import os, shutil, json
from os.path import *
from typing import Sequence

USER_HOME_DIR = os.environ["HOME"]
USER_CONF_DIR = join(USER_HOME_DIR, ".config")
USER_DESKTOP_DIR = join(USER_HOME_DIR, "Desktop")


def mkdir_as_needed(*ps: Sequence[str], recursive=False):
    p = join(*ps)
    if not exists(p):
        if recursive:
            os.makedirs(p)
        else:
            os.mkdir(p)
    return p


def get_barwex_data_dir():
    return mkdir_as_needed(USER_CONF_DIR, "barwex")


def get_barwex_app_data_dir(app: str):
    bxdir = get_barwex_data_dir()
    return mkdir_as_needed(bxdir, app)


class IO:
    json_load = json.load
    json_loads = json.loads
    json_dump = json.dump
    json_dumps = json.dumps

    @staticmethod
    def read_json(src_file: str):
        with open(src_file, "r") as f:
            return json.load(f)

    @staticmethod
    def write_json(data, dest_file: str, indent=2):
        with open(dest_file, "w") as f:
            json.dump(data, f, indent=indent, ensure_ascii=False)

    @staticmethod
    def read_text(src_file: str):
        """读取一个文本文件为字符串"""
        with open(src_file, "r") as f:
            return f.read()

    @staticmethod
    def write_text(text: str, dest_file: str, mode=None):
        """将一个字符串写入文本文件，覆盖模式，支持设置文件权限"""
        with open(dest_file, "w") as f:
            f.write(text)

        if mode:
            from xuse.more.shell import run

            run(f"chmod {mode} {dest_file}")


class SUBPROCESS:
    @staticmethod
    def check_output(cmd: str, exit=True):
        import subprocess

        try:
            output = subprocess.check_output(cmd, shell=True, stderr=subprocess.STDOUT)
            return output.decode().strip()
        except subprocess.CalledProcessError as e:
            if exit:
                raise e
            else:
                return e.output.decode().strip()
