#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Pyamoto Level Editor
# Copyright (C) 2009-2026 Pyamoto contributors
# This file is part of Pyamoto.

# See LICENSE.txt for more information.


################################################################
################################################################

############ Imports ############

import os

from PyQt5 import QtCore, QtGui, QtWidgets
Qt = QtCore.Qt

from .bytes import bytes_to_string, to_bytes
from . import globals
from .items import ZoneItem
from .misc import HexSpinBox, BGName, setting
from .strings import MiyamotoTranslation
from .ui import MiyamotoTheme, toQColor, GetIcon, createHorzLine
from .widgets import LoadingTab, TilesetsTab
from .verifications import SetDirty

#################################


class InputBox(QtWidgets.QDialog):
    Type_TextBox = 1
    Type_SpinBox = 2
    Type_HexSpinBox = 3

    def __init__(self, type=Type_TextBox):
        super().__init__()

        self.label = QtWidgets.QLabel('-')
        self.label.setWordWrap(True)

        if type == InputBox.Type_TextBox:
            self.textbox = QtWidgets.QLineEdit()
            widget = self.textbox
        elif type == InputBox.Type_SpinBox:
            self.spinbox = QtWidgets.QSpinBox()
            widget = self.spinbox
        elif type == InputBox.Type_HexSpinBox:
            self.spinbox = HexSpinBox()
            widget = self.spinbox

        self.buttons = QtWidgets.QDialogButtonBox(QtWidgets.QDialogButtonBox.Ok | QtWidgets.QDialogButtonBox.Cancel)
        self.buttons.accepted.connect(self.accept)
        self.buttons.rejected.connect(self.reject)

        self.layout = QtWidgets.QVBoxLayout()
        self.layout.addWidget(self.label)
        self.layout.addWidget(widget)
        self.layout.addWidget(self.buttons)
        self.setLayout(self.layout)


class AboutDialog(QtWidgets.QDialog):
    """
    The About info for Miyamoto
    """

    def __init__(self):
        """
        Creates and initializes the dialog
        """
        super().__init__()
        self.setWindowTitle(globals.trans.string('AboutDlg', 0))
        self.setWindowIcon(GetIcon('help'))

        # Open the readme file
        f = open('readme.md', 'r')
        readme = f.read()
        f.close()
        del f

        # Description
        description = '<html><head><style type=\'text/CSS\'>'
        description += 'body {font-family: Calibri}'
        description += '.main {font-size: 12px}'
        description += '</style></head><body>'
        description += '<center><h1><i>Pyamoto</i> Level Editor</h1><div class=\'main\'>'
        description += '<i>Pyamoto Level Editor</i> is an advanced fork of the original Miyamoto editor with the purpose of improving functionality and usability.<br>'
        description += '</div></center></body></html>'
        description += 'Need help? Check out <a href=\'https://github.com/Zenith-Team/Pyamoto\'>the Github repository</a>, and <a href=\'https://go.nsmbu.net/discord\'>our Discord server</a><br>'

        # Description label
        descLabel = QtWidgets.QLabel()
        descLabel.setText(description)
        descLabel.setMinimumWidth(512)
        descLabel.setWordWrap(True)

        # Readme.md viewer
        readmeView = QtWidgets.QPlainTextEdit()
        readmeView.setPlainText(readme)
        readmeView.setReadOnly(True)

        # Buttonbox
        buttonBox = QtWidgets.QDialogButtonBox(QtWidgets.QDialogButtonBox.Ok)
        buttonBox.accepted.connect(self.accept)

        # Main layout
        L = QtWidgets.QGridLayout()
        L.addWidget(descLabel, 0, 1)
        L.addWidget(readmeView, 1, 1)
        L.addWidget(buttonBox, 2, 0, 1, 2)
        L.setRowStretch(1, 1)
        L.setColumnStretch(1, 1)
        self.setLayout(L)


class ObjectShiftDialog(QtWidgets.QDialog):
    """
    Lets you pick an amount to shift selected items by
    """

    def __init__(self):
        """
        Creates and initializes the dialog
        """
        super().__init__()
        self.setWindowTitle(globals.trans.string('ShftItmDlg', 0))
        self.setWindowIcon(GetIcon('move'))

        self.XOffset = QtWidgets.QSpinBox()
        self.XOffset.setRange(-16384, 16383)

        self.YOffset = QtWidgets.QSpinBox()
        self.YOffset.setRange(-8192, 8191)

        buttonBox = QtWidgets.QDialogButtonBox(QtWidgets.QDialogButtonBox.Ok | QtWidgets.QDialogButtonBox.Cancel)
        buttonBox.accepted.connect(self.accept)
        buttonBox.rejected.connect(self.reject)

        moveLayout = QtWidgets.QFormLayout()
        offsetlabel = QtWidgets.QLabel(globals.trans.string('ShftItmDlg', 2))
        offsetlabel.setWordWrap(True)
        moveLayout.addWidget(offsetlabel)
        moveLayout.addRow(globals.trans.string('ShftItmDlg', 3), self.XOffset)
        moveLayout.addRow(globals.trans.string('ShftItmDlg', 4), self.YOffset)

        moveGroupBox = QtWidgets.QGroupBox(globals.trans.string('ShftItmDlg', 1))
        moveGroupBox.setLayout(moveLayout)

        mainLayout = QtWidgets.QVBoxLayout()
        mainLayout.addWidget(moveGroupBox)
        mainLayout.addWidget(buttonBox)
        self.setLayout(mainLayout)


class ObjectTilesetSwapDialog(QtWidgets.QDialog):
    """
    Lets you pick tilesets to swap objects to
    """

    def __init__(self):
        """
        Creates and initializes the dialog
        """
        super().__init__()
        self.setWindowTitle('Swap Objects\' Tilesets')
        self.setWindowIcon(GetIcon('swap'))

        # Create widgets
        self.FromTS = QtWidgets.QSpinBox()
        self.FromTS.setRange(1, 4)

        self.ToTS = QtWidgets.QSpinBox()
        self.ToTS.setRange(1, 4)

        # Swap layouts
        swapLayout = QtWidgets.QFormLayout()

        swapLayout.addRow('From tileset:', self.FromTS)
        swapLayout.addRow('To tileset:', self.ToTS)

        self.DoExchange = QtWidgets.QCheckBox('Exchange (perform 2-way conversion)')

        # Buttonbox
        buttonBox = QtWidgets.QDialogButtonBox(QtWidgets.QDialogButtonBox.Ok | QtWidgets.QDialogButtonBox.Cancel)
        buttonBox.accepted.connect(self.accept)
        buttonBox.rejected.connect(self.reject)

        # Main layout
        mainLayout = QtWidgets.QVBoxLayout()
        mainLayout.addLayout(swapLayout)
        mainLayout.addWidget(self.DoExchange)
        mainLayout.addWidget(buttonBox)
        self.setLayout(mainLayout)


class ObjectTypeSwapDialog(QtWidgets.QDialog):
    """
    Lets you pick object types to swap objects to
    """

    def __init__(self):
        """
        Creates and initializes the dialog
        """
        super().__init__()
        self.setWindowTitle('Swap Objects\' Types')
        self.setWindowIcon(GetIcon('swap'))

        # Create widgets
        self.FromType = QtWidgets.QSpinBox()
        self.FromType.setRange(0, 255)

        self.ToType = QtWidgets.QSpinBox()
        self.ToType.setRange(0, 255)

        self.FromTileset = QtWidgets.QSpinBox()
        self.FromTileset.setRange(1, 4)

        self.ToTileset = QtWidgets.QSpinBox()
        self.ToTileset.setRange(1, 4)

        self.DoExchange = QtWidgets.QCheckBox('Exchange (perform 2-way conversion)')

        # Swap layout
        swapLayout = QtWidgets.QGridLayout()

        swapLayout.addWidget(QtWidgets.QLabel('From tile type:'), 0, 0)
        swapLayout.addWidget(self.FromType, 0, 1)

        swapLayout.addWidget(QtWidgets.QLabel('From tileset:'), 1, 0)
        swapLayout.addWidget(self.FromTileset, 1, 1)

        swapLayout.addWidget(QtWidgets.QLabel('To tile type:'), 0, 2)
        swapLayout.addWidget(self.ToType, 0, 3)

        swapLayout.addWidget(QtWidgets.QLabel('To tileset:'), 1, 2)
        swapLayout.addWidget(self.ToTileset, 1, 3)

        # Buttonbox
        buttonBox = QtWidgets.QDialogButtonBox(QtWidgets.QDialogButtonBox.Ok | QtWidgets.QDialogButtonBox.Cancel)
        buttonBox.accepted.connect(self.accept)
        buttonBox.rejected.connect(self.reject)

        # Main layout
        mainLayout = QtWidgets.QVBoxLayout()
        mainLayout.addLayout(swapLayout)
        mainLayout.addWidget(self.DoExchange)
        mainLayout.addWidget(buttonBox)
        self.setLayout(mainLayout)


class MetaInfoDialog(QtWidgets.QDialog):
    """
    Allows the user to enter in various meta-info to be kept in the level for display
    """

    def __init__(self):
        """
        Creates and initializes the dialog
        """
        super().__init__()
        self.setWindowTitle(globals.trans.string('InfoDlg', 0))
        self.setWindowIcon(GetIcon('info'))

        title = globals.Area.Metadata.strData('Title')
        author = globals.Area.Metadata.strData('Author')
        group = globals.Area.Metadata.strData('Group')
        website = globals.Area.Metadata.strData('Website')
        creator = globals.Area.Metadata.strData('Creator')
        password = globals.Area.Metadata.strData('Password')
        if title is None: title = '-'
        if author is None: author = '-'
        if group is None: group = '-'
        if website is None: website = '-'
        if creator is None: creator = '(unknown)'
        if password is None: password = ''

        self.levelName = QtWidgets.QLineEdit()
        self.levelName.setMaxLength(128)
        self.levelName.setReadOnly(True)
        self.levelName.setMinimumWidth(320)
        self.levelName.setText(title)

        self.Author = QtWidgets.QLineEdit()
        self.Author.setMaxLength(128)
        self.Author.setReadOnly(True)
        self.Author.setMinimumWidth(320)
        self.Author.setText(author)

        self.Group = QtWidgets.QLineEdit()
        self.Group.setMaxLength(128)
        self.Group.setReadOnly(True)
        self.Group.setMinimumWidth(320)
        self.Group.setText(group)

        self.Website = QtWidgets.QLineEdit()
        self.Website.setMaxLength(128)
        self.Website.setReadOnly(True)
        self.Website.setMinimumWidth(320)
        self.Website.setText(website)

        self.Password = QtWidgets.QLineEdit()
        self.Password.setMaxLength(128)
        self.Password.textChanged.connect(self.PasswordEntry)
        self.Password.setMinimumWidth(320)

        self.changepw = QtWidgets.QPushButton(globals.trans.string('InfoDlg', 1))

        if password != '':
            self.levelName.setReadOnly(False)
            self.Author.setReadOnly(False)
            self.Group.setReadOnly(False)
            self.Website.setReadOnly(False)
            self.changepw.setDisabled(False)

        buttonBox = QtWidgets.QDialogButtonBox(QtWidgets.QDialogButtonBox.Ok | QtWidgets.QDialogButtonBox.Cancel)
        buttonBox.addButton(self.changepw, buttonBox.ActionRole)
        buttonBox.accepted.connect(self.accept)
        buttonBox.rejected.connect(self.reject)
        self.changepw.clicked.connect(self.ChangeButton)
        self.changepw.setDisabled(True)

        self.lockedLabel = QtWidgets.QLabel(globals.trans.string('InfoDlg', 2))

        infoLayout = QtWidgets.QFormLayout()
        infoLayout.addWidget(self.lockedLabel)
        infoLayout.addRow(globals.trans.string('InfoDlg', 3), self.Password)
        infoLayout.addRow(globals.trans.string('InfoDlg', 4), self.levelName)
        infoLayout.addRow(globals.trans.string('InfoDlg', 5), self.Author)
        infoLayout.addRow(globals.trans.string('InfoDlg', 6), self.Group)
        infoLayout.addRow(globals.trans.string('InfoDlg', 7), self.Website)

        self.PasswordLabel = infoLayout.labelForField(self.Password)

        levelIsLocked = password != ''
        self.lockedLabel.setVisible(levelIsLocked)
        self.PasswordLabel.setVisible(levelIsLocked)
        self.Password.setVisible(levelIsLocked)

        infoGroupBox = QtWidgets.QGroupBox(globals.trans.string('InfoDlg', 8, '[name]', creator))
        infoGroupBox.setLayout(infoLayout)

        mainLayout = QtWidgets.QVBoxLayout()
        mainLayout.addWidget(infoGroupBox)
        mainLayout.addWidget(buttonBox)
        self.setLayout(mainLayout)

        self.PasswordEntry('')

    def PasswordEntry(self, text):
        pswd = globals.Area.Metadata.strData('Password')
        if pswd is None: pswd = ''
        if text == pswd:
            self.levelName.setReadOnly(False)
            self.Author.setReadOnly(False)
            self.Group.setReadOnly(False)
            self.Website.setReadOnly(False)
            self.changepw.setDisabled(False)
        else:
            self.levelName.setReadOnly(True)
            self.Author.setReadOnly(True)
            self.Group.setReadOnly(True)
            self.Website.setReadOnly(True)
            self.changepw.setDisabled(True)

    # To all would be crackers who are smart enough to reach here:
    #
    #   Make your own levels.
    #
    #
    #
    #       - The management
    #


    def ChangeButton(self):
        """
        Allows the changing of a given password
        """

        class ChangePWDialog(QtWidgets.QDialog):
            """
            Dialog
            """

            def __init__(self):
                super().__init__()
                self.setWindowTitle(globals.trans.string('InfoDlg', 9))
                self.setWindowIcon(GetIcon('info'))

                self.New = QtWidgets.QLineEdit()
                self.New.setMaxLength(64)
                self.New.textChanged.connect(self.PasswordMatch)
                self.New.setMinimumWidth(320)

                self.Verify = QtWidgets.QLineEdit()
                self.Verify.setMaxLength(64)
                self.Verify.textChanged.connect(self.PasswordMatch)
                self.Verify.setMinimumWidth(320)

                self.Ok = QtWidgets.QPushButton('OK')
                self.Cancel = QtWidgets.QDialogButtonBox.Cancel

                buttonBox = QtWidgets.QDialogButtonBox()
                buttonBox.addButton(self.Ok, buttonBox.AcceptRole)
                buttonBox.addButton(self.Cancel)

                buttonBox.accepted.connect(self.accept)
                buttonBox.rejected.connect(self.reject)
                self.Ok.setDisabled(True)

                infoLayout = QtWidgets.QFormLayout()
                infoLayout.addRow(globals.trans.string('InfoDlg', 10), self.New)
                infoLayout.addRow(globals.trans.string('InfoDlg', 11), self.Verify)

                infoGroupBox = QtWidgets.QGroupBox(globals.trans.string('InfoDlg', 12))

                infoLabel = QtWidgets.QVBoxLayout()
                infoLabel.addWidget(QtWidgets.QLabel(globals.trans.string('InfoDlg', 13)), 0, Qt.AlignCenter)
                infoLabel.addLayout(infoLayout)
                infoGroupBox.setLayout(infoLabel)

                mainLayout = QtWidgets.QVBoxLayout()
                mainLayout.addWidget(infoGroupBox)
                mainLayout.addWidget(buttonBox)
                self.setLayout(mainLayout)

            def PasswordMatch(self, text):
                self.Ok.setDisabled(self.New.text() != self.Verify.text() and self.New.text() != '')

        dlg = ChangePWDialog()
        if dlg.exec_() == QtWidgets.QDialog.Accepted:
            self.lockedLabel.setVisible(True)
            self.Password.setVisible(True)
            self.PasswordLabel.setVisible(True)
            pswd = str(dlg.Verify.text())
            globals.Area.Metadata.setStrData('Password', pswd)
            self.Password.setText(pswd)
            SetDirty()

            self.levelName.setReadOnly(False)
            self.Author.setReadOnly(False)
            self.Group.setReadOnly(False)
            self.Website.setReadOnly(False)
            self.changepw.setDisabled(False)


class AreaOptionsDialog(QtWidgets.QDialog):
    """
    Dialog which lets you choose among various area options from tabs
    """

    def __init__(self):
        """
        Creates and initializes the tab dialog
        """
        super().__init__()
        self.setWindowTitle(globals.trans.string('AreaDlg', 0))
        self.setWindowIcon(GetIcon('area'))

        self.tabWidget = QtWidgets.QTabWidget()
        self.LoadingTab = LoadingTab()
        self.TilesetsTab = TilesetsTab()
        self.tabWidget.addTab(self.TilesetsTab, globals.trans.string('AreaDlg', 1))
        self.tabWidget.addTab(self.LoadingTab, globals.trans.string('AreaDlg', 2))

        buttonBox = QtWidgets.QDialogButtonBox(QtWidgets.QDialogButtonBox.Ok | QtWidgets.QDialogButtonBox.Cancel)

        buttonBox.accepted.connect(self.accept)
        buttonBox.rejected.connect(self.reject)

        mainLayout = QtWidgets.QVBoxLayout()
        mainLayout.addWidget(self.tabWidget)
        mainLayout.addWidget(buttonBox)
        self.setLayout(mainLayout)


class ZonesDialog(QtWidgets.QDialog):
    """
    Dialog for editing zone properties.
    """

    def __init__(self):
        super().__init__()
        self.setWindowTitle('Edit Zones')
        self.setWindowIcon(GetIcon('zones'))
        self._dirtyTabs = set()  # set of ZoneTab objects with unsaved changes
        self._newButtons = []    # one per zone tab, for _updateButtonStates
        self._cloneButtons = []  # one per zone tab, for _updateButtonStates

        self.tabWidget = QtWidgets.QTabWidget()
        self.zoneTabs = []
        self.BGTabs = []

        for i, z in enumerate(globals.Area.zones):
            self._addZoneTab(z, i)

        self._updateButtonStates()

        saveBtn = QtWidgets.QPushButton("OK")
        saveBtn.setDefault(True)
        dontSaveBtn = QtWidgets.QPushButton("Cancel")
        saveBtn.clicked.connect(self.accept)
        dontSaveBtn.clicked.connect(self._forceReject)

        btnRow = QtWidgets.QHBoxLayout()
        btnRow.addStretch()
        btnRow.addWidget(saveBtn)
        btnRow.addWidget(dontSaveBtn)

        mainLayout = QtWidgets.QVBoxLayout()
        mainLayout.setSpacing(6)
        mainLayout.addWidget(self.tabWidget)
        mainLayout.addLayout(btnRow)
        self.setLayout(mainLayout)

    def _addZoneTab(self, z, idx):
        zoneTab = ZoneTab(z)
        bgTab = BGTab(z.background)
        self.zoneTabs.append(zoneTab)
        self.BGTabs.append(bgTab)

        # Merged Dimensions + Bounds widget (single tab, separated by a line)
        dimBoundsWidget = QtWidgets.QWidget()
        dbLayout = QtWidgets.QVBoxLayout(dimBoundsWidget)
        dbLayout.setContentsMargins(0, 0, 0, 0)
        dbLayout.setSpacing(4)
        dbLayout.addWidget(zoneTab.dimWidget)
        dbLayout.addWidget(createHorzLine())
        dbLayout.addWidget(zoneTab.boundsWidget)

        # Inner per-zone tab widget: one tab per settings section
        innerTabs = QtWidgets.QTabWidget()
        innerTabs.addTab(dimBoundsWidget,   'Dimensions')
        innerTabs.addTab(zoneTab.camWidget, 'Camera')
        innerTabs.addTab(zoneTab.audioWidget, 'Audio')
        innerTabs.addTab(bgTab,             'Background')

        # New / Duplicate / Delete — 3-wide row below inner tabs
        newBtn = QtWidgets.QPushButton('+ New')
        cloneBtn = QtWidgets.QPushButton('Duplicate')
        deleteBtn = QtWidgets.QPushButton('Delete')
        newBtn.clicked.connect(self.NewZone)
        cloneBtn.clicked.connect(self.CloneZone)
        deleteBtn.clicked.connect(self.DeleteZone)
        self._newButtons.append(newBtn)
        self._cloneButtons.append(cloneBtn)

        zoneBtnRow = QtWidgets.QHBoxLayout()
        zoneBtnRow.setContentsMargins(0, 0, 0, 0)
        zoneBtnRow.addWidget(newBtn)
        zoneBtnRow.addWidget(cloneBtn)
        zoneBtnRow.addWidget(deleteBtn)

        container = QtWidgets.QWidget()
        cLayout = QtWidgets.QVBoxLayout(container)
        cLayout.setContentsMargins(6, 6, 6, 6)
        cLayout.setSpacing(5)
        cLayout.addWidget(innerTabs)
        cLayout.addLayout(zoneBtnRow)

        label = self._zoneLabel(idx)
        self.tabWidget.addTab(container, label)

        # Dirty tracking — *args absorbs the signal's emitted value so _zt is never overwritten
        def markDirty(*_, _zt=zoneTab):
            self._markTabDirty(_zt)

        zoneTab.connectChanges(markDirty)
        bgTab.connectChanges(markDirty)

    def _zoneLabel(self, idx):
        count = self.tabWidget.count()
        if count < 5:
            return globals.trans.string('ZonesDlg', 3, '[num]', idx + 1)
        return str(idx + 1)

    def _markTabDirty(self, zoneTab):
        if zoneTab in self._dirtyTabs:
            return
        self._dirtyTabs.add(zoneTab)
        try:
            idx = self.zoneTabs.index(zoneTab)
        except ValueError:
            return
        text = self.tabWidget.tabText(idx)
        if not text.endswith(' *'):
            self.tabWidget.setTabText(idx, text + ' *')

    def _updateButtonStates(self):
        enabled = len(self.zoneTabs) < 8
        for btn in self._newButtons:
            btn.setEnabled(enabled)
        for btn in self._cloneButtons:
            btn.setEnabled(enabled)

    def _renormalizeLabels(self):
        count = self.tabWidget.count()
        for i in range(count):
            if count < 6:
                label = globals.trans.string('ZonesDlg', 3, '[num]', i + 1)
            else:
                label = str(i + 1)
            if self.zoneTabs[i] in self._dirtyTabs:
                label += ' *'
            self.tabWidget.setTabText(i, label)

    def reject(self):
        if self._dirtyTabs:
            names = ', '.join(
                self.tabWidget.tabText(self.zoneTabs.index(zt)).rstrip(' *')
                for zt in self._dirtyTabs
                if zt in self.zoneTabs
            )
            msg = QtWidgets.QMessageBox(self)
            msg.setWindowTitle('Unsaved Changes')
            msg.setText(f'You have unsaved changes in: {names}')
            msg.setInformativeText('Do you want to save before closing?')
            saveBtn = msg.addButton('Save', QtWidgets.QMessageBox.AcceptRole)
            msg.addButton("Don't Save", QtWidgets.QMessageBox.DestructiveRole)
            msg.addButton('Cancel', QtWidgets.QMessageBox.RejectRole)
            msg.exec_()
            clicked = msg.clickedButton()
            if clicked == saveBtn:
                self.accept()
            elif msg.buttonRole(clicked) == QtWidgets.QMessageBox.DestructiveRole:
                super().reject()
            # else Cancel — do nothing, keep dialog open
        else:
            super().reject()

    def _forceReject(self):
        super().reject()

    def NewZone(self):
        if len(self.zoneTabs) >= 15:
            result = QtWidgets.QMessageBox.warning(
                self, globals.trans.string('ZonesDlg', 6), globals.trans.string('ZonesDlg', 7),
                QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)
            if result == QtWidgets.QMessageBox.No:
                return

        idx = len(self.zoneTabs)
        z = ZoneItem(256, 256, 448, 224, 0, 0, idx, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0,
                     (0, 0, 0, 0, 0, 0xF, 0, 0), (0, 0, 0, 0, to_bytes('Black', 16), 0))
        self._addZoneTab(z, idx)
        self._renormalizeLabels()
        self._updateButtonStates()
        self.tabWidget.setCurrentIndex(self.tabWidget.count() - 1)

    def DeleteZone(self):
        curindex = self.tabWidget.currentIndex()
        if self.tabWidget.count() == 0:
            return
        deleted_tab = self.zoneTabs[curindex]
        self._dirtyTabs.discard(deleted_tab)
        self.tabWidget.removeTab(curindex)
        self.zoneTabs.pop(curindex)
        self.BGTabs.pop(curindex)
        self._newButtons.pop(curindex)
        self._cloneButtons.pop(curindex)
        self._renormalizeLabels()
        self._updateButtonStates()

    def CloneZone(self):
        if len(self.zoneTabs) >= 15:
            result = QtWidgets.QMessageBox.warning(
                self, globals.trans.string('ZonesDlg', 6), globals.trans.string('ZonesDlg', 7),
                QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)
            if result == QtWidgets.QMessageBox.No:
                return

        src = self.tabWidget.currentIndex()
        z0 = self.zoneTabs[src].zoneObj
        idx = len(self.zoneTabs)
        z = ZoneItem(
            z0.objx, z0.objy, z0.width, z0.height, z0.modeldark, z0.terraindark, idx, 0,
            z0.cammode, z0.camzoom, z0.unk1, z0.visibility, 0, z0.unk2, z0.camtrack, z0.unk3,
            z0.music, z0.sfxmod, 0, z0.type,
            (z0.yupperbound, z0.ylowerbound, z0.yupperbound2, z0.ylowerbound2, z0.entryid,
             z0.mpcamzoomadjust, z0.yupperbound3, z0.ylowerbound3),
            z0.background,
        )
        self._addZoneTab(z, idx)
        self._renormalizeLabels()
        self._updateButtonStates()
        self.tabWidget.setCurrentIndex(self.tabWidget.count() - 1)


class ZoneTab:
    """
    Builds all zone-property widgets for one zone. Not a QWidget itself;
    its four sub-widgets (dimWidget, camWidget, boundsWidget, audioWidget)
    are inserted directly into the inner QTabWidget in ZonesDialog.
    All widget attributes preserve the same names used by HandleZones in app.py.
    """

    def __init__(self, z):
        self.zoneObj = z
        self.AutoChangingSize = False
        self.AutoEditMusic = False
        self.zm = -1

        self.dimWidget    = self._buildDimensions(z)
        self.camWidget    = self._buildCamera(z)
        self.boundsWidget = self._buildBounds(z)
        self.audioWidget  = self._buildAudio(z)

    # ── Dimensions ──────────────────────────────────────────────────────────

    def _buildDimensions(self, z):
        self.Zone_xpos = QtWidgets.QSpinBox()
        self.Zone_xpos.setRange(16, 65535)
        self.Zone_xpos.setToolTip(globals.trans.string('ZonesDlg', 10))
        self.Zone_xpos.setValue(z.objx)

        self.Zone_ypos = QtWidgets.QSpinBox()
        self.Zone_ypos.setRange(16, 65535)
        self.Zone_ypos.setToolTip(globals.trans.string('ZonesDlg', 12))
        self.Zone_ypos.setValue(z.objy)

        self.Zone_width = QtWidgets.QSpinBox()
        self.Zone_width.setRange(80, 65535)
        self.Zone_width.setToolTip(globals.trans.string('ZonesDlg', 14))
        self.Zone_width.setValue(z.width)
        self.Zone_width.valueChanged.connect(self.PresetDeselected)

        self.Zone_height = QtWidgets.QSpinBox()
        self.Zone_height.setRange(16, 65535)
        self.Zone_height.setToolTip(globals.trans.string('ZonesDlg', 16))
        self.Zone_height.setValue(z.height)
        self.Zone_height.valueChanged.connect(self.PresetDeselected)

        # Common retail zone presets
        self.Zone_presets_values = (
            '0: 416x224', '0: 448x224', '0: 512x272',
            '2: 560x304', '2: 608x320', '3: 704x384', '4: 944x448')
        self.Zone_presets = QtWidgets.QComboBox()
        self.Zone_presets.addItems(self.Zone_presets_values)
        self.Zone_presets.setToolTip(globals.trans.string('ZonesDlg', 18))
        self.Zone_presets.currentIndexChanged.connect(self.PresetSelected)
        self.PresetDeselected()

        self.snapButton8 = QtWidgets.QPushButton(globals.trans.string('ZonesDlg', 78))
        self.snapButton8.clicked.connect(lambda: self.HandleSnapTo8x8Grid(z))
        self.snapButton16 = QtWidgets.QPushButton(globals.trans.string('ZonesDlg', 79))
        self.snapButton16.clicked.connect(lambda: self.HandleSnapTo16x16Grid(z))

        posForm = QtWidgets.QFormLayout()
        posForm.addRow(globals.trans.string('ZonesDlg', 9),  self.Zone_xpos)
        posForm.addRow(globals.trans.string('ZonesDlg', 11), self.Zone_ypos)

        sizeForm = QtWidgets.QFormLayout()
        sizeForm.addRow(globals.trans.string('ZonesDlg', 13), self.Zone_width)
        sizeForm.addRow(globals.trans.string('ZonesDlg', 15), self.Zone_height)
        sizeForm.addRow(globals.trans.string('ZonesDlg', 17), self.Zone_presets)

        snapRow = QtWidgets.QHBoxLayout()
        snapRow.addWidget(self.snapButton8)
        snapRow.addWidget(self.snapButton16)

        cols = QtWidgets.QHBoxLayout()
        cols.addLayout(posForm)
        cols.addSpacing(12)
        cols.addLayout(sizeForm)

        w = QtWidgets.QWidget()
        L = QtWidgets.QVBoxLayout(w)
        L.setContentsMargins(8, 8, 8, 8)
        L.addLayout(cols)
        L.addLayout(snapRow)
        L.addStretch()
        return w

    def HandleSnapTo8x8Grid(self, z):
        left  = self.Zone_xpos.value()
        top   = self.Zone_ypos.value()
        right  = left + self.Zone_width.value()
        bottom = top  + self.Zone_height.value()

        def snap8(v):
            return v - (v % 8) if v % 8 < 4 else v + 8 - (v % 8)

        left, top, right, bottom = snap8(left), snap8(top), snap8(right), snap8(bottom)
        if right  <= left:  right  += 8
        if bottom <= top:   bottom += 8
        right -= left;  bottom -= top
        left   = max(16, min(left,   65528))
        top    = max(16, min(top,    65528))
        right  = max(80, min(right,  65528))
        bottom = max(16, min(bottom, 65528))
        self.Zone_xpos.setValue(left);   self.Zone_ypos.setValue(top)
        self.Zone_width.setValue(right); self.Zone_height.setValue(bottom)

    def HandleSnapTo16x16Grid(self, z):
        left  = self.Zone_xpos.value()
        top   = self.Zone_ypos.value()
        right  = left + self.Zone_width.value()
        bottom = top  + self.Zone_height.value()

        def snap16(v):
            return v - (v % 16) if v % 16 < 8 else v + 16 - (v % 16)

        left, top, right, bottom = snap16(left), snap16(top), snap16(right), snap16(bottom)
        if right  <= left:  right  += 16
        if bottom <= top:   bottom += 16
        right -= left;  bottom -= top
        left   = max(16, min(left,   65520))
        top    = max(16, min(top,    65520))
        right  = max(80, min(right,  65520))
        bottom = max(16, min(bottom, 65520))
        self.Zone_xpos.setValue(left);   self.Zone_ypos.setValue(top)
        self.Zone_width.setValue(right); self.Zone_height.setValue(bottom)

    def PresetSelected(self, info=None):
        if self.AutoChangingSize: return
        if self.Zone_presets.currentText() == globals.trans.string('ZonesDlg', 60): return
        w, h = self.Zone_presets.currentText()[3:].split('x')
        self.AutoChangingSize = True
        self.Zone_width.setValue(int(w))
        self.Zone_height.setValue(int(h))
        self.AutoChangingSize = False
        if self.Zone_presets.itemText(0) == globals.trans.string('ZonesDlg', 60):
            self.Zone_presets.removeItem(0)

    def PresetDeselected(self, info=None):
        if self.AutoChangingSize: return
        self.AutoChangingSize = True
        check = '%dx%d' % (self.Zone_width.value(), self.Zone_height.value())
        found = next((p for p in self.Zone_presets_values if check == p[3:]), None)
        if found is not None:
            self.Zone_presets.setCurrentIndex(self.Zone_presets.findText(found))
            if self.Zone_presets.itemText(0) == globals.trans.string('ZonesDlg', 60):
                self.Zone_presets.removeItem(0)
        else:
            if self.Zone_presets.itemText(0) != globals.trans.string('ZonesDlg', 60):
                self.Zone_presets.insertItem(0, globals.trans.string('ZonesDlg', 60))
            self.Zone_presets.setCurrentIndex(0)
        self.AutoChangingSize = False

    # ── Camera ──────────────────────────────────────────────────────────────

    def _buildCamera(self, z):
        # Spotlight / full-dark checkboxes
        self.Zone_vspotlight = QtWidgets.QCheckBox(globals.trans.string('ZonesDlg', 26))
        self.Zone_vspotlight.setToolTip(globals.trans.string('ZonesDlg', 27))
        self.Zone_vfulldark  = QtWidgets.QCheckBox(globals.trans.string('ZonesDlg', 28))
        self.Zone_vfulldark.setToolTip(globals.trans.string('ZonesDlg', 29))

        self.Zone_visibility = QtWidgets.QComboBox()
        self.zv = z.visibility
        if self.zv & 0x10: self.Zone_vspotlight.setChecked(True)
        if self.zv & 0x20: self.Zone_vfulldark.setChecked(True)
        self.ChangeVisibilityList()
        self.Zone_vspotlight.clicked.connect(self.ChangeVisibilityList)
        self.Zone_vfulldark.clicked.connect(self.ChangeVisibilityList)

        # Camera mode radios
        cammode = z.cammode if z.cammode <= 7 else 3
        camzoom = z.camzoom
        if cammode == 2:
            if camzoom > 8:  camzoom = 0
        elif 1 < cammode < 6:
            if camzoom > 9:  camzoom = 0
        else:
            if camzoom > 11: camzoom = 0

        self.Zone_cammodebuttongroup = QtWidgets.QButtonGroup()
        cammodebuttons = []
        for btnId, name, tooltip in [
            (0, 'Normal',                     'The standard camera mode, appropriate for most situations.'),
            (3, 'Static Zoom',                'The camera will not zoom out during multiplayer.'),
            (4, 'Static Zoom, Y Track Only',  'No multiplayer zoom-out; camera centered horizontally.'),
            (5, 'Static Zoom, Event-Ctrl*',   'No multiplayer zoom-out; event-controlled camera (*removed in NSMBU).'),
            (6, 'X Tracking Only',            'Camera only moves horizontally, aligned to bottom edge.'),
            (7, 'X Expanding Only',           'Camera zooms out in multiplayer only if players are far apart horizontally.'),
            (1, 'Y Tracking Only',            'Camera only moves vertically, centered horizontally.'),
            (2, 'Y Expanding Only',           'Camera zooms out in multiplayer if players are far apart vertically.'),
        ]:
            rb = QtWidgets.QRadioButton('%d: %s' % (btnId, name))
            rb.setToolTip('<b>%s:</b><br>%s' % (name, tooltip))
            self.Zone_cammodebuttongroup.addButton(rb, btnId)
            cammodebuttons.append(rb)
            if btnId == cammode: rb.setChecked(True)
            rb.clicked.connect(self.ChangeCamModeList)

        camModeGrid = QtWidgets.QGridLayout()
        camModeGrid.setSpacing(2)
        for i, b in enumerate(cammodebuttons):
            camModeGrid.addWidget(b, i % 4, i // 4)

        self.Zone_screenheights = QtWidgets.QComboBox()
        self.Zone_screenheights.setToolTip(
            "<b>Screen Heights:</b><br>Screen heights (in blocks) the camera can use during multiplayer. "
            "Only the smallest height is used in single-player.<br>"
            "* or ** = glitchy when zone bounds are 0; ** = also unplayably glitchy in multiplayer.")
        self.ChangeCamModeList()
        self.Zone_screenheights.setCurrentIndex(camzoom)

        directionmodeValues = globals.trans.stringList('ZonesDlg', 38)
        self.Zone_directionmode = QtWidgets.QComboBox()
        self.Zone_directionmode.addItems(directionmodeValues)
        self.Zone_directionmode.setToolTip(globals.trans.string('ZonesDlg', 40))
        self.Zone_directionmode.setCurrentIndex(z.camtrack if z.camtrack < 9 else 0)

        self.Zone_camunk1 = QtWidgets.QSpinBox()
        self.Zone_camunk1.setRange(0, 255)
        self.Zone_camunk1.setToolTip("It is unknown what this value does.")
        self.Zone_camunk1.setValue(z.unk1)

        self.Zone_camunk2 = QtWidgets.QSpinBox()
        self.Zone_camunk2.setRange(0, 255)
        self.Zone_camunk2.setToolTip("Value looks to be unused in the game code.")
        self.Zone_camunk2.setValue(z.unk2)

        self.Zone_camunk3 = QtWidgets.QSpinBox()
        self.Zone_camunk3.setRange(0, 255)
        self.Zone_camunk3.setToolTip("Used as \"Progress Path ID\" in NSMB2.")
        self.Zone_camunk3.setValue(z.unk3)

        # Zone settings checkboxes (8 flags)
        self.Zone_settings = []
        settingsNames = globals.trans.stringList('ZonesDlg', 77)
        flagsLeft  = QtWidgets.QFormLayout()
        flagsRight = QtWidgets.QFormLayout()
        for i in range(8):
            cb = QtWidgets.QCheckBox()
            cb.setChecked(bool(z.type & (1 << i)))
            cb.setStyleSheet("margin-left:100%;")
            self.Zone_settings.append(cb)
            (flagsLeft if i < 4 else flagsRight).addRow(settingsNames[i], cb)

        flagsRow = QtWidgets.QHBoxLayout()
        flagsRow.addLayout(flagsLeft)
        flagsRow.addStretch()
        flagsRow.addLayout(flagsRight)

        # Camera form
        camForm = QtWidgets.QFormLayout()
        camForm.addRow('Camera Mode:', camModeGrid)
        camForm.addRow('Screen Heights:', self.Zone_screenheights)
        camForm.addRow(globals.trans.string('ZonesDlg', 39), self.Zone_directionmode)

        # Lighting row
        lightRow = QtWidgets.QHBoxLayout()
        lightRow.addWidget(self.Zone_vspotlight)
        lightRow.addWidget(self.Zone_vfulldark)
        lightRow.addStretch()

        visForm = QtWidgets.QFormLayout()
        visForm.addRow('Lighting:', lightRow)
        visForm.addRow('Visibility Effect:', self.Zone_visibility)

        # Unknowns
        unkForm = QtWidgets.QFormLayout()
        unkForm.addRow('Unknown 1:', self.Zone_camunk1)
        unkForm.addRow('Unknown 2:', self.Zone_camunk2)
        unkForm.addRow('Unknown 3:', self.Zone_camunk3)

        w = QtWidgets.QWidget()
        L = QtWidgets.QVBoxLayout(w)
        L.setContentsMargins(8, 8, 8, 8)
        L.setSpacing(6)
        L.addLayout(camForm)
        L.addWidget(createHorzLine())
        L.addLayout(visForm)
        L.addWidget(createHorzLine())
        L.addLayout(unkForm)
        L.addWidget(createHorzLine())
        L.addLayout(flagsRow)
        L.addStretch()
        return w

    def ChangeVisibilityList(self):
        SelectedIndex = self.zv & 0x0F
        self.Zone_visibility.clear()

        if not self.Zone_vspotlight.isChecked() and not self.Zone_vfulldark.isChecked():
            self.Zone_visibility.addItem(globals.trans.string('ZonesDlg', 41))
            self.Zone_visibility.setToolTip(globals.trans.string('ZonesDlg', 42))
            SelectedIndex = 0
        elif self.Zone_vspotlight.isChecked() and self.Zone_vfulldark.isChecked():
            self.Zone_visibility.addItem(globals.trans.string('ZonesDlg', 80))
            self.Zone_visibility.setToolTip(globals.trans.string('ZonesDlg', 81))
            SelectedIndex = 0
        elif self.Zone_vspotlight.isChecked():
            self.Zone_visibility.addItems(globals.trans.stringList('ZonesDlg', 43))
            self.Zone_visibility.setToolTip(globals.trans.string('ZonesDlg', 44))
            if SelectedIndex > 2: SelectedIndex = 0
        elif self.Zone_vfulldark.isChecked():
            self.Zone_visibility.addItems(globals.trans.stringList('ZonesDlg', 45))
            self.Zone_visibility.setToolTip(globals.trans.string('ZonesDlg', 46))
            if SelectedIndex > 5: SelectedIndex = 5

        self.Zone_visibility.setCurrentIndex(SelectedIndex)

    def ChangeCamModeList(self):
        mode = self.Zone_cammodebuttongroup.checkedId()
        oldListChoice = [1, 1, 2, 3, 3, 3, 1, 1][self.zm] if self.zm != -1 else -1
        newListChoice = [1, 1, 2, 3, 3, 3, 1, 1][mode]

        if self.zm == -1 or oldListChoice != newListChoice:
            if newListChoice == 1:
                heights = [
                    ([14, 19  ],       ''), ([14, 19, 24],    ''), ([14, 19, 28],    ''),
                    ([20, 24  ],       ''), ([19, 24, 28],    ''), ([17, 24  ],      ''),
                    ([17, 24, 28],     ''), ([17, 20  ],      ''), ([ 7, 11, 28],    '**'),
                    ([17, 20.5, 24],   ''), ([17, 20, 28],    ''), ([20,  0,  0],    ''),
                ]
            elif newListChoice == 2:
                heights = [
                    ([14, 19  ],       ''), ([14, 19, 24],    ''), ([14, 19, 28],    ''),
                    ([19, 19, 24],     ''), ([19, 24, 28],    ''), ([19, 24, 28],    ''),
                    ([17, 24, 28],     ''), ([17, 20.5, 24],  ''), ([17,  0,  0],    ''),
                ]
            else:
                heights = [
                    ([14  ], ''), ([19  ], ''), ([24  ], ''), ([28  ], ''),
                    ([17  ], ''), ([20  ], ''), ([16  ], ''), ([28  ], ''),
                    ([ 7  ], '*'), ([10.5], '*'),
                ]

            items = ['%d: ' % i + ' -> '.join('%s blocks' % o for o in opts) + ast
                     for i, (opts, ast) in enumerate(heights)]
            self.Zone_screenheights.clear()
            self.Zone_screenheights.addItems(items)
            self.Zone_screenheights.setCurrentIndex(0)
            self.zm = mode

    # ── Bounds ──────────────────────────────────────────────────────────────

    def _buildBounds(self, z):
        self.Zone_yboundup = QtWidgets.QSpinBox()
        self.Zone_yboundup.setRange(-32688, 32847)
        self.Zone_yboundup.setToolTip(globals.trans.string('ZonesDlg', 49))
        self.Zone_yboundup.setValue(80 + z.yupperbound)

        self.Zone_ybounddown = QtWidgets.QSpinBox()
        self.Zone_ybounddown.setRange(-32695, 32840)
        self.Zone_ybounddown.setToolTip(globals.trans.string('ZonesDlg', 51))
        self.Zone_ybounddown.setValue(72 - z.ylowerbound)

        self.Zone_yboundup2 = QtWidgets.QSpinBox()
        self.Zone_yboundup2.setRange(-32680, 32855)
        self.Zone_yboundup2.setToolTip(globals.trans.string('ZonesDlg', 71))
        self.Zone_yboundup2.setValue(88 + z.yupperbound2)

        self.Zone_ybounddown2 = QtWidgets.QSpinBox()
        self.Zone_ybounddown2.setRange(-32679, 32856)
        self.Zone_ybounddown2.setToolTip(globals.trans.string('ZonesDlg', 73))
        self.Zone_ybounddown2.setValue(88 - z.ylowerbound2)

        self.Zone_yboundup3 = QtWidgets.QSpinBox()
        self.Zone_yboundup3.setRange(-32768, 32767)
        self.Zone_yboundup3.setToolTip(
            '<b>Multiplayer Upper Bounds Adjust:</b><br>Added to the upper bounds value during '
            'multiplayer and after an Auto-Scroll Controller finishes its path.')
        self.Zone_yboundup3.setValue(z.yupperbound3)

        self.Zone_ybounddown3 = QtWidgets.QSpinBox()
        self.Zone_ybounddown3.setRange(-32767, 32768)
        self.Zone_ybounddown3.setToolTip(
            '<b>Multiplayer Lower Bounds Adjust:</b><br>Added to the lower bounds value during '
            'multiplayer and after an Auto-Scroll Controller finishes its path.')
        self.Zone_ybounddown3.setValue(-z.ylowerbound3)

        self.Zone_boundflg = QtWidgets.QCheckBox()
        self.Zone_boundflg.setToolTip(globals.trans.string('ZonesDlg', 75))
        self.Zone_boundflg.setChecked(z.mpcamzoomadjust == 0xF)
        self.Zone_boundflg.stateChanged.connect(
            lambda: self.Zone_mpzoomadjust.setEnabled(not self.Zone_boundflg.isChecked()))

        self.Zone_mpzoomadjust = QtWidgets.QSpinBox()
        self.Zone_mpzoomadjust.setRange(0, 14)
        self.Zone_mpzoomadjust.setToolTip(
            '<b>Multiplayer Screen Height Adjust:</b><br>Increases screen height during multiplayer. '
            'Requires "Enable Upward Scrolling" to be unchecked.')
        self.Zone_mpzoomadjust.setEnabled(not self.Zone_boundflg.isChecked())
        if z.mpcamzoomadjust < 0xF:
            self.Zone_mpzoomadjust.setValue(z.mpcamzoomadjust)

        LA = QtWidgets.QFormLayout()
        LA.addRow(globals.trans.string('ZonesDlg', 48), self.Zone_yboundup)
        LA.addRow(globals.trans.string('ZonesDlg', 50), self.Zone_ybounddown)
        LA.addRow(globals.trans.string('ZonesDlg', 74), self.Zone_boundflg)
        LA.addRow('MP Screen Height Adjust:', self.Zone_mpzoomadjust)

        LB = QtWidgets.QFormLayout()
        LB.addRow(globals.trans.string('ZonesDlg', 70), self.Zone_yboundup2)
        LB.addRow(globals.trans.string('ZonesDlg', 72), self.Zone_ybounddown2)
        LB.addRow('MP Upper Bounds Adjust:', self.Zone_yboundup3)
        LB.addRow('MP Lower Bounds Adjust:', self.Zone_ybounddown3)

        cols = QtWidgets.QHBoxLayout()
        cols.addLayout(LA)
        cols.addSpacing(12)
        cols.addLayout(LB)

        w = QtWidgets.QWidget()
        L = QtWidgets.QVBoxLayout(w)
        L.setContentsMargins(8, 8, 8, 8)
        L.addLayout(cols)
        L.addStretch()
        return w

    # ── Audio ────────────────────────────────────────────────────────────────

    def _buildAudio(self, z):
        self.Zone_music = QtWidgets.QComboBox()
        self.Zone_music.setToolTip(globals.trans.string('ZonesDlg', 54))

        from . import gamedefs
        for a, b in gamedefs.getMusic():
            self.Zone_music.addItem(b, a)
        del gamedefs

        self.Zone_music.setCurrentIndex(self.Zone_music.findData(z.music))
        self.Zone_music.currentIndexChanged.connect(self.handleMusicListSelect)

        self.Zone_musicid = QtWidgets.QSpinBox()
        self.Zone_musicid.setToolTip(globals.trans.string('ZonesDlg', 69))
        self.Zone_musicid.setMaximum(255)
        self.Zone_musicid.setValue(z.music)
        self.Zone_musicid.valueChanged.connect(self.handleMusicIDChange)

        self.Zone_sfx = QtWidgets.QComboBox()
        self.Zone_sfx.setToolTip(globals.trans.string('ZonesDlg', 56))
        self.Zone_sfx.addItems(globals.trans.stringList('ZonesDlg', 57))
        self.Zone_sfx.setCurrentIndex(z.sfxmod >> 4)

        self.Zone_boss = QtWidgets.QCheckBox()
        self.Zone_boss.setToolTip(globals.trans.string('ZonesDlg', 59))
        self.Zone_boss.setChecked(bool(z.sfxmod & 0x0F))

        audioForm = QtWidgets.QFormLayout()
        audioForm.addRow(globals.trans.string('ZonesDlg', 53), self.Zone_music)
        audioForm.addRow(globals.trans.string('ZonesDlg', 68), self.Zone_musicid)
        audioForm.addRow(globals.trans.string('ZonesDlg', 55), self.Zone_sfx)
        audioForm.addRow(globals.trans.string('ZonesDlg', 58), self.Zone_boss)

        w = QtWidgets.QWidget()
        L = QtWidgets.QVBoxLayout(w)
        L.setContentsMargins(8, 8, 8, 8)
        L.addLayout(audioForm)
        L.addStretch()
        return w

    def handleMusicListSelect(self):
        if self.AutoEditMusic: return
        musicId = int(str(self.Zone_music.itemData(self.Zone_music.currentIndex())))
        self.AutoEditMusic = True
        self.Zone_musicid.setValue(musicId)
        self.AutoEditMusic = False

    def handleMusicIDChange(self):
        if self.AutoEditMusic: return
        self.AutoEditMusic = True
        self.Zone_music.setCurrentIndex(self.Zone_music.findData(self.Zone_musicid.value()))
        self.AutoEditMusic = False

    # ── Dirty tracking ───────────────────────────────────────────────────────

    def connectChanges(self, cb):
        for w in (self.Zone_xpos, self.Zone_ypos, self.Zone_width, self.Zone_height,
                  self.Zone_camunk1, self.Zone_camunk2, self.Zone_camunk3,
                  self.Zone_mpzoomadjust, self.Zone_musicid,
                  self.Zone_yboundup, self.Zone_ybounddown,
                  self.Zone_yboundup2, self.Zone_ybounddown2,
                  self.Zone_yboundup3, self.Zone_ybounddown3):
            w.valueChanged.connect(cb)
        for w in (self.Zone_visibility, self.Zone_screenheights,
                  self.Zone_directionmode, self.Zone_sfx, self.Zone_presets):
            w.currentIndexChanged.connect(cb)
        for w in (self.Zone_vspotlight, self.Zone_vfulldark,
                  self.Zone_boundflg, self.Zone_boss):
            w.stateChanged.connect(cb)
        for rb in self.Zone_cammodebuttongroup.buttons():
            rb.toggled.connect(cb)
        for cb_flag in self.Zone_settings:
            cb_flag.stateChanged.connect(cb)


class BGTab(QtWidgets.QWidget):
    def __init__(self, background):
        super().__init__()

        fname = bytes_to_string(background[4])

        # Determine if the stored name is a known preset or a custom one.
        # BGName.getTransAll() returns all translated preset names plus "Custom filename..."
        # at the end. BGName.index(name) returns that last index when the name is unknown.
        all_names   = BGName.getTransAll()
        _custom_str = 'Custom filename...'
        full_idx    = BGName.index(fname)
        is_custom   = full_idx < len(all_names) and all_names[full_idx] == _custom_str

        # Preset dropdown — no "Custom filename..." entry; that's handled by the checkbox.
        preset_names = [n for n in all_names if n != _custom_str]
        self.bgName = QtWidgets.QComboBox()
        self.bgName.addItems(preset_names)
        if not is_custom:
            self.bgName.setCurrentIndex(full_idx)
        self.bgName.activated.connect(self._handlePresetChanged)

        # Custom filename input with dv_ / .szs decorators
        self.bgFname = QtWidgets.QLineEdit()
        self.bgFname.setText(fname)
        self.bgFname.setPlaceholderText('background name')

        self._dvLabel  = QtWidgets.QLabel('dv_')
        self._szsLabel = QtWidgets.QLabel('.szs')
        filenameRow = QtWidgets.QHBoxLayout()
        filenameRow.setContentsMargins(0, 0, 0, 0)
        filenameRow.setSpacing(2)
        filenameRow.addWidget(self._dvLabel)
        filenameRow.addWidget(self.bgFname)
        filenameRow.addWidget(self._szsLabel)

        # Checkbox that switches between preset and custom modes
        self.useCustomFname = QtWidgets.QCheckBox('Use custom filename')
        self.useCustomFname.setChecked(is_custom)
        self.useCustomFname.stateChanged.connect(self._updateCustomMode)

        # Page 0: preset dropdown row
        presetPage = QtWidgets.QWidget()
        presetPageLayout = QtWidgets.QHBoxLayout(presetPage)
        presetPageLayout.setContentsMargins(0, 0, 0, 0)
        presetPageLayout.addWidget(QtWidgets.QLabel('Background:'))
        presetPageLayout.addWidget(self.bgName)

        # Page 1: custom filename row
        filePage = QtWidgets.QWidget()
        filePageLayout = QtWidgets.QHBoxLayout(filePage)
        filePageLayout.setContentsMargins(0, 0, 0, 0)
        filePageLayout.setSpacing(0)
        filePageLayout.addWidget(QtWidgets.QLabel('Filename:'))
        filePageLayout.addSpacing(8)
        filePageLayout.addWidget(self._dvLabel)
        filePageLayout.addWidget(self.bgFname)
        filePageLayout.addWidget(self._szsLabel)

        # Stack — index 0 = preset, index 1 = custom
        self._nameStack = QtWidgets.QStackedWidget()
        self._nameStack.addWidget(presetPage)
        self._nameStack.addWidget(filePage)

        # Offset / parallax controls
        self.xPos = QtWidgets.QSpinBox()
        self.xPos.setRange(-32768, 32767)
        self.xPos.setToolTip("X offset applied to the background center. No longer valid in the original game.")
        self.xPos.setValue(background[1])

        self.yPos = QtWidgets.QSpinBox()
        self.yPos.setRange(-32768, 32767)
        self.yPos.setToolTip("Y offset applied to the background center. No longer valid in the original game.")
        self.yPos.setValue(background[2])

        self.zPos = QtWidgets.QSpinBox()
        self.zPos.setRange(-32768, 32767)
        self.zPos.setToolTip("Z offset applied to the background center. No longer valid in the original game.")
        self.zPos.setValue(background[3])

        self.parallaxMode = QtWidgets.QComboBox()
        self.parallaxMode.addItems((
            "Y Offset Off, All Parallax On",
            "Y Offset On, All Parallax On",
            "Y Offset On, All Parallax Off",
            "Y Offset On, Y Parallax Off",
            "Y Offset On, X Parallax Off",
        ))
        self.parallaxMode.setToolTip("Parallax Mode from NSMB2. No longer valid in the original game.")
        self.parallaxMode.setCurrentIndex(background[5])

        self.preview = QtWidgets.QLabel()
        self.preview.setAlignment(Qt.AlignCenter)

        self._filenameLabel = QtWidgets.QLabel()
        self._filenameLabel.setAlignment(Qt.AlignCenter)
        self._filenameLabel.setStyleSheet('font-size: 10px;')

        settingsForm = QtWidgets.QFormLayout()
        settingsForm.setContentsMargins(0, 0, 0, 0)
        settingsForm.addRow('X Offset:',      self.xPos)
        settingsForm.addRow('Y Offset:',      self.yPos)
        settingsForm.addRow('Z Offset:',      self.zPos)
        settingsForm.addRow('Parallax Mode:', self.parallaxMode)

        mainLayout = QtWidgets.QVBoxLayout(self)
        mainLayout.setContentsMargins(8, 8, 8, 8)
        mainLayout.setSpacing(6)
        mainLayout.addWidget(self.preview)
        mainLayout.addWidget(self._filenameLabel)
        mainLayout.addWidget(self.useCustomFname)
        mainLayout.addWidget(self._nameStack)
        mainLayout.addWidget(createHorzLine())
        mainLayout.addLayout(settingsForm)
        mainLayout.addStretch()

        self.bgFname.textChanged.connect(self.updatePreview)
        self._updateCustomMode()
        self.updatePreview()

    def _updateCustomMode(self):
        """Swap the visible row between preset dropdown and custom filename input."""
        custom = self.useCustomFname.isChecked()
        self._nameStack.setCurrentIndex(1 if custom else 0)
        if not custom:
            self.bgFname.setText(BGName.getNameForTrans(self.bgName.currentText()))
        self.updatePreview()

    def connectChanges(self, cb):
        self.bgName.activated.connect(cb)
        self.bgFname.textChanged.connect(cb)
        self.useCustomFname.stateChanged.connect(cb)
        for w in (self.xPos, self.yPos, self.zPos):
            w.valueChanged.connect(cb)
        self.parallaxMode.currentIndexChanged.connect(cb)

    def _handlePresetChanged(self):
        if not self.useCustomFname.isChecked():
            self.bgFname.setText(BGName.getNameForTrans(self.bgName.currentText()))
        self.updatePreview()

    def updatePreview(self):
        if self.useCustomFname.isChecked():
            filename = os.path.join(globals.miyamoto_path, 'miyamotodata', 'bg', 'no_preview.png')
        else:
            folders = globals.gamedef.recursiveFiles('bg', False, True)
            folders.append(os.path.join(globals.miyamoto_path, 'miyamotodata', 'bg'))
            for folder in folders:
                filename = os.path.join(folder, self.bgName.currentText() + '.png')
                if os.path.isfile(filename):
                    break
            else:
                filename = os.path.join(globals.miyamoto_path, 'miyamotodata', 'bg', 'no_preview.png')

        pix = QtGui.QPixmap(filename)
        self.preview.setPixmap(pix)

        name = self.bgFname.text()
        self._filenameLabel.setText(f'dv_{name}.szs' if name else '')


class ScreenCapChoiceDialog(QtWidgets.QDialog):
    """
    Dialog which lets you choose which zone to take a pic of
    """

    def __init__(self):
        """
        Creates and initializes the dialog
        """
        super().__init__()
        self.setWindowTitle(globals.trans.string('ScrShtDlg', 0))
        self.setWindowIcon(GetIcon('screenshot'))

        self.zoneCombo = QtWidgets.QComboBox()
        self.zoneCombo.addItem(globals.trans.string('ScrShtDlg', 1))

        zonecount = len(globals.Area.zones)
        if zonecount:
            self.zoneCombo.addItem(globals.trans.string('ScrShtDlg', 2))
            for i in range(zonecount):
                self.zoneCombo.addItem(globals.trans.string('ScrShtDlg', 3, '[zone]', i + 1))

        self.hideBackground = QtWidgets.QCheckBox()
        self.hideBackground.setChecked(True)

        self.saveImage = QtWidgets.QCheckBox()
        self.saveImage.setChecked(True)
        self.saveImage.stateChanged.connect(self.saveImageChanged)

        self.saveClip = QtWidgets.QCheckBox()
        self.saveClip.stateChanged.connect(self.saveClipChanged)

        buttonBox = QtWidgets.QDialogButtonBox(QtWidgets.QDialogButtonBox.Ok | QtWidgets.QDialogButtonBox.Cancel)
        buttonBox.accepted.connect(self.accept)
        buttonBox.rejected.connect(self.reject)

        mainLayout = QtWidgets.QFormLayout()
        mainLayout.setLabelAlignment(QtCore.Qt.AlignRight)
        mainLayout.addRow("Target:", self.zoneCombo)
        mainLayout.addRow("Hide background:", self.hideBackground)
        mainLayout.addRow(createHorzLine())
        mainLayout.addRow("Save image to file:", self.saveImage)
        mainLayout.addRow("Copy image to clipboard:", self.saveClip)
        mainLayout.addRow(buttonBox)
        self.setLayout(mainLayout)

    def saveImageChanged(self, checked):
        if not (checked or self.saveClip.isChecked()):
            self.saveClip.setChecked(True)

    def saveClipChanged(self, checked):
        if not (checked or self.saveImage.isChecked()):
            self.saveImage.setChecked(True)


class AutoSavedInfoDialog(QtWidgets.QDialog):
    """
    Dialog which lets you know that an auto saved level exists
    """

    def __init__(self, filename):
        """
        Creates and initializes the dialog
        """
        super().__init__()
        self.setWindowTitle(globals.trans.string('AutoSaveDlg', 0))
        self.setWindowIcon(GetIcon('save'))

        mainlayout = QtWidgets.QVBoxLayout(self)

        hlayout = QtWidgets.QHBoxLayout()

        icon = QtWidgets.QLabel()
        hlayout.addWidget(icon)

        label = QtWidgets.QLabel(globals.trans.string('AutoSaveDlg', 1, '[path]', filename))
        label.setWordWrap(True)
        hlayout.addWidget(label)
        hlayout.setStretch(1, 1)

        buttonbox = QtWidgets.QDialogButtonBox(QtWidgets.QDialogButtonBox.No | QtWidgets.QDialogButtonBox.Yes)
        buttonbox.accepted.connect(self.accept)
        buttonbox.rejected.connect(self.reject)

        mainlayout.addLayout(hlayout)
        mainlayout.addWidget(buttonbox)


class AreaChoiceDialog(QtWidgets.QDialog):
    """
    Dialog which lets you choose an area
    """

    def __init__(self, areacount):
        """
        Creates and initializes the dialog
        """
        super().__init__()
        self.setWindowTitle(globals.trans.string('AreaChoiceDlg', 0))
        self.setWindowIcon(GetIcon('areas'))

        self.areaCombo = QtWidgets.QComboBox()
        for i in range(areacount):
            self.areaCombo.addItem(globals.trans.string('AreaChoiceDlg', 1, '[num]', i + 1))

        buttonBox = QtWidgets.QDialogButtonBox(QtWidgets.QDialogButtonBox.Ok | QtWidgets.QDialogButtonBox.Cancel)

        buttonBox.accepted.connect(self.accept)
        buttonBox.rejected.connect(self.reject)

        mainLayout = QtWidgets.QVBoxLayout()
        mainLayout.addWidget(self.areaCombo)
        mainLayout.addWidget(buttonBox)
        self.setLayout(mainLayout)


class PreferencesDialog(QtWidgets.QDialog):
    """
    Dialog which lets you customize Miyamoto
    """

    def __init__(self):
        """
        Creates and initializes the dialog
        """
        super().__init__()
        self.setWindowTitle(globals.trans.string('PrefsDlg', 0))
        self.setWindowIcon(GetIcon('settings'))

        # Create the tab widget
        self.tabWidget = QtWidgets.QTabWidget()
        self.tabWidget.currentChanged.connect(self.tabChanged)

        # Create other widgets
        self.infoLabel = QtWidgets.QLabel()
        self.generalTab = self.getGeneralTab()
        self.tilesetsTab = self.getTilesetsTab()
        self.editorTab = self.getEditorTab()
        self.toolbarTab = self.getToolbarTab()
        self.themesTab = self.getThemesTab(QtWidgets.QWidget)()
        self.tabWidget.addTab(self.generalTab, globals.trans.string('PrefsDlg', 1))
        self.tabWidget.addTab(self.tilesetsTab, 'Tilesets')
        self.tabWidget.addTab(self.editorTab, 'Editor')
        self.tabWidget.addTab(self.toolbarTab, globals.trans.string('PrefsDlg', 2))
        self.tabWidget.addTab(self.themesTab, globals.trans.string('PrefsDlg', 3))

        # Create the buttonbox
        buttonBox = QtWidgets.QDialogButtonBox(QtWidgets.QDialogButtonBox.Ok | QtWidgets.QDialogButtonBox.Cancel)
        buttonBox.accepted.connect(self.accept)
        buttonBox.rejected.connect(self.reject)

        # Create a main layout
        mainLayout = QtWidgets.QVBoxLayout()
        mainLayout.addWidget(self.infoLabel)
        mainLayout.addWidget(self.tabWidget)
        mainLayout.addWidget(buttonBox)
        self.setLayout(mainLayout)

        # Update it
        self.tabChanged()

    def tabChanged(self):
        """
        Handles the current tab being changed
        """
        self.infoLabel.setText(self.tabWidget.currentWidget().info)

    def getGeneralTab(self):
        """
        Returns the General Tab
        """

        class GeneralTab(QtWidgets.QWidget):
            """
            General Tab
            """
            info = globals.trans.string('PrefsDlg', 4)

            def __init__(self):
                """
                Initializes the General Tab
                """
                super().__init__()

                # Add the Clear Recent Files button
                ClearRecentBtn = QtWidgets.QPushButton(globals.trans.string('PrefsDlg', 16))
                ClearRecentBtn.setMaximumWidth(ClearRecentBtn.minimumSizeHint().width())
                ClearRecentBtn.clicked.connect(self.ClearRecent)

                # Add the Translation Language setting
                self.Trans = QtWidgets.QComboBox()
                self.Trans.setMaximumWidth(256)

                # Add the Embedded tab type determiner
                self.separate = QtWidgets.QCheckBox()
                self.separate.setChecked(globals.isEmbeddedSeparate)

                from .spritelib import RotationFPS

                # Add the pivotal rotation animation FPS specifier
                self.rotationFPS = QtWidgets.QSpinBox()
                self.rotationFPS.setMaximumWidth(256)
                self.rotationFPS.setRange(1, 60)
                self.rotationFPS.setValue(RotationFPS)

                del RotationFPS

                # Add the File Opening Behavior setting
                self.openMethod = QtWidgets.QComboBox()
                self.openMethod.addItems(["Always Ask", "Same Window", "New Window"])
                self.openMethod.setCurrentIndex(setting('OpenMethodMode', 0))

                # Create the main layout
                L = QtWidgets.QFormLayout()
                L.addRow(globals.trans.string('PrefsDlg', 14), self.Trans)
                L.addRow(globals.trans.string('PrefsDlg', 15), ClearRecentBtn)
                L.addRow(globals.trans.string('PrefsDlg', 43), self.separate)
                L.addRow(globals.trans.string('PrefsDlg', 45), self.rotationFPS)
                L.addRow("File opening behavior:", self.openMethod)

                self.setLayout(L)

                # Set the buttons
                self.Reset()

            def Reset(self):
                """
                Read the preferences and check the respective boxes
                """
                self.Trans.addItem('English')
                self.Trans.setItemData(0, None, Qt.UserRole)
                self.Trans.setCurrentIndex(0)
                i = 1
                _trans_dir = os.path.join(globals.miyamoto_path, 'miyamotodata', 'translations')
                for trans in os.listdir(_trans_dir):
                    if trans.lower() == 'english': continue

                    fp = os.path.join(_trans_dir, trans, 'main.xml')
                    if not os.path.isfile(fp): continue

                    transobj = MiyamotoTranslation(trans)
                    name = transobj.name
                    self.Trans.addItem(name)
                    self.Trans.setItemData(i, trans, Qt.UserRole)
                    if trans == str(setting('Translation')):
                        self.Trans.setCurrentIndex(i)
                    i += 1

            def ClearRecent(self):
                """
                Handle the Clear Recent Files button being clicked
                """
                ans = QtWidgets.QMessageBox.question(None, globals.trans.string('PrefsDlg', 17), globals.trans.string('PrefsDlg', 18), QtWidgets.QMessageBox.Yes, QtWidgets.QMessageBox.No)
                if ans != QtWidgets.QMessageBox.Yes: return
                globals.mainWindow.RecentMenu.clearAll()

        return GeneralTab()

    def getTilesetsTab(self):
        """
        Returns the Tilesets Tab
        """

        class TilesetsTab(QtWidgets.QWidget):
            """
            Tilesets Tab
            """
            info = "<b>Tilesets</b><br>Configure how tilesets are compressed and saved."

            def __init__(self):
                """
                Initializes the Tilesets Tab
                """
                super().__init__()

                self.useRGBA8 = QtWidgets.QCheckBox("Use RGBA8 lossless compression")
                self.useRGBA8.setChecked(globals.UseRGBA8)

                self.alwaysRepack = QtWidgets.QCheckBox("Always repack tilesets on level save")
                self.alwaysRepack.setChecked(setting('OverrideTilesetSaving', False))

                self.autoSave = QtWidgets.QCheckBox("Auto-save tilesets")
                self.autoSave.setToolTip("Skips the save confirmation dialog when closing the tileset editor.")
                self.autoSave.setChecked(setting('AutoSaveTilesets', False))

                # Create the main layout
                L = QtWidgets.QVBoxLayout()
                L.addWidget(self.useRGBA8)
                L.addWidget(self.alwaysRepack)
                L.addWidget(self.autoSave)
                L.addStretch(1)

                self.setLayout(L)

        return TilesetsTab()

    def getEditorTab(self):
        """
        Returns the Editor Tab
        """

        class EditorTab(QtWidgets.QWidget):
            """
            Editor preferences tab — sprite data display and level editing options.
            """
            info = "<b>Editor</b><br>Configure sprite data display and level editing behavior."

            def __init__(self):
                super().__init__()

                # --- Sprite Data group ---
                self.categorizedSpriteData = QtWidgets.QCheckBox("Categorized sprite data")
                self.categorizedSpriteData.setToolTip(
                    "When enabled, actor flags in the sprite data editor are grouped into "
                    "tabbed categories (Behavior, Movement, Events, Uncategorized) for "
                    "easier navigation."
                )
                self.categorizedSpriteData.setChecked(globals.CategorizedSpriteData)

                spriteDataGroup = QtWidgets.QGroupBox("Sprite Data")
                spriteDataLayout = QtWidgets.QVBoxLayout()
                spriteDataLayout.addWidget(self.categorizedSpriteData)
                spriteDataGroup.setLayout(spriteDataLayout)

                # --- Level Editing group ---
                self.overwriteActors = QtWidgets.QCheckBox("Don't overwrite actors in the level archive")
                self.overwriteActors.setToolTip(
                    "When enabled, actors already in the level's archive will not be replaced "
                    "by actors from the game data folder."
                )
                self.overwriteActors.setChecked(not globals.OverwriteSprite)

                self.placeFullSize = QtWidgets.QCheckBox("Place objects at their full size")
                self.placeFullSize.setToolTip(
                    "When enabled, right-clicking to place an object in the level canvas places it "
                    "at its full width and height instead of as a 1×1 tile."
                )
                self.placeFullSize.setChecked(globals.PlaceObjectFullSize)

                levelGroup = QtWidgets.QGroupBox("Level Editing")
                levelLayout = QtWidgets.QVBoxLayout()
                levelLayout.addWidget(self.overwriteActors)
                levelLayout.addWidget(self.placeFullSize)
                levelGroup.setLayout(levelLayout)

                # --- Palette group ---
                self.spriteListPreview = QtWidgets.QComboBox()
                self.spriteListPreview.addItem('Disabled',      globals.SPRITE_PREVIEW_DISABLED)
                self.spriteListPreview.addItem('Small (24 px)', globals.SPRITE_PREVIEW_SMALL)
                self.spriteListPreview.addItem('Medium (40 px)', globals.SPRITE_PREVIEW_MEDIUM)
                self.spriteListPreview.addItem('Large (56 px)', globals.SPRITE_PREVIEW_LARGE)
                cur = globals.SpriteListPreviewSize
                for i in range(self.spriteListPreview.count()):
                    if self.spriteListPreview.itemData(i) == cur:
                        self.spriteListPreview.setCurrentIndex(i)
                        break

                previewRow = QtWidgets.QHBoxLayout()
                previewRow.addWidget(QtWidgets.QLabel('Actor list preview size:'))
                previewRow.addWidget(self.spriteListPreview)
                previewRow.addStretch()

                paletteGroup = QtWidgets.QGroupBox("Palette")
                paletteLayout = QtWidgets.QVBoxLayout()
                paletteLayout.addLayout(previewRow)
                paletteGroup.setLayout(paletteLayout)

                L = QtWidgets.QVBoxLayout()
                L.addWidget(spriteDataGroup)
                L.addWidget(levelGroup)
                L.addWidget(paletteGroup)
                L.addStretch(1)
                self.setLayout(L)

        return EditorTab()

    def getToolbarTab(self):
        """
        Returns the Toolbar Tab
        """

        class ToolbarTab(QtWidgets.QWidget):
            """
            Toolbar Tab
            """
            info = globals.trans.string('PrefsDlg', 5)

            def __init__(self):
                """
                Initializes the Toolbar Tab
                """
                super().__init__()

                # Determine which keys are activated
                if setting('ToolbarActs') in (None, 'None', 'none', '', 0):
                    # Get the default settings
                    toggled = {}
                    for List in (globals.FileActions, globals.EditActions, globals.ViewActions, globals.SettingsActions, globals.SpritedataActions, globals.HelpActions):
                        for name, activated, key in List:
                            toggled[key] = activated
                else:  # Get the registry settings
                    toggled = setting('ToolbarActs')
                    newToggled = {}  # here, I'm replacing QStrings w/ python strings
                    for key in toggled:
                        newToggled[str(key)] = toggled[key]
                    toggled = newToggled

                # Create some data
                self.FileBoxes = []
                self.EditBoxes = []
                self.ViewBoxes = []
                self.SettingsBoxes = []
                self.SpritedataBoxes = []
                self.HelpBoxes = []
                FL = QtWidgets.QVBoxLayout()
                EL = QtWidgets.QVBoxLayout()
                VL = QtWidgets.QVBoxLayout()
                SL = QtWidgets.QVBoxLayout()
                SDL = QtWidgets.QVBoxLayout()
                HL = QtWidgets.QVBoxLayout()
                FB = QtWidgets.QGroupBox(globals.trans.string('Menubar', 0))
                EB = QtWidgets.QGroupBox(globals.trans.string('Menubar', 1))
                VB = QtWidgets.QGroupBox(globals.trans.string('Menubar', 2))
                SB = QtWidgets.QGroupBox(globals.trans.string('Menubar', 3))
                SDB = QtWidgets.QGroupBox('Spritedata')
                HB = QtWidgets.QGroupBox(globals.trans.string('Menubar', 5))

                # Arrange this data so it can be iterated over
                menuItems = (
                    (globals.FileActions, self.FileBoxes, FL, FB),
                    (globals.EditActions, self.EditBoxes, EL, EB),
                    (globals.ViewActions, self.ViewBoxes, VL, VB),
                    (globals.SettingsActions, self.SettingsBoxes, SL, SB),
                    (globals.SpritedataActions, self.SpritedataBoxes, SDL, SDB),
                    (globals.HelpActions, self.HelpBoxes, HL, HB),
                )

                # Set up the menus by iterating over the above data
                for defaults, boxes, layout, group in menuItems:
                    for L, C, I in defaults:
                        box = QtWidgets.QCheckBox(L)
                        boxes.append(box)
                        layout.addWidget(box)
                        try:
                            box.setChecked(toggled[I])
                        except KeyError:
                            pass
                        box.InternalName = I  # to save settings later
                    group.setLayout(layout)

                # Create the always-enabled Current Area checkbox
                CurrentArea = QtWidgets.QCheckBox(globals.trans.string('PrefsDlg', 19))
                CurrentArea.setChecked(True)
                CurrentArea.setEnabled(False)

                # Create the Reset button
                reset = QtWidgets.QPushButton(globals.trans.string('PrefsDlg', 20))
                reset.clicked.connect(self.reset)

                # Create the main layout
                L = QtWidgets.QGridLayout()
                L.addWidget(reset, 0, 0, 1, 1)
                L.addWidget(FB, 1, 0, 3, 1)
                L.addWidget(EB, 1, 1, 3, 1)
                L.addWidget(VB, 1, 2, 3, 1)
                L.addWidget(SB, 1, 3, 1, 1)
                L.addWidget(SDB, 2, 3, 1, 1)
                L.addWidget(HB, 3, 3, 1, 1)
                L.addWidget(CurrentArea, 4, 3, 1, 1)
                self.setLayout(L)

            def reset(self):
                """
                This is called when the Reset button is clicked
                """
                items = (
                    (self.FileBoxes, globals.FileActions),
                    (self.EditBoxes, globals.EditActions),
                    (self.ViewBoxes, globals.ViewActions),
                    (self.SettingsBoxes, globals.SettingsActions),
                    (self.SpritedataBoxes, globals.SpritedataActions),
                    (self.HelpBoxes, globals.HelpActions)
                )

                for boxes, defaults in items:
                    for box, default in zip(boxes, defaults):
                        box.setChecked(default[1])

        return ToolbarTab()

    @staticmethod
    def getThemesTab(parent):
        """
        Returns the Themes Tab
        """

        class ThemesTab(parent):
            """
            Themes Tab
            """
            info = globals.trans.string('PrefsDlg', 6)

            def __init__(self):
                """
                Initializes the Themes Tab
                """
                super().__init__()

                # Get the current and available themes
                self.themeID = globals.theme.themeName
                self.themes = self.getAvailableThemes

                # Create the theme box
                self.themeBox = QtWidgets.QComboBox()
                for name, themeObj in self.themes:
                    self.themeBox.addItem(name)

                index = self.themeBox.findText(setting('Theme'), Qt.MatchFixedString)
                if index >= 0:
                     self.themeBox.setCurrentIndex(index)

                self.themeBox.currentIndexChanged.connect(self.UpdatePreview)

                boxGB = QtWidgets.QGroupBox('Themes')
                L = QtWidgets.QFormLayout()
                L.addRow('Theme:', self.themeBox)
                L2 = QtWidgets.QGridLayout()
                L2.addLayout(L, 0, 0)
                boxGB.setLayout(L2)

                # Create the preview labels and groupbox
                self.preview = QtWidgets.QLabel()
                self.description = QtWidgets.QLabel()
                L = QtWidgets.QVBoxLayout()
                L.addWidget(self.preview)
                L.addWidget(self.description)
                L.addStretch(1)
                previewGB = QtWidgets.QGroupBox(globals.trans.string('PrefsDlg', 22))
                previewGB.setLayout(L)

                # Create the options box options
                keys = QtWidgets.QStyleFactory().keys()
                self.NonWinStyle = QtWidgets.QComboBox()
                self.NonWinStyle.setToolTip(globals.trans.string('PrefsDlg', 24))
                self.NonWinStyle.addItems(keys)
                uistyle = setting('uiStyle', "Fusion")
                if uistyle is not None:
                    self.NonWinStyle.setCurrentIndex(keys.index(setting('uiStyle', "Fusion")))

                # Create the options groupbox
                L = QtWidgets.QVBoxLayout()
                L.addWidget(self.NonWinStyle)
                optionsGB = QtWidgets.QGroupBox(globals.trans.string('PrefsDlg', 25))
                optionsGB.setLayout(L)

                # Create a main layout
                Layout = QtWidgets.QGridLayout()
                Layout.addWidget(boxGB, 0, 0)
                Layout.addWidget(optionsGB, 0, 1)
                Layout.addWidget(previewGB, 1, 1)
                Layout.setRowStretch(1, 1)
                self.setLayout(Layout)

                # Update the preview things
                self.UpdatePreview()

            @property
            def getAvailableThemes(self):
                """Searches the Themes folder and returns a list of theme filepaths.
                Automatically adds 'Classic' to the list."""
                _themes_dir = os.path.join(globals.miyamoto_path, 'miyamotodata', 'themes')
                themes = os.listdir(_themes_dir)
                themeList = [('Classic', MiyamotoTheme())]
                for themeName in themes:
                    if os.path.isdir(os.path.join(_themes_dir, themeName)):
                        try:
                            theme = MiyamotoTheme(themeName)
                            themeList.append((themeName, theme))
                        except Exception:
                            pass

                return tuple(themeList)

            def UpdatePreview(self):
                """
                Updates the preview and theme box
                """
                theme = self.themeBox.currentText()
                style = self.NonWinStyle.currentText()

                themeObj = MiyamotoTheme(theme)
                keys = QtWidgets.QStyleFactory().keys()

                if themeObj.color('ui') is not None and not themeObj.forceStyleSheet:
                    styles = ["WindowsXP", "WindowsVista"]
                    for _style in styles:
                        for key in _style, _style.lower():
                            if key in keys:
                                keys.remove(key)

                    if style in styles + [_style.lower() for _style in styles]:
                        style = "Fusion"

                self.NonWinStyle.clear()
                self.NonWinStyle.addItems(keys)
                self.NonWinStyle.setCurrentIndex(keys.index(style))

                for name, themeObj in self.themes:
                    if name == self.themeBox.currentText():
                        t = themeObj
                        self.preview.setPixmap(self.drawPreview(t))
                        text = globals.trans.string('PrefsDlg', 26, '[name]', t.themeName, '[creator]', t.creator,
                                            '[description]', t.description)
                        self.description.setText(text)

            def drawPreview(self, theme):
                """
                Returns a preview pixmap for the given theme
                """

                tilewidth = 24
                width = int(21.875 * tilewidth)
                height = int(11.5625 * tilewidth)

                # Set up some things
                px = QtGui.QPixmap(width, height)
                px.fill(theme.color('bg'))

                paint = QtGui.QPainter(px)

                font = QtGui.QFont(globals.NumberFont) # need to make a new instance to avoid changing global settings
                font.setPointSize(6)
                paint.setFont(font)

                # Draw the spriteboxes
                paint.setPen(QtGui.QPen(theme.color('spritebox_lines'), 1))
                paint.setBrush(QtGui.QBrush(theme.color('spritebox_fill')))

                paint.drawRoundedRect(11 * tilewidth, 4 * tilewidth, tilewidth, tilewidth, 5, 5)
                paint.drawText(QtCore.QPointF(11.25 * tilewidth, 4.6875 * tilewidth), '38')

                paint.drawRoundedRect(tilewidth, 6 * tilewidth, tilewidth, tilewidth, 5, 5)
                paint.drawText(QtCore.QPointF(1.25 * tilewidth, 6.6875 * tilewidth), '53')

                # Draw the entrance
                paint.setPen(QtGui.QPen(theme.color('entrance_lines'), 1))
                paint.setBrush(QtGui.QBrush(theme.color('entrance_fill')))

                paint.drawRoundedRect(13 * tilewidth, 8 * tilewidth, tilewidth, tilewidth, 5, 5)
                paint.drawText(QtCore.QPointF(13.25 * tilewidth, 8.625 * tilewidth), '0')

                # Draw the location
                paint.setPen(QtGui.QPen(theme.color('location_lines'), 1))
                paint.setBrush(QtGui.QBrush(theme.color('location_fill')))

                paint.drawRect(tilewidth, 9 * tilewidth, 6 * tilewidth, 2 * tilewidth)
                paint.setPen(QtGui.QPen(theme.color('location_text'), 1))
                paint.drawText(QtCore.QPointF(1.25 * tilewidth, 9.625 * tilewidth), '1')

                # Draw the zone
                paint.setPen(QtGui.QPen(theme.color('zone_lines'), 3))
                paint.setBrush(QtGui.QBrush(toQColor(0, 0, 0, 0)))
                paint.drawRect(QtCore.QRectF(8.5 * tilewidth, 3.25 * tilewidth, 16 * tilewidth, 7.5 * tilewidth))
                paint.setPen(QtGui.QPen(theme.color('zone_corner'), 3))
                paint.setBrush(QtGui.QBrush(theme.color('zone_corner'), 3))
                paint.drawRect(QtCore.QRectF(8.4375 * tilewidth, 3.1875 * tilewidth, 0.125 * tilewidth, 0.125 * tilewidth))
                paint.drawRect(QtCore.QRectF(8.4375 * tilewidth, 10.6875 * tilewidth, 0.125 * tilewidth, 0.125 * tilewidth))
                paint.setPen(QtGui.QPen(theme.color('zone_text'), 1))
                font = QtGui.QFont(globals.NumberFont)
                font.setPointSize(round((5 / 16) * tilewidth))
                paint.setFont(font)
                paint.drawText(QtCore.QPointF(8.75 * tilewidth, 3.875 * tilewidth), 'Zone 1')

                # Draw the grid
                paint.setPen(QtGui.QPen(theme.color('grid'), 1, Qt.DotLine))
                gridcoords = [i for i in range(0, width, tilewidth)]
                for i in gridcoords:
                    paint.setPen(QtGui.QPen(theme.color('grid'), 0.75, Qt.DotLine))
                    paint.drawLine(i, 0, i, height)
                    paint.drawLine(0, i, width, i)
                    if not (i / tilewidth) % (tilewidth / 4):
                        paint.setPen(QtGui.QPen(theme.color('grid'), 1.5, Qt.DotLine))
                        paint.drawLine(i, 0, i, height)
                        paint.drawLine(0, i, width, i)

                    if not (i / tilewidth) % (tilewidth / 2):
                        paint.setPen(QtGui.QPen(theme.color('grid'), 2.25, Qt.DotLine))
                        paint.drawLine(i, 0, i, height)
                        paint.drawLine(0, i, width, i)

                # Delete the painter and return the pixmap
                paint.end()
                return px

        return ThemesTab


class ChooseLevelNameDialog(QtWidgets.QDialog):
    """
    Dialog which lets you choose a level from a list
    """

    def __init__(self):
        """
        Creates and initializes the dialog
        """
        super().__init__()
        self.setWindowTitle(globals.trans.string('OpenFromNameDlg', 0))
        self.setWindowIcon(GetIcon('open'))

        self.currentlevel = None

        # create the tree
        tree = QtWidgets.QTreeWidget()
        tree.setColumnCount(1)
        tree.setHeaderHidden(True)
        tree.setIndentation(16)
        tree.currentItemChanged.connect(self.HandleItemChange)
        tree.itemActivated.connect(self.HandleItemActivated)

        # add items (globals.LevelNames is effectively a big category)
        tree.addTopLevelItems(self.ParseCategory(globals.LevelNames))

        # assign it to self.leveltree
        self.leveltree = tree

        # create the buttons
        self.buttonBox = QtWidgets.QDialogButtonBox(QtWidgets.QDialogButtonBox.Ok | QtWidgets.QDialogButtonBox.Cancel)
        self.buttonBox.button(QtWidgets.QDialogButtonBox.Ok).setEnabled(False)

        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)

        # create the layout
        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(self.leveltree)
        layout.addWidget(self.buttonBox)

        self.setLayout(layout)
        self.layout = layout

        self.setMinimumWidth(320)  # big enough to fit "World 5: Freezeflame Volcano/Freezeflame Glacier"
        self.setMinimumHeight(384)

    def ParseCategory(self, items):
        """
        Parses a XML category
        """
        nodes = []
        for item in items:
            node = QtWidgets.QTreeWidgetItem()
            node.setText(0, item[0])
            # see if it's a category or a level
            if isinstance(item[1], str):
                # it's a level
                node.setData(0, Qt.UserRole, item[1])
                node.setToolTip(0, item[1])
            else:
                # it's a category
                children = self.ParseCategory(item[1])
                for cnode in children:
                    node.addChild(cnode)
                node.setToolTip(0, item[0])
            nodes.append(node)
        return tuple(nodes)

    def HandleItemChange(self, current, previous):
        """
        Catch the selected level and enable/disable OK button as needed
        """
        self.currentlevel = current.data(0, Qt.UserRole)
        if self.currentlevel is None:
            self.buttonBox.button(QtWidgets.QDialogButtonBox.Ok).setEnabled(False)
        else:
            self.buttonBox.button(QtWidgets.QDialogButtonBox.Ok).setEnabled(True)
            self.currentlevel = str(self.currentlevel)

    def HandleItemActivated(self, item, column):
        """
        Handle a doubleclick on a level
        """
        self.currentlevel = item.data(0, Qt.UserRole)
        if self.currentlevel is not None:
            self.currentlevel = str(self.currentlevel)
            self.accept()
