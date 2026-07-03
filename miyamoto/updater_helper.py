#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Pyamoto updater helper — spawned by main app to replace old install with
# downloaded update zip.  Handles rename-then-replace, ad-hoc codesign, and
# re-launch.  Runs via sys.executable --update-helper (frozen) or
# python miyamoto/updater_helper.py (source tree).

import argparse
import os
import platform
import shutil
import subprocess
import sys
import time
import zipfile


def run_helper():
    parser = argparse.ArgumentParser()
    parser.add_argument('--zip', required=True)
    parser.add_argument('--install-dir', required=True)
    parser.add_argument('--exe', default='Pyamoto')
    parser.add_argument('--platform', default='darwin')
    parser.add_argument('--codesign', action='store_true')
    parser.add_argument('--wait-pid', type=int, default=None)
    args = parser.parse_args()

    zip_path = args.zip
    install_dir = args.install_dir
    exe_name = args.exe
    platform_name = args.platform

    if args.wait_pid:
        _wait_for_exit(args.wait_pid)

    old_dir = install_dir + '.old'

    if os.path.exists(old_dir):
        shutil.rmtree(old_dir, ignore_errors=True)

    if os.path.exists(install_dir):
        os.rename(install_dir, old_dir)

    try:
        _extract_zip(zip_path, install_dir)

        if args.codesign and platform_name == 'darwin':
            _ad_hoc_sign(install_dir, exe_name)

        if os.path.exists(old_dir):
            shutil.rmtree(old_dir, ignore_errors=True)

        _launch_app(install_dir, exe_name, platform_name)
    except Exception:
        if os.path.exists(old_dir):
            if os.path.exists(install_dir):
                shutil.rmtree(install_dir, ignore_errors=True)
            os.rename(old_dir, install_dir)
        raise


def _wait_for_exit(pid):
    if platform.system() == 'Windows':
        import ctypes
        kernel32 = ctypes.windll.kernel32
        SYNCHRONIZE = 0x00100000
        handle = kernel32.OpenProcess(SYNCHRONIZE, False, pid)
        if handle:
            kernel32.WaitForSingleObject(handle, 0xFFFFFFFF)
            kernel32.CloseHandle(handle)
    else:
        while True:
            try:
                os.kill(pid, 0)
                time.sleep(0.5)
            except (OSError, ProcessLookupError):
                break


def _extract_zip(zip_path, install_dir):
    parent = os.path.dirname(install_dir)
    with zipfile.ZipFile(zip_path, 'r') as zf:
        names = zf.namelist()
        top = set(n.split('/')[0] for n in names if n.split('/')[0]
                  and not n.split('/')[0].startswith('__MACOSX')
                  and n.split('/')[0] != '.DS_Store')

        # Single wrapping dir (Pyamoto.app/ or miyamoto_v1.0/)
        if len(top) == 1:
            wrap = list(top)[0]
            zf.extractall(parent)
            extracted = os.path.join(parent, wrap)
            if extracted != install_dir:
                if os.path.exists(install_dir):
                    shutil.rmtree(install_dir, ignore_errors=True)
                os.rename(extracted, install_dir)
            return

        # Flat contents — extract into install_dir
        os.makedirs(install_dir, exist_ok=True)
        for name in names:
            if name.endswith('/'):
                continue
            target = os.path.join(install_dir, name)
            os.makedirs(os.path.dirname(target), exist_ok=True)
            with zf.open(name) as src, open(target, 'wb') as dst:
                shutil.copyfileobj(src, dst)


def _ad_hoc_sign(install_dir, exe_name):
    if install_dir.endswith('.app') and os.path.isdir(install_dir):
        subprocess.run(
            ['codesign', '--force', '--deep', '--sign', '-', install_dir],
            check=False,
        )
    else:
        app_bundle = os.path.join(install_dir, exe_name)
        if not app_bundle.endswith('.app'):
            app_bundle += '.app'
        if os.path.isdir(app_bundle):
            subprocess.run(
                ['codesign', '--force', '--deep', '--sign', '-', app_bundle],
                check=False,
            )


def _launch_app(install_dir, exe_name, platform_name):
    if platform_name == 'darwin':
        if install_dir.endswith('.app') and os.path.isdir(install_dir):
            subprocess.Popen(['open', install_dir])
        else:
            app_bundle = install_dir
            if not app_bundle.endswith('.app'):
                app_bundle += '.app'
            if os.path.isdir(app_bundle):
                subprocess.Popen(['open', app_bundle])
            else:
                exe_path = os.path.join(install_dir, exe_name)
                if os.path.exists(exe_path):
                    subprocess.Popen([exe_path])
    elif platform_name == 'windows':
        exe_path = os.path.join(install_dir, exe_name)
        if not exe_path.endswith('.exe'):
            exe_path += '.exe'
        subprocess.Popen([exe_path])
    else:
        exe_path = os.path.join(install_dir, exe_name)
        subprocess.Popen([exe_path])


if __name__ == '__main__':
    run_helper()
