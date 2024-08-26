#!/usr/bin/env python3
import datetime
import os
import pathlib
import re
import subprocess
import sys
import shlex
import shutil
from typing import List

from .utils import cprint, pad_string


class OpenerError(Exception):
    """Exception raised when command fails"""

    def __init__(self, error, message="ERROR: Failed to run"):
        self.error = error
        self.message = message
        super().__init__(self.message)

    def __str__(self):
        return f"{self.message} {self.error}"


def browse_base(user):
    """
    Browse a user's base directory with their desired program
    """
    base_dir = user.settings["base_dir"]
    opener = shlex.split(user.settings["file_manager"])
    if opener is None:
        raise OpenerError(user.files["conf_file"])
    opener.append(base_dir)
    try:
        open_process(opener)
    except OpenerError as err:
        cprint("red", err, out_file=sys.stderr)
        return 1


def check_mimetype(file: str):
    cmd = shlex.split(f"file --mime-type \"{file}\" -bL")
    result = return_cmd(cmd)
    return result["stdout"].strip("\n")


def check_zipped_dirs(dirs: List[pathlib.Path], zip_cmd: str, first_run: bool = True):
    recheck_flag = False
    for dir in dirs:
        if not dir.is_absolute():
            cprint("red", f"ERROR: Cannot fix zip: '{dir}.cbz'")
            continue
        parent = dir.parent.as_posix()
        cbz = pathlib.Path(dir.as_posix() + ".cbz")
        if not cbz.is_file():
            continue
        result = check_mimetype(cbz.as_posix())
        if result == "application/zip":
            continue
        cprint("yellow", f"Remaking broken zip '{cbz}'")
        if not recheck_flag:
            recheck_flag = True
        cbz.unlink()
        run_cmd([zip_cmd, parent, dir.as_posix()])
    if recheck_flag and first_run:
        check_zipped_dirs(dirs, zip_cmd, False)



def clean_dir_name(dir: pathlib.Path):
    pattern = r"([0-9]+\.?[0-9]*)"
    match = re.search(pattern, dir.name)
    if not match:
        return None
    new_name = pad_string(match.group(1))
    new = dir.parent.as_posix() + "/" + new_name
    return dir.rename(new)



def create_directory(base_dir, dir):
    """
    Create the given list of directories in base_dir
    """
    dir_path = pathlib.Path(base_dir, dir)
    if dir_path.is_dir():
        return True
    elif dir_path.is_file():
        return False
    dir_path.mkdir(parents=True)
    return True


def get_dirs(path: pathlib.Path):
    # list all directories under the given path
    directories = [
        entry
        for entry in path.glob("*")
        if entry.is_dir()
    ]
    return directories


def get_files(path: pathlib.Path):
    # list all files
    files = [
        file
        for file in path.glob("*")
        if file.is_file()
    ]
    return files


def get_new_count(dest, latest):
    path = pathlib.Path(dest)
    result = 0
    for file in get_files(path):
        try:
            name = file.name.split(".")[0]
            count = float(name)
        except (ValueError, IndexError):
            continue
        if count > latest:
            result += 1
    return result


def move_cbz(dest, path: pathlib.Path):
    target_dir = pathlib.Path(dest, path.name)
    for file in os.listdir(path):
        if not file.endswith("cbz"):
            continue
        dest_file = pathlib.Path(target_dir / file)
        if dest_file.exists() and dest_file.is_file():
            dest_file.unlink()
        elif dest_file.is_dir():
            raise OSError(f"Destination is a directory {dest_file}")
        shutil.move(file, target_dir)


def move_to_raw(base_dir, path: pathlib.Path):
    move_to_x(base_dir, "raw_manga", path)


def move_to_x(base_dir, x: str, path: pathlib.Path):
    target_dir = pathlib.Path(base_dir, x, path.name)
    dirs = get_dirs(path)
    for dir in dirs:
        target_path = target_dir / dir.name
        try:
            shutil.move(dir, target_path)
        except shutil.Error:
            cprint("red", f"ERROR: Cannot move '{dir}' to '{target_path}'")


def open_process(opener, out=subprocess.DEVNULL, err=subprocess.STDOUT):
    """Open a program with the given opener list"""
    try:
        subprocess.Popen(opener, stdout=out, stderr=err)
    except (subprocess.CalledProcessError, FileNotFoundError):
        raise OpenerError(opener)


def remove_directory(path: pathlib.Path):
    try:
        shutil.rmtree(path)
    except Exception as e:
        cprint("red", f"Error deleting directory {path}: {e}", out_file=sys.stderr)


def return_cmd(cmd):
    """
    Run a command and return the the output as a dict
    """
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = proc.communicate()
    return {"stdout": stdout.decode("utf-8"), "stderr": stderr.decode("utf-8")}


def re_zip(user, args):
    if args.path is None:
        path = pathlib.Path().absolute()
    else:
        path = pathlib.Path(args.path)
    dirs = [dir for dir in get_dirs(path) if dir is not None]
    cprint("green", f"(Re)zipping '{path}'")
    zip_dirs(dirs, user.settings["zip_cmd"])
    if args.dir is None:
        base = user.settings["base_dir"]
    else:
        base = args.dir
    if args.move:
        move_cbz(base, path)


def run_cmd(cmd):
    subprocess.run(cmd)


def write_recent_updates(user, items):
    update_file = pathlib.Path(user.files["updates_file"])
    if update_file.is_file():
        update_file.replace(user.files["updates_bak_file"])
    update_file.touch()
    with open(update_file, "w") as file:
        file.write(f"Recent updates to library as of {datetime.datetime.now()}.\n")
        for item in items:
            title = item["title"]
            new_count = item["new_count"]
            file.write(
                f"{title} had {new_count} new chapter(s).\n"
            )



def zip_dirs(dirs: List[pathlib.Path], zip_cmd: str):
    # compress each directory using user cmd
    processes = []
    for dir in dirs:
        if not dir.is_absolute():
            cprint("red", f"ERROR: Cannot zip dir: '{dir}'")
            continue
        process = subprocess.Popen(
            [
                zip_cmd,
                dir.parent.as_posix(),
                dir.as_posix(),
                # "tar",
                # "--sort=name",
                # "-C",
                # dir_path,
                # "-caf",
                # f"{d}.zip",
                # chapter,
            ]
        )
        processes.append(process)
    for process in processes:
        process.communicate()
