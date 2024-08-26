import os
from os.path import abspath, dirname, exists, join, splitext
from argparse import ArgumentParser
from .bashrcio import BashrcIO

ROOT_DIR = abspath(dirname(__file__))


# 列出所有可用的 bashrc 文件
def list_all():
    arr = os.listdir(join(ROOT_DIR, "data"))
    return [x[:-3] for x in arr if x.endswith(".sh")]


def exec_init(args, other):
    bashrc_io = BashrcIO(ROOT_DIR)
    if not bashrc_io.is_initialized():
        bashrc_io.initialize()
    print("barwex-bashrc has already been initialized.")


def exec_add(args, other):
    bashrc_io = BashrcIO(ROOT_DIR)
    bashrc_io.exit_if_not_initialized()

    ks = list_all()
    if len(other) == 0 or other[0] in ("-h", "--help"):
        s = ", ".join(ks)
        print(f"All available files: {s}")
        return

    k = other[0]
    if k not in ks:
        print(f"File '{k}' not found.")
        return

    bashrc_io.add(k)


def exec_remove(args, other):
    bashrc_io = BashrcIO(ROOT_DIR)
    bashrc_io.exit_if_not_initialized()

    text = bashrc_io.fulltext()
    ks = [i for i in list_all() if f"#:{i}:#" in text]
    if len(other) == 0 or other[0] in ("-h", "--help"):
        print(f"All installed files: {', '.join(ks)}")
        return

    k = other[0]
    if k not in ks:
        print(f"File '{k}' not installed.")
        return

    bashrc_io.remove(k)


def exec_uninstall(args, other):
    bashrc_io = BashrcIO(ROOT_DIR)
    bashrc_io.exit_if_not_initialized()
    bashrc_io.uninstall()


def main():
    parser = ArgumentParser()
    subparsers = parser.add_subparsers()

    subparser = subparsers.add_parser("init", aliases=["install"], help="初始化")
    subparser.set_defaults(func=exec_init)

    subparser = subparsers.add_parser("add", help="添加一个文件")
    subparser.set_defaults(func=exec_add)

    subparser = subparsers.add_parser("remove", help="移除一个文件")
    subparser.set_defaults(func=exec_remove)

    subparser = subparsers.add_parser("uninstall", help="卸载")
    subparser.set_defaults(func=exec_uninstall)

    args, other = parser.parse_known_args()
    if not hasattr(args, "func"):
        parser.print_help()
        return
    try:
        args.func(args, other)
    except KeyboardInterrupt:
        print()
