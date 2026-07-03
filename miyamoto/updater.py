#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Pyamoto auto-updater — downloads and applies full binary updates.

import json
import os
import platform
import subprocess
import sys
import threading
import urllib.request

from PyQt5 import QtCore, QtWidgets

from . import globals
from .misc import setting, setSetting

GITHUB_REPO = 'Zenith-Team/Pyamoto'
_API_BASE = f'https://api.github.com/repos/{GITHUB_REPO}/releases'
_API_LATEST = f'{_API_BASE}/latest'
_API_RECENT = f'{_API_BASE}?per_page=10'

_HEADERS = {
    'Accept': 'application/vnd.github+json',
    'X-GitHub-Api-Version': '2022-11-28',
    'User-Agent': 'Pyamoto-updater',
}

_OS_MAP = {
    'Darwin': 'macOS-x86_64',
    'Windows': 'Windows-amd64',
    'Linux': 'Linux-x86_64',
}

CHANNEL_STABLE = 'stable'
CHANNEL_NIGHTLY = 'nightly'
CHANNEL_OFF = 'off'

_CHANNEL_LABELS = ['Stable', 'Nightly', 'Off']
_CHANNEL_VALUES = [CHANNEL_STABLE, CHANNEL_NIGHTLY, CHANNEL_OFF]


def _current_channel():
    val = setting('UpdateChannel', None)
    if val is not None:
        return val if val in _CHANNEL_VALUES else CHANNEL_STABLE
    old = setting('CheckForUpdates', None)
    if old is False:
        return CHANNEL_OFF
    return CHANNEL_STABLE


def _install_dir():
    exe = os.path.realpath(sys.executable)
    if platform.system() == 'Darwin':
        parts = exe.split(os.sep)
        for i, part in enumerate(parts):
            if part.endswith('.app'):
                return os.sep.join(parts[:i + 1])
        return os.path.dirname(exe)
    else:
        return os.path.dirname(exe)


def _executable_name():
    if platform.system() == 'Windows':
        return 'Pyamoto.exe'
    return 'Pyamoto'


def _asset_url(release_data):
    os_name = _OS_MAP.get(platform.system())
    if not os_name:
        return None
    ver = release_data['tag_name'].lstrip('v')
    expected = f'pyamoto_v{ver}_{os_name}.zip'
    for asset in release_data.get('assets', []):
        if asset['name'] == expected:
            return asset['browser_download_url']
    for asset in release_data.get('assets', []):
        if asset['name'].endswith('.zip'):
            return asset['browser_download_url']
    return None


class _UpdateChecker(QtCore.QObject):
    update_found = QtCore.pyqtSignal(str, str, str)

    def start(self):
        threading.Thread(target=self._run, daemon=True).start()

    def _run(self):
        try:
            channel = _current_channel()
            if channel == CHANNEL_NIGHTLY:
                self._check_nightly()
            elif channel == CHANNEL_STABLE:
                self._check_release()
        except Exception:
            pass

    def _fetch(self, url):
        req = urllib.request.Request(url, headers=_HEADERS)
        with urllib.request.urlopen(req, timeout=10) as resp:
            return json.loads(resp.read())

    def _check_release(self):
        data = self._fetch(_API_LATEST)
        latest_ver = data['tag_name'].lstrip('v')
        current_ver = globals.MiyamotoVersion.lstrip('v')
        if latest_ver != current_ver:
            url = _asset_url(data)
            if url:
                self.update_found.emit(current_ver, latest_ver, url)

    def _check_nightly(self):
        releases = self._fetch(_API_RECENT)
        nightlies = [
            r for r in releases
            if r.get('prerelease') and r['tag_name'].startswith('nightly-')
        ]
        if not nightlies:
            return
        nightlies.sort(key=lambda r: r['tag_name'], reverse=True)
        latest = nightlies[0]
        latest_sha = latest['tag_name'].rsplit('-', 1)[-1]
        current_sha = globals.MiyamotoVersion
        if latest_sha != current_sha:
            url = _asset_url(latest)
            if url:
                self.update_found.emit(current_sha, latest_sha, url)


class _UpdateDialog(QtWidgets.QDialog):
    def __init__(self, current, latest, download_url, parent=None):
        super().__init__(parent)
        self._download_url = download_url
        self._zip_path = None
        self._cancel = False
        self._tmp_dir = None

        is_nightly = globals.MiyamotoReleaseType == 'nightly'
        kind = 'Nightly ' if is_nightly else ''
        self.setWindowTitle(f'Pyamoto {kind}Update Available')
        self.setWindowFlag(QtCore.Qt.WindowContextHelpButtonHint, False)
        self.setFixedWidth(440)
        self.setSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Minimum)

        root = QtWidgets.QVBoxLayout(self)
        root.setSpacing(12)
        root.setContentsMargins(24, 22, 24, 20)

        headline = QtWidgets.QLabel(f'Update: v{current} \u2192 v{latest}')
        hf = headline.font()
        hf.setPointSize(hf.pointSize() + 3)
        hf.setBold(True)
        headline.setFont(hf)
        root.addWidget(headline)

        warn = QtWidgets.QLabel(
            'Project data will be overwritten. '
            '<b>User data</b> (patches, settings, downloads) stays untouched.'
        )
        warn.setWordWrap(True)
        root.addWidget(warn)

        self._progress = QtWidgets.QProgressBar()
        self._progress.setVisible(False)
        root.addWidget(self._progress)

        self._status = QtWidgets.QLabel()
        self._status.setVisible(False)
        root.addWidget(self._status)

        self._codesign_cb = None
        if platform.system() == 'Darwin':
            self._codesign_cb = QtWidgets.QCheckBox('Ad-hoc re-sign bundle')
            self._codesign_cb.setChecked(True)
            self._codesign_cb.setToolTip(
                'Run codesign --force --deep --sign - on updated app. '
                'Reduces Gatekeeper warnings.'
            )
            root.addWidget(self._codesign_cb)

        btn_box = QtWidgets.QDialogButtonBox()
        self._cancel_btn = btn_box.addButton('Cancel', QtWidgets.QDialogButtonBox.RejectRole)
        self._cancel_btn.setAutoDefault(False)
        self._dl_btn = btn_box.addButton('Download & Update', QtWidgets.QDialogButtonBox.AcceptRole)
        self._dl_btn.setDefault(True)
        btn_box.accepted.connect(self._on_download)
        btn_box.rejected.connect(self.reject)
        root.addWidget(btn_box)

    def _on_download(self):
        self._dl_btn.setEnabled(False)
        self._cancel_btn.setText('Cancel')
        self._cancel_btn.setEnabled(True)
        self._progress.setVisible(True)
        self._status.setVisible(True)
        self._status.setText('Downloading update...')
        try:
            self._dl_btn.clicked.disconnect()
        except TypeError:
            pass
        threading.Thread(target=self._download_update, daemon=True).start()

    def _download_update(self):
        import tempfile
        try:
            req = urllib.request.Request(self._download_url, headers=_HEADERS)
            with urllib.request.urlopen(req, timeout=120) as resp:
                total = int(resp.headers.get('Content-Length', 0))
                chunk = 8192
                data = bytearray()
                while not self._cancel:
                    part = resp.read(chunk)
                    if not part:
                        break
                    data.extend(part)
                    if total:
                        pct = int(len(data) / total * 100)
                        self._progress.setValue(pct)

            if self._cancel:
                return

            self._tmp_dir = tempfile.mkdtemp(prefix='pyamoto_update_')
            self._zip_path = os.path.join(self._tmp_dir, 'update.zip')
            with open(self._zip_path, 'wb') as f:
                f.write(data)

            self._status.setText('Download complete!')
            self._progress.setValue(100)
            self._dl_btn.setText('Restart & Update')
            self._dl_btn.setEnabled(True)
            self._cancel_btn.setText('Cancel')
            self._dl_btn.clicked.connect(self._on_restart)
        except Exception as e:
            self._status.setText(f'Download failed: {e}')
            self._dl_btn.setText('Retry')
            self._dl_btn.setEnabled(True)
            self._dl_btn.clicked.connect(self._on_download)

    def _on_restart(self):
        if not self._zip_path or not os.path.exists(self._zip_path):
            return
        codesign = self._codesign_cb.isChecked() if self._codesign_cb else False
        self._spawn_helper(codesign)
        QtWidgets.QApplication.quit()

    def _spawn_helper(self, codesign):
        install_dir = _install_dir()
        exe_name = _executable_name()
        args = [
            sys.executable,
            '--update-helper',
            '--zip', self._zip_path,
            '--install-dir', install_dir,
            '--exe', exe_name,
            '--platform', platform.system().lower(),
            '--wait-pid', str(os.getpid()),
        ]
        if codesign:
            args.append('--codesign')
        subprocess.Popen(args)

    def reject(self):
        self._cancel = True
        if self._tmp_dir and os.path.isdir(self._tmp_dir):
            import shutil
            shutil.rmtree(self._tmp_dir, ignore_errors=True)
        super().reject()


_checker = None


def check_for_updates():
    channel = _current_channel()
    if channel == CHANNEL_OFF:
        return
    global _checker
    _checker = _UpdateChecker()
    _checker.update_found.connect(_show_dialog)
    _checker.start()


def _show_dialog(current, latest, download_url):
    dlg = _UpdateDialog(current, latest, download_url, globals.mainWindow)
    dlg.exec_()
