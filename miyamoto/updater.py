#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Pyamoto update notifier — checks GitHub for new versions and opens
# the release page for manual download.  No automatic installation.

import json
import threading
import urllib.request

from PyQt5 import QtCore, QtGui, QtWidgets

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

CHANNEL_STABLE = 'stable'
CHANNEL_NIGHTLY = 'nightly'
CHANNEL_OFF = 'off'

_CHANNEL_LABELS = ['Stable', 'Nightly', 'Off']
_CHANNEL_VALUES = [CHANNEL_STABLE, CHANNEL_NIGHTLY, CHANNEL_OFF]


def _default_channel():
    return CHANNEL_NIGHTLY if globals.MiyamotoReleaseType == 'nightly' else CHANNEL_STABLE


def _current_channel():
    val = setting('UpdateChannel', None)
    if val is not None:
        return val if val in _CHANNEL_VALUES else CHANNEL_STABLE
    return _default_channel()


def _is_skipped(version):
    skipped = setting('SkippedUpdates', [])
    return isinstance(skipped, list) and version in skipped


def _skip_version(version):
    skipped = setting('SkippedUpdates', [])
    if not isinstance(skipped, list):
        skipped = []
    if version not in skipped:
        skipped.append(version)
    setSetting('SkippedUpdates', skipped)


class _UpdateChecker(QtCore.QObject):
    update_found = QtCore.pyqtSignal(str, str, str)
    up_to_date = QtCore.pyqtSignal()

    def start(self, channel=None):
        self._channel_override = channel
        self._found = False
        threading.Thread(target=self._run, daemon=True).start()

    def _run(self):
        try:
            channel = self._channel_override or _current_channel()
            if channel == CHANNEL_NIGHTLY:
                self._check_nightly()
            elif channel == CHANNEL_STABLE:
                self._check_release()
        except Exception:
            pass
        if not self._found:
            self.up_to_date.emit()
        global _checker
        if _checker is self:
            _checker = None

    def _fetch(self, url):
        req = urllib.request.Request(url, headers=_HEADERS)
        with urllib.request.urlopen(req, timeout=10) as resp:
            return json.loads(resp.read())

    def _check_release(self):
        data = self._fetch(_API_LATEST)
        latest_ver = data['tag_name'].lstrip('v')
        current_ver = globals.MiyamotoVersion.lstrip('v')
        if latest_ver != current_ver and not _is_skipped(latest_ver):
            self._found = True
            self.update_found.emit(current_ver, latest_ver, data['tag_name'])

    def _check_nightly(self):
        releases = self._fetch(_API_RECENT)
        nightlies = [
            r for r in releases
            if r.get('prerelease') and r['tag_name'].startswith('nightly-')
        ]
        if not nightlies:
            return
        nightlies.sort(key=lambda r: r.get('published_at', r['created_at']), reverse=True)
        latest = nightlies[0]
        latest_sha = latest['tag_name'].rsplit('-', 1)[-1]
        current_sha = globals.MiyamotoVersion
        if latest_sha != current_sha and not _is_skipped(latest_sha):
            self._found = True
            self.update_found.emit(current_sha, latest_sha, latest['tag_name'])


class _UpdateDialog(QtWidgets.QDialog):
    def __init__(self, current, latest, tag_name, parent=None):
        super().__init__(parent)
        self._latest = latest
        self._tag_name = tag_name

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

        info = QtWidgets.QLabel(
            'A new version is available. Visit the release page to download it, '
            'then install manually over your current installation.'
        )
        info.setWordWrap(True)
        root.addWidget(info)

        btn_box = QtWidgets.QDialogButtonBox()
        skip_btn = btn_box.addButton('Skip this version', QtWidgets.QDialogButtonBox.DestructiveRole)
        skip_btn.setAutoDefault(False)
        skip_btn.clicked.connect(self._on_skip)
        cancel_btn = btn_box.addButton('Cancel', QtWidgets.QDialogButtonBox.RejectRole)
        cancel_btn.setAutoDefault(False)
        dl_btn = btn_box.addButton('Download', QtWidgets.QDialogButtonBox.AcceptRole)
        dl_btn.setDefault(True)
        dl_btn.clicked.connect(self._on_download)
        btn_box.rejected.connect(self.reject)
        root.addWidget(btn_box)

    def _on_skip(self):
        _skip_version(self._latest)
        self.reject()

    def _on_download(self):
        url = f'https://github.com/{GITHUB_REPO}/releases/tag/{self._tag_name}'
        QtGui.QDesktopServices.openUrl(QtCore.QUrl(url))
        self.accept()


_checker = None


def check_for_updates():
    channel = _current_channel()
    if channel == CHANNEL_OFF:
        return
    _start_check(channel)


def check_for_updates_now(channel):
    _start_check(channel, manual=True)


def _start_check(channel, manual=False):
    global _checker
    if _checker is not None:
        return
    _checker = _UpdateChecker()
    _checker.update_found.connect(_on_update_found)
    if manual:
        _checker.up_to_date.connect(_on_up_to_date)
    _checker.start(channel)


def _on_update_found(current, latest, tag_name):
    dlg = _UpdateDialog(current, latest, tag_name, globals.mainWindow)
    dlg.exec_()


def _on_up_to_date():
    msg = QtWidgets.QMessageBox(globals.mainWindow)
    msg.setWindowTitle('Pyamoto')
    msg.setText('Software is up to date')
    msg.setInformativeText(f'v{globals.MiyamotoVersion} {globals.MiyamotoReleaseType}')
    msg.setStandardButtons(QtWidgets.QMessageBox.Ok)
    msg.exec_()
