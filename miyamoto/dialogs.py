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
from .misc import HexSpinBox, BGName, setting, hasLevelNameSources
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
    The About info for Pyamoto
    """

    def __init__(self):
        """
        Creates and initializes the dialog
        """
        super().__init__()
        self.setWindowTitle('About Pyamoto')
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)

        import platform as _platform
        icon_name = 'pyamoto1024mac.png' if _platform.system() == 'Darwin' else 'pyamoto1024.png'
        icon_path = os.path.join(globals.miyamoto_path, 'miyamotodata', icon_name)
        if os.path.isfile(icon_path):
            self.setWindowIcon(QtGui.QIcon(icon_path))
        else:
            self.setWindowIcon(GetIcon('help'))

        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(36, 28, 36, 20)
        layout.setSpacing(0)

        # Logo
        if os.path.isfile(icon_path):
            logo = QtWidgets.QLabel()
            logo.setAlignment(Qt.AlignHCenter)
            dpr = QtWidgets.QApplication.instance().devicePixelRatio()
            physical = int(108 * dpr)
            pix = QtGui.QPixmap(icon_path).scaled(physical, physical, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            pix.setDevicePixelRatio(dpr)
            logo.setPixmap(pix)
            logo.setFixedHeight(108)
            layout.addWidget(logo)
            layout.addSpacing(14)

        # Heading
        heading = QtWidgets.QLabel('Pyamoto Level Editor')
        heading.setAlignment(Qt.AlignHCenter)
        hf = heading.font()
        hf.setPointSize(hf.pointSize() + 5)
        hf.setBold(True)
        heading.setFont(hf)
        layout.addWidget(heading)
        layout.addSpacing(4)

        # Version
        ver = QtWidgets.QLabel('v' + globals.MiyamotoVersion)
        ver.setAlignment(Qt.AlignHCenter)
        ver.setStyleSheet('color: palette(mid);')
        layout.addWidget(ver)
        layout.addSpacing(16)

        # Description
        desc = QtWidgets.QLabel(
            'An advanced fork of the original Miyamoto editor with the purpose of '
            'improving functionality and usability for creating New Super Mario Bros. U levels.')
        desc.setAlignment(Qt.AlignHCenter)
        desc.setWordWrap(True)
        desc.setStyleSheet('color: palette(text);')
        layout.addWidget(desc)
        layout.addSpacing(16)

        # Separator
        sep = QtWidgets.QFrame()
        sep.setFrameShape(QtWidgets.QFrame.HLine)
        sep.setFrameShadow(QtWidgets.QFrame.Sunken)
        layout.addWidget(sep)
        layout.addSpacing(12)

        # Resources heading
        res_hdr = QtWidgets.QLabel('Resources')
        hdr_font = res_hdr.font()
        hdr_font.setPointSize(hdr_font.pointSize() - 1)
        hdr_font.setBold(True)
        res_hdr.setFont(hdr_font)
        res_hdr.setStyleSheet('color: palette(mid);')
        res_hdr.setAlignment(Qt.AlignHCenter)
        layout.addWidget(res_hdr)
        layout.addSpacing(8)

        # Links
        links = QtWidgets.QLabel(
            '<html><body style="text-align:center;">'
            '&#x1F30D; <a href="https://github.com/Zenith-Team/Pyamoto">GitHub</a>'
            ' &nbsp;&middot;&nbsp; '
            '&#x1F4AC; <a href="https://go.nsmbu.net/discord">Discord</a>'
            ' &nbsp;&middot;&nbsp; '
            '&#x1F4D6; <a href="https://zenith.nsmbu.net/">Wiki</a>'
            '</body></html>')
        links.setTextFormat(Qt.RichText)
        links.setOpenExternalLinks(True)
        links.setAlignment(Qt.AlignHCenter)
        layout.addWidget(links)
        layout.addSpacing(16)

        # Credits
        credits = QtWidgets.QLabel(
            '<html><body style="text-align:center;">'
            'Maintained by <b>Zenith Team</b>.<br>'
            '</body></html>')
        credits.setAlignment(Qt.AlignHCenter)
        credits.setStyleSheet('color: palette(mid); font-size: 11px;')
        layout.addWidget(credits)
        layout.addSpacing(20)

        # OK button
        btn = QtWidgets.QPushButton('OK')
        btn.setFixedHeight(36)
        btn.clicked.connect(self.accept)
        layout.addWidget(btn)

        self.adjustSize()
        self.setFixedSize(440, self.sizeHint().height())


class ObjectShiftDialog(QtWidgets.QDialog):
    """
    Lets you pick an amount to shift selected items by
    """

    def __init__(self):
        """
        Creates and initializes the dialog
        """
        super().__init__()
        self.setWindowTitle('Shift Items')
        self.setWindowIcon(GetIcon('move'))

        self.XOffset = QtWidgets.QSpinBox()
        self.XOffset.setRange(-16384, 16383)

        self.YOffset = QtWidgets.QSpinBox()
        self.YOffset.setRange(-8192, 8191)

        buttonBox = QtWidgets.QDialogButtonBox(QtWidgets.QDialogButtonBox.Ok | QtWidgets.QDialogButtonBox.Cancel)
        buttonBox.accepted.connect(self.accept)
        buttonBox.rejected.connect(self.reject)

        moveLayout = QtWidgets.QFormLayout()
        offsetlabel = QtWidgets.QLabel("Enter an offset in pixels - each block is 16 pixels in size. Note that normal objects can only be placed on 16x16 boundaries, so if the offset you enter isn't a multiple of 16, they won't be moved correctly.")
        offsetlabel.setWordWrap(True)
        moveLayout.addWidget(offsetlabel)
        moveLayout.addRow('X:', self.XOffset)
        moveLayout.addRow('Y:', self.YOffset)

        moveGroupBox = QtWidgets.QGroupBox('Move objects by:')
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
        self.setWindowTitle('Level Information')
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

        self.changepw = QtWidgets.QPushButton('Add/Change Password')

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

        self.lockedLabel = QtWidgets.QLabel("This level's information is locked.<br>Please enter the password below in order to modify it.")

        infoLayout = QtWidgets.QFormLayout()
        infoLayout.addWidget(self.lockedLabel)
        infoLayout.addRow('Password:', self.Password)
        infoLayout.addRow('Title:', self.levelName)
        infoLayout.addRow('Author:', self.Author)
        infoLayout.addRow('Group:', self.Group)
        infoLayout.addRow('Website:', self.Website)

        self.PasswordLabel = infoLayout.labelForField(self.Password)

        levelIsLocked = password != ''
        self.lockedLabel.setVisible(levelIsLocked)
        self.PasswordLabel.setVisible(levelIsLocked)
        self.Password.setVisible(levelIsLocked)

        infoGroupBox = QtWidgets.QGroupBox('Created with [name]'.replace('[name]', str(creator)))
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
                self.setWindowTitle('Change Password')
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
                infoLayout.addRow('New Password:', self.New)
                infoLayout.addRow('Verify Password:', self.Verify)

                infoGroupBox = QtWidgets.QGroupBox('Level Information')

                infoLabel = QtWidgets.QVBoxLayout()
                infoLabel.addWidget(QtWidgets.QLabel('Password may be composed of any ASCII character,<br>and up to 64 characters long.<br>'), 0, Qt.AlignCenter)
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
        self.setWindowTitle('Area Options')
        self.setWindowIcon(GetIcon('area'))

        self.tabWidget = QtWidgets.QTabWidget()
        self.LoadingTab = LoadingTab()
        self.TilesetsTab = TilesetsTab()
        self.tabWidget.addTab(self.TilesetsTab, 'Tilesets')
        self.tabWidget.addTab(self.LoadingTab, 'Settings')

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

        self.tabWidget.tabBarClicked.connect(self.NewButtonTab)
        self.tabWidget.setTabBarAutoHide(True)

        for i, z in enumerate(globals.Area.zones):
            self._addZoneTab(z, i)
        self._addNewButtonTab()

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

    def _addNewButtonTab(self):
        newBtn = QtWidgets.QPushButton('New')
        cloneBtn = QtWidgets.QPushButton('Duplicate')
        deleteBtn = QtWidgets.QPushButton('Delete')
        newBtn.clicked.connect(self.NewZone)
        cloneBtn.setEnabled(False)
        deleteBtn.setEnabled(False)

        zoneBtnRow = QtWidgets.QHBoxLayout()
        zoneBtnRow.setContentsMargins(0, 0, 0, 0)
        zoneBtnRow.addWidget(newBtn)
        zoneBtnRow.addWidget(cloneBtn)
        zoneBtnRow.addWidget(deleteBtn)

        container = QtWidgets.QWidget()
        cLayout = QtWidgets.QVBoxLayout(container)
        cLayout.setContentsMargins(6, 6, 6, 6)
        cLayout.setSpacing(5)
        cLayout.addLayout(zoneBtnRow)
        cLayout.setAlignment(Qt.AlignBottom)

        self.tabWidget.addTab(container, '+')

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
        newBtn = QtWidgets.QPushButton('New')
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
        self.tabWidget.insertTab(len(self.zoneTabs) - 1, container, label)

        # Dirty tracking — *args absorbs the signal's emitted value so _zt is never overwritten
        def markDirty(*_, _zt=zoneTab):
            self._markTabDirty(_zt)

        zoneTab.connectChanges(markDirty)
        bgTab.connectChanges(markDirty)

    def _zoneLabel(self, idx):
        return 'Zone [num]'.replace('[num]', str(idx + 1))

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

        count = len(self.zoneTabs)
        self.tabWidget.setTabEnabled(self.tabWidget.count() - 1, count < 8)

    def _renormalizeLabels(self):
        count = len(self.zoneTabs)
        for i in range(count):
            label = 'Zone [num]'.replace('[num]', str(i + 1))
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
                self, 'Warning', 'You are trying to add more than 15 zones to a level - keep in mind that without the proper fix to the game, this will cause your level to <b>crash</b> or have other strange issues!<br><br>Are you sure you want to do this?',
                QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)
            if result == QtWidgets.QMessageBox.No:
                return

        idx = len(self.zoneTabs)
        z = ZoneItem(256, 256, 448, 224, 0, 0, idx, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0,
                     (0, 0, 0, 0, 0, 0xF, 0, 0), (0, 0, 0, 0, to_bytes('Black', 16), 0))
        self._addZoneTab(z, idx)
        self._renormalizeLabels()
        self._updateButtonStates()
        self.tabWidget.setCurrentIndex(len(self.zoneTabs) - 1)

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
        self.tabWidget.setCurrentIndex(curindex - 1)

    def CloneZone(self):
        if len(self.zoneTabs) >= 15:
            result = QtWidgets.QMessageBox.warning(
                self, 'Warning', 'You are trying to add more than 15 zones to a level - keep in mind that without the proper fix to the game, this will cause your level to <b>crash</b> or have other strange issues!<br><br>Are you sure you want to do this?',
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
        self.tabWidget.setCurrentIndex(len(self.zoneTabs) - 1)

    def NewButtonTab(self, tabIndex):
        if tabIndex == self.tabWidget.count() - 1:
            self.NewZone()


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
        self.Zone_xpos.setToolTip('<b>X position:</b><br>Sets the X Position of the upper left corner')
        self.Zone_xpos.setValue(z.objx)

        self.Zone_ypos = QtWidgets.QSpinBox()
        self.Zone_ypos.setRange(16, 65535)
        self.Zone_ypos.setToolTip('<b>Y position:</b><br>Sets the Y Position of the upper left corner')
        self.Zone_ypos.setValue(z.objy)

        self.Zone_width = QtWidgets.QSpinBox()
        self.Zone_width.setRange(80, 65535)
        self.Zone_width.setToolTip('<b>X size:</b><br>Sets the width of the zone')
        self.Zone_width.setValue(z.width)
        self.Zone_width.valueChanged.connect(self.PresetDeselected)

        self.Zone_height = QtWidgets.QSpinBox()
        self.Zone_height.setRange(16, 65535)
        self.Zone_height.setToolTip('<b>Y size:</b><br>Sets the height of the zone')
        self.Zone_height.setValue(z.height)
        self.Zone_height.valueChanged.connect(self.PresetDeselected)

        # Common retail zone presets
        self.Zone_presets_values = (
            '0: 416x224', '0: 448x224', '0: 512x272',
            '2: 560x304', '2: 608x320', '3: 704x384', '4: 944x448')
        self.Zone_presets = QtWidgets.QComboBox()
        self.Zone_presets.addItems(self.Zone_presets_values)
        self.Zone_presets.setToolTip('<b>Select Preset:</b><br>Snaps the zone to common sizes.<br>The number before each entry specifies which zoom level works best with each size.')
        self.Zone_presets.currentIndexChanged.connect(self.PresetSelected)
        self.PresetDeselected()

        self.snapButton8 = QtWidgets.QPushButton('Snap to 8x8 Grid')
        self.snapButton8.clicked.connect(lambda: self.HandleSnapTo8x8Grid(z))
        self.snapButton16 = QtWidgets.QPushButton('Snap to 16x16 Grid')
        self.snapButton16.clicked.connect(lambda: self.HandleSnapTo16x16Grid(z))

        posForm = QtWidgets.QFormLayout()
        posForm.addRow('X position:',  self.Zone_xpos)
        posForm.addRow('Y position:', self.Zone_ypos)

        sizeForm = QtWidgets.QFormLayout()
        sizeForm.addRow('X size:', self.Zone_width)
        sizeForm.addRow('Y size:', self.Zone_height)
        sizeForm.addRow('Select Preset:', self.Zone_presets)

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
        if self.Zone_presets.currentText() == '(None)': return
        w, h = self.Zone_presets.currentText()[3:].split('x')
        self.AutoChangingSize = True
        self.Zone_width.setValue(int(w))
        self.Zone_height.setValue(int(h))
        self.AutoChangingSize = False
        if self.Zone_presets.itemText(0) == '(None)':
            self.Zone_presets.removeItem(0)

    def PresetDeselected(self, info=None):
        if self.AutoChangingSize: return
        self.AutoChangingSize = True
        check = '%dx%d' % (self.Zone_width.value(), self.Zone_height.value())
        found = next((p for p in self.Zone_presets_values if check == p[3:]), None)
        if found is not None:
            self.Zone_presets.setCurrentIndex(self.Zone_presets.findText(found))
            if self.Zone_presets.itemText(0) == '(None)':
                self.Zone_presets.removeItem(0)
        else:
            if self.Zone_presets.itemText(0) != '(None)':
                self.Zone_presets.insertItem(0, '(None)')
            self.Zone_presets.setCurrentIndex(0)
        self.AutoChangingSize = False

    # ── Camera ──────────────────────────────────────────────────────────────

    def _buildCamera(self, z):
        # Spotlight / full-dark checkboxes
        self.Zone_vspotlight = QtWidgets.QCheckBox('Layer 0 Spotlight')
        self.Zone_vspotlight.setToolTip('<b>Visibility - Layer 0 Spotlight:</b><br>Sets the visibility mode to spotlight. In Spotlight mode,<br>moving behind layer 0 objects enables a spotlight that<br>follows Mario around.')
        self.Zone_vfulldark  = QtWidgets.QCheckBox('Full Darkness')
        self.Zone_vfulldark.setToolTip('<b>Visibility - Full Darkness:</b><br>Sets the visibility mode to full darkness. In full dark mode,<br>the screen is completely black and visibility is only provided<br>by the available spotlight effect. Stars and some actors<br>can enhance the default visibility.')

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

        directionmodeValues = ('Right and Down', 'Right and Up', 'Left and Down', 'Left and Up', 'Down and Right', 'Down and Left', 'Up and Right', 'Up and Left', 'Right and Right')
        self.Zone_directionmode = QtWidgets.QComboBox()
        self.Zone_directionmode.addItems(directionmodeValues)
        self.Zone_directionmode.setToolTip("<b>Camera Tracking:</b><br>This setting makes changes to camera tracking during multiplayer mode.<br>It prioritizes these directions when players goes in the wrong direction.<br>For example if you are making a tower level where the primary objective is going up<br>and you don't want the screen going back down if just one player falls,<br>then set the tracking to any value containing 'Up' and that will prevent that from happening.<br>The order of the directions is unique. Priority is most given to the first direction and the second direction is less strict.")
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
        settingsNames = ('Start Zoom as Screen Height:<br>(No initial zoom out/in)', 'Center Camera X-pos On Load:', 'Camera Follows on Y-axis:', 'Camera Stops At Zone End:', 'Unused 1:', 'Toad House Related 1:', 'Unused 2:', 'Toad House Related 2:')
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
        camForm.addRow('Camera Tracking:', self.Zone_directionmode)

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
            self.Zone_visibility.addItem('Hidden')
            self.Zone_visibility.setToolTip('<b>Visibility:</b><br>Hidden - Mario is hidden when moving behind objects on Layer 0.<br><br>Note: Entities behind layer 0 other than Mario are never visible.')
            SelectedIndex = 0
        elif self.Zone_vspotlight.isChecked() and self.Zone_vfulldark.isChecked():
            self.Zone_visibility.addItem('Small / Small Focus Light')
            self.Zone_visibility.setToolTip('<b>Visibility:</b><br>Small - A small, centered spotlight affords visibility through layer 0.<br>Small Focuslight - A small spotlight which changes size based on player movement.')
            SelectedIndex = 0
        elif self.Zone_vspotlight.isChecked():
            self.Zone_visibility.addItems(('Small', 'Large', 'Full Screen'))
            self.Zone_visibility.setToolTip('<b>Visibility:</b><br>Small - A small, centered spotlight affords visibility through layer 0.<br>Large - A large, centered spotlight affords visibility through layer 0<br>Full Screen - the entire screen is revealed whenever Mario walks behind layer 0')
            if SelectedIndex > 2: SelectedIndex = 0
        elif self.Zone_vfulldark.isChecked():
            self.Zone_visibility.addItems(('Large Foglight', 'Lightbeam', 'Large Focus Light', 'Small Foglight', 'Small Focus Light', 'Absolute Black'))
            self.Zone_visibility.setToolTip('<b>Visibility:</b><br>Large Foglight - A large, organic lightsource surrounds Mario<br>Lightbeam - Mario is able to aim a conical lightbeam through use of the Wiimote<br>Large Focus Light - A large spotlight which changes size based upon player movement<br>Small Foglight - A small, organic lightsource surrounds Mario<br>Small Focuslight - A small spotlight which changes size based on player movement<br>Absolute Black - Visibility is provided only by fireballs, stars, and certain actors')
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
        self.Zone_yboundup.setToolTip('<b>Upper Bounds:</b><br>Controls the maximum distance magnitude the player can be at from the top edge of the screen to move the camera upwards. One block = 16 units.<br><br>Values "0" and less (negative values) make scrolling upwards impossible.<br>Higher positive values mean it is easier to scroll upwards.<br>Lower positive values mean it is harder to scroll upwards.<br><br>Very high values (larger than the screen height) with a low positive "Lower Bounds" value cause instant death.')
        self.Zone_yboundup.setValue(80 + z.yupperbound)

        self.Zone_ybounddown = QtWidgets.QSpinBox()
        self.Zone_ybounddown.setRange(-32695, 32840)
        self.Zone_ybounddown.setToolTip('<b>Lower Bounds:</b><br>Controls the maximum distance magnitude the player can be at from the bottom edge of the screen to move the camera downwards. One block = 16 units.<br><br>Values "0" and less (negative values) do NOT make scrolling downwards impossible.<br>Higher positive values mean it is easier to scroll downwards.<br>Lower positive values mean it is harder to scroll downwards.<br><br>Very high values (larger than the screen height) with a low positive "Upper Bounds" value make scrolling upwards impossible.')
        self.Zone_ybounddown.setValue(72 - z.ylowerbound)

        self.Zone_yboundup2 = QtWidgets.QSpinBox()
        self.Zone_yboundup2.setRange(-32680, 32855)
        self.Zone_yboundup2.setToolTip('<b>Lakitu Upper Bounds:</b><br>Used instead of Upper Bounds when at least one player is riding a Lakitu cloud.')
        self.Zone_yboundup2.setValue(88 + z.yupperbound2)

        self.Zone_ybounddown2 = QtWidgets.QSpinBox()
        self.Zone_ybounddown2.setRange(-32679, 32856)
        self.Zone_ybounddown2.setToolTip('<b>Lakitu Lower Bounds:</b><br>Used instead of Lower Bounds when at least one player is riding a Lakitu cloud.')
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
        self.Zone_boundflg.setToolTip('<b>Enable Upward Scrolling:</b><br>If not checked and "Multiplayer Screen Height Adjust" is set to value "0", the screen won\'t scroll upwards unless the player uses a Propeller Suit or Block. Always checked in the retail game.')
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
        LA.addRow('Upper Bounds:', self.Zone_yboundup)
        LA.addRow('Lower Bounds:', self.Zone_ybounddown)
        LA.addRow('Enable Upward Scrolling:', self.Zone_boundflg)
        LA.addRow('MP Screen Height Adjust:', self.Zone_mpzoomadjust)

        LB = QtWidgets.QFormLayout()
        LB.addRow('Lakitu Upper Bounds:', self.Zone_yboundup2)
        LB.addRow('Lakitu Lower Bounds:', self.Zone_ybounddown2)
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
        self.Zone_music.setToolTip('<b>Background Music:</b><br>Changes the background music')

        from . import gamedefs
        for a, b in gamedefs.getMusic():
            self.Zone_music.addItem(b, a)
        del gamedefs

        self.Zone_music.setCurrentIndex(self.Zone_music.findData(z.music))
        self.Zone_music.currentIndexChanged.connect(self.handleMusicListSelect)

        self.Zone_musicid = QtWidgets.QSpinBox()
        self.Zone_musicid.setToolTip('<b>Background Music ID:</b><br>This advanced option allows custom music tracks to be loaded if the proper ASM hacks are in place.')
        self.Zone_musicid.setMaximum(255)
        self.Zone_musicid.setValue(z.music)
        self.Zone_musicid.valueChanged.connect(self.handleMusicIDChange)

        self.Zone_sfx = QtWidgets.QComboBox()
        self.Zone_sfx.setToolTip('<b>Sound Modulation:</b><br>Changes the sound effect modulation')
        self.Zone_sfx.addItems(('Normal', 'Wall Echo', 'Room Echo', 'Double Echo', 'Cave Echo', 'Underwater Echo', 'Triple Echo', 'High Pitch Echo', 'Tinny Echo', 'Flat', 'Dull', 'Hollow Echo', 'Rich', 'Triple Underwater', 'Ring Echo'))
        self.Zone_sfx.setCurrentIndex(z.sfxmod >> 4)

        self.Zone_boss = QtWidgets.QCheckBox()
        self.Zone_boss.setToolTip('<b>Boss Flag:</b><br>Set for bosses to allow proper music switching by actors')
        self.Zone_boss.setChecked(bool(z.sfxmod & 0x0F))

        audioForm = QtWidgets.QFormLayout()
        audioForm.addRow('Background Music:', self.Zone_music)
        audioForm.addRow('Background Music ID:', self.Zone_musicid)
        audioForm.addRow('Sound Modulation:', self.Zone_sfx)
        audioForm.addRow('Boss Flag:', self.Zone_boss)

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
        self.setWindowTitle('Choose a Screenshot source')
        self.setWindowIcon(GetIcon('screenshot'))

        self.zoneCombo = QtWidgets.QComboBox()
        self.zoneCombo.addItem('Current Screen')

        zonecount = len(globals.Area.zones)
        if zonecount:
            self.zoneCombo.addItem('All Zones')
            for i in range(zonecount):
                self.zoneCombo.addItem('Zone [zone]'.replace('[zone]', str(i + 1)))

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
        self.setWindowTitle('Auto-saved backup found')
        self.setWindowIcon(GetIcon('save'))

        mainlayout = QtWidgets.QVBoxLayout(self)

        hlayout = QtWidgets.QHBoxLayout()

        icon = QtWidgets.QLabel()
        hlayout.addWidget(icon)

        label = QtWidgets.QLabel("Pyamoto has found some level data which wasn't saved - possibly due to a crash within the editor or by your computer. Do you want to restore this level?<br><br>If you pick No, the autosaved level data will be deleted and will no longer be accessible.<br><br>Original file path: [path]".replace('[path]', str(filename)))
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
        self.setWindowTitle('Choose an Area')
        self.setWindowIcon(GetIcon('areas'))

        self.areaCombo = QtWidgets.QComboBox()
        for i in range(areacount):
            self.areaCombo.addItem('Area [num]'.replace('[num]', str(i + 1)))

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
        self.setWindowTitle('Pyamoto Preferences')
        self.setWindowIcon(GetIcon('settings'))

        # Create the tab widget
        self.tabWidget = QtWidgets.QTabWidget()
        self.tabWidget.currentChanged.connect(self.tabChanged)

        # Create tabs
        self.infoLabel = QtWidgets.QLabel()
        self.generalTab = self.getGeneralTab()   # merged General + Editor + Tilesets
        self._initial_showActorNotes = self.generalTab.showActorNotes.isChecked()
        self._initial_showInfoIcons = self.generalTab.showInfoIcons.isChecked()
        self.toolbarTab = self.getToolbarTab()
        self.themesTab = self.getThemesTab(QtWidgets.QWidget)()
        self.gameSetupTab = self.getGameSetupTab()  # merged Games + Mods

        # Backward-compat aliases so app.py attribute access still works
        self.tilesetsTab = self.generalTab
        self.editorTab = self.generalTab
        self.gamesTab = self.gameSetupTab
        self.modsTab = self.gameSetupTab

        self.tabWidget.addTab(self.generalTab, 'General')
        self.tabWidget.addTab(self.toolbarTab, 'Toolbar')
        self.tabWidget.addTab(self.themesTab, 'Themes')
        self.tabWidget.addTab(self.gameSetupTab, 'Game Setup')

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

    def needsRestart(self):
        """Returns True if the user changed a setting that requires a restart (theme, toolbar, actor notes, or info icons)."""
        if self.editorTab.showActorNotes.isChecked() != self._initial_showActorNotes:
            return True
        if self.editorTab.showInfoIcons.isChecked() != self._initial_showInfoIcons:
            return True
        if self.themesTab.themeBox.currentText() != self.themesTab._initial_theme:
            return True
        if self.themesTab.NonWinStyle.currentText() != self.themesTab._initial_style:
            return True
        initial = self.toolbarTab._initial_toolbar_acts
        for boxList in (self.toolbarTab.FileBoxes, self.toolbarTab.EditBoxes,
                        self.toolbarTab.ViewBoxes, self.toolbarTab.SettingsBoxes,
                        self.toolbarTab.SpritedataBoxes, self.toolbarTab.HelpBoxes):
            for box in boxList:
                if box.isChecked() != initial.get(box.InternalName):
                    return True
        return False

    def tabChanged(self):
        """
        Handles the current tab being changed
        """
        self.infoLabel.setText(self.tabWidget.currentWidget().info)

    def getGeneralTab(self):
        """Returns the General tab — merged General, Editor, and Tilesets sections."""

        class GeneralTab(QtWidgets.QWidget):
            info = '<b>General</b><br>Customize language, file handling, and other general settings.'

            def __init__(self):
                super().__init__()

                scroll = QtWidgets.QScrollArea()
                scroll.setWidgetResizable(True)
                scroll.setFrameShape(QtWidgets.QFrame.NoFrame)
                container = QtWidgets.QWidget()
                vbox = QtWidgets.QVBoxLayout(container)
                vbox.setSpacing(16)
                vbox.setContentsMargins(4, 4, 4, 4)

                # ── General section ──────────────────────────────────────────
                from .spritelib import RotationFPS
                self.rotationFPS = QtWidgets.QSpinBox()
                self.rotationFPS.setMaximumWidth(256)
                self.rotationFPS.setRange(1, 60)
                self.rotationFPS.setValue(RotationFPS)
                del RotationFPS

                self.openMethod = QtWidgets.QComboBox()
                self.openMethod.addItems(["Always Ask", "Same Window", "New Window"])
                self.openMethod.setCurrentIndex(setting('OpenMethodMode', 0))

                self.launchBehavior = QtWidgets.QComboBox()
                self.launchBehavior.addItems(["Show welcome page", "Open last level"])
                self.launchBehavior.setCurrentIndex(setting('LaunchBehavior', 0))

                _update_label = 'Check for updates (%s)' % globals.MiyamotoReleaseType
                self.checkForUpdates = QtWidgets.QCheckBox(_update_label)
                self.checkForUpdates.setChecked(setting('CheckForUpdates', True))

                gen_form = QtWidgets.QFormLayout()
                gen_form.addRow('File opening behavior:', self.openMethod)
                gen_form.addRow('Launch behavior:', self.launchBehavior)
                gen_lay = QtWidgets.QVBoxLayout()
                gen_lay.addLayout(gen_form)
                gen_lay.addWidget(self.checkForUpdates)
                gen_group = QtWidgets.QGroupBox('General')
                gen_group.setLayout(gen_lay)
                vbox.addWidget(gen_group)

                # ── Editor section ───────────────────────────────────────────
                self.showActorNotes = QtWidgets.QCheckBox('Show actor notes box')
                self.showActorNotes.setToolTip(
                    'When enabled, actor notes are shown in a text box within the properties panel. '
                    'When disabled, a \"Notes\" button is shown instead which displays notes in a tooltip.')
                self.showActorNotes.setChecked(setting('ShowActorNotes', True))

                self.showInfoIcons = QtWidgets.QCheckBox('Show info icons on sprite data fields')
                self.showInfoIcons.setToolTip(
                    'When enabled, a small info icon is shown next to sprite data field '
                    'labels that have a tooltip comment.')
                self.showInfoIcons.setChecked(setting('ShowInfoIcons', True))

                self.categorizedSpriteData = QtWidgets.QCheckBox('Categorized sprite data')
                self.categorizedSpriteData.setToolTip(
                    'When enabled, actor flags in the sprite data editor are grouped into '
                    'tabbed categories (Behavior, Movement, Events, Uncategorized) for '
                    'easier navigation.')
                self.categorizedSpriteData.setChecked(globals.CategorizedSpriteData)

                self.overwriteActors = QtWidgets.QCheckBox("Don't overwrite actor models in the level archive")
                self.overwriteActors.setToolTip(
                    "When enabled, actors already in the level's archive will not be replaced "
                    'by actors from the game data folder.')
                self.overwriteActors.setChecked(not globals.OverwriteSprite)

                self.placeFullSize = QtWidgets.QCheckBox('Place objects at their full size')
                self.placeFullSize.setToolTip(
                    'When enabled, right-clicking to place an object in the level canvas places it '
                    'at its full width and height instead of as a 1×1 tile.')
                self.placeFullSize.setChecked(globals.PlaceObjectFullSize)

                self.spriteListPreview = QtWidgets.QComboBox()
                self.spriteListPreview.addItem('Disabled',       globals.SPRITE_PREVIEW_DISABLED)
                self.spriteListPreview.addItem('Small (24 px)',  globals.SPRITE_PREVIEW_SMALL)
                self.spriteListPreview.addItem('Medium (40 px)', globals.SPRITE_PREVIEW_MEDIUM)
                self.spriteListPreview.addItem('Large (56 px)',  globals.SPRITE_PREVIEW_LARGE)
                cur = globals.SpriteListPreviewSize
                for i in range(self.spriteListPreview.count()):
                    if self.spriteListPreview.itemData(i) == cur:
                        self.spriteListPreview.setCurrentIndex(i)
                        break

                self.spriteListPreviewHighDetail = QtWidgets.QCheckBox('High Detail Mode')
                self.spriteListPreviewHighDetail.setToolTip(
                    'Renders preview thumbnails at the sprite\'s native resolution for '
                    'maximum quality, then scales them down to the chosen preview size.')
                self.spriteListPreviewHighDetail.setChecked(globals.SpriteListPreviewHighDetail)

                preview_row = QtWidgets.QHBoxLayout()
                preview_row.addWidget(QtWidgets.QLabel('Actor list preview size:'))
                preview_row.addWidget(self.spriteListPreview)
                preview_row.addWidget(self.spriteListPreviewHighDetail)
                preview_row.addStretch()

                ed_fps_form = QtWidgets.QFormLayout()
                ed_fps_form.addRow('Pivotal Rotation Preview FPS:', self.rotationFPS)

                ed_lay = QtWidgets.QVBoxLayout()
                ed_lay.addLayout(ed_fps_form)
                ed_lay.addWidget(self.showActorNotes)
                ed_lay.addWidget(self.showInfoIcons)
                ed_lay.addWidget(self.categorizedSpriteData)
                ed_lay.addWidget(self.overwriteActors)
                ed_lay.addWidget(self.placeFullSize)
                ed_lay.addLayout(preview_row)
                editor_group = QtWidgets.QGroupBox('Editor')
                editor_group.setLayout(ed_lay)
                vbox.addWidget(editor_group)

                # ── Tilesets section ─────────────────────────────────────────
                self.useRGBA8 = QtWidgets.QCheckBox('Use RGBA8 lossless compression')
                self.useRGBA8.setChecked(globals.UseRGBA8)

                self.alwaysRepack = QtWidgets.QCheckBox('Always repack tilesets on level save')
                self.alwaysRepack.setChecked(setting('OverrideTilesetSaving', False))

                self.autoSave = QtWidgets.QCheckBox('Auto-save tilesets')
                self.autoSave.setToolTip('Skips the save confirmation dialog when closing the tileset editor.')
                self.autoSave.setChecked(setting('AutoSaveTilesets', False))

                ts_lay = QtWidgets.QVBoxLayout()
                ts_lay.addWidget(self.useRGBA8)
                ts_lay.addWidget(self.alwaysRepack)
                ts_lay.addWidget(self.autoSave)
                tileset_group = QtWidgets.QGroupBox('Tilesets')
                tileset_group.setLayout(ts_lay)
                vbox.addWidget(tileset_group)

                vbox.addStretch(1)
                scroll.setWidget(container)
                outer = QtWidgets.QVBoxLayout(self)
                outer.setContentsMargins(0, 0, 0, 0)
                outer.addWidget(scroll)

        return GeneralTab()

    def getTilesetsTab(self):
        return self.generalTab  # merged into getGeneralTab

    def getEditorTab(self):
        return self.generalTab  # merged into getGeneralTab

    def getToolbarTab(self):
        """
        Returns the Toolbar Tab
        """

        class ToolbarTab(QtWidgets.QWidget):
            """
            Toolbar Tab
            """
            info = '<b>Toolbar</b><br>Choose which actions appear on the toolbar.'

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

                self._initial_toolbar_acts = dict(toggled)

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
                FB = QtWidgets.QGroupBox('&File')
                EB = QtWidgets.QGroupBox('&Edit')
                VB = QtWidgets.QGroupBox('&View')
                SB = QtWidgets.QGroupBox('&Area')
                SDB = QtWidgets.QGroupBox('Spritedata')
                HB = QtWidgets.QGroupBox('&Help')

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
                CurrentArea = QtWidgets.QCheckBox('Current Area')
                CurrentArea.setChecked(True)
                CurrentArea.setEnabled(False)

                # Create the Reset button
                reset = QtWidgets.QPushButton('Reset')
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

    def getGamesTab(self):
        return self.gameSetupTab  # merged into getGameSetupTab

    def getModsTab(self):
        return self.gameSetupTab  # merged into getGameSetupTab

    def getGameSetupTab(self):
        """Returns the Game Setup tab — game selection + mod management."""
        from . import gamedefs as _gd
        from .verifications import isValidGamePath

        class GameSetupTab(QtWidgets.QWidget):
            info = 'Select your base game, manage mods, and configure game paths.'

            def __init__(self_inner):
                super().__init__()

                vbox = QtWidgets.QVBoxLayout(self_inner)
                vbox.setSpacing(12)
                vbox.setContentsMargins(8, 8, 8, 8)

                # ── Game Selection ───────────────────────────────────────────
                self_inner._path_edits = {}
                self_inner._game_radios = {}

                games_group = QtWidgets.QGroupBox('Game')
                games_vbox = QtWidgets.QVBoxLayout(games_group)
                games_vbox.setSpacing(6)

                radio_group = QtWidgets.QButtonGroup(games_group)
                current_base = setting('LastBaseGame', 'NSMBU')

                base_games = _gd.getAvailableBaseGames()
                for idx_g, (def_, folder) in enumerate(base_games):
                    # Radio button = the game selector
                    radio = QtWidgets.QRadioButton(def_.name)
                    radio.setChecked(folder == current_base)
                    radio_group.addButton(radio)
                    self_inner._game_radios[folder] = radio
                    games_vbox.addWidget(radio)

                    # Path row indented under its radio button
                    indent_w = QtWidgets.QWidget()
                    indent_lay = QtWidgets.QVBoxLayout(indent_w)
                    indent_lay.setContentsMargins(22, 0, 0, 0)
                    indent_lay.setSpacing(2)

                    path_row = QtWidgets.QHBoxLayout()
                    path_edit = QtWidgets.QLineEdit()
                    path_edit.setPlaceholderText('Select the game folder…')
                    existing = setting('GamePath_' + folder,
                                       setting('GamePath', '') if folder == 'NSMBU' else '')
                    if existing:
                        path_edit.setText(str(existing))
                    self_inner._path_edits[folder] = path_edit

                    valid_lbl = QtWidgets.QLabel()
                    valid_lbl.setStyleSheet('font-size: 11px;')

                    def _make_validator(edit, lbl):
                        def _v():
                            p = edit.text().strip()
                            ok = isValidGamePath(p) if p else False
                            lbl.setText('✓ Valid' if ok else ('✗ Not set' if not p else '✗ Invalid path'))
                            lbl.setStyleSheet('color: green; font-size: 11px;' if ok
                                              else 'color: palette(mid); font-size: 11px;' if not p
                                              else 'color: red; font-size: 11px;')
                        edit.textChanged.connect(_v)
                        _v()

                    _make_validator(path_edit, valid_lbl)

                    def _make_browser(edit, fn=folder):
                        def _b():
                            p = QtWidgets.QFileDialog.getExistingDirectory(
                                None, f'Select {fn} game folder', edit.text())
                            if p:
                                edit.setText(p)
                        return _b

                    browse_btn = QtWidgets.QPushButton('Browse…')
                    browse_btn.clicked.connect(_make_browser(path_edit))

                    path_row.addWidget(path_edit)
                    path_row.addWidget(browse_btn)
                    indent_lay.addLayout(path_row)
                    indent_lay.addWidget(valid_lbl)
                    games_vbox.addWidget(indent_w)

                    if idx_g < len(base_games) - 1:
                        games_vbox.addSpacing(4)

                vbox.addWidget(games_group)

                # ── Mod Selection header ──────────────────────────────────────
                mod_header_row = QtWidgets.QHBoxLayout()

                mod_text_col = QtWidgets.QVBoxLayout()
                mod_text_col.setSpacing(1)
                mod_title = QtWidgets.QLabel('<b>Mod Selection</b>')
                mod_sub = QtWidgets.QLabel("Create patches with your Mod's data.")
                mod_sub.setStyleSheet('color: palette(mid); font-size: 11px;')
                mod_text_col.addWidget(mod_title)
                mod_text_col.addWidget(mod_sub)

                open_folder_btn = QtWidgets.QPushButton(GetIcon('open'), '')
                open_folder_btn.setToolTip('Open Mods Folder')
                open_folder_btn.setFixedSize(26, 26)
                open_folder_btn.setIconSize(QtCore.QSize(15, 15))

                refresh_btn = QtWidgets.QPushButton(GetIcon('reload'), '')
                refresh_btn.setToolTip('Refresh Mods')
                refresh_btn.setFixedSize(26, 26)
                refresh_btn.setIconSize(QtCore.QSize(15, 15))

                util_row = QtWidgets.QHBoxLayout()
                util_row.setSpacing(3)
                util_row.addWidget(open_folder_btn)
                util_row.addWidget(refresh_btn)

                mod_header_row.addLayout(mod_text_col)
                mod_header_row.addStretch(1)
                mod_header_row.addLayout(util_row)
                mod_header_row.setAlignment(util_row, Qt.AlignVCenter)
                vbox.addLayout(mod_header_row)

                # ── Two-panel mods layout ────────────────────────────────────
                current_mods = setting('LastMods') or []
                if isinstance(current_mods, str):
                    current_mods = [current_mods]
                all_mods = _gd.getAvailableMods()
                all_folders = {f: d for d, f in all_mods}

                splitter = QtWidgets.QSplitter(Qt.Horizontal)

                left_w = QtWidgets.QWidget()
                left_lay = QtWidgets.QVBoxLayout(left_w)
                left_lay.setContentsMargins(0, 0, 4, 0)
                left_lay.setSpacing(4)

                avail_header = QtWidgets.QHBoxLayout()
                avail_lbl = QtWidgets.QLabel('Available')
                add_btn = QtWidgets.QPushButton('Add →')
                add_btn.setStyleSheet('font-size: 11px; padding: 1px 6px;')
                new_mod_btn = QtWidgets.QPushButton('+ New')
                new_mod_btn.setIconSize(QtCore.QSize(13, 13))
                new_mod_btn.setStyleSheet('font-size: 11px; padding: 1px 6px;')
                avail_header.addWidget(avail_lbl)
                avail_header.addStretch(1)
                avail_header.addWidget(new_mod_btn)
                avail_header.addWidget(add_btn)

                avail_list = QtWidgets.QListWidget()
                avail_list.setDragDropMode(QtWidgets.QAbstractItemView.NoDragDrop)
                self_inner.avail_list = avail_list

                left_lay.addLayout(avail_header)
                left_lay.addWidget(avail_list)

                # Right panel: Active + Remove button in header
                right_w = QtWidgets.QWidget()
                right_lay = QtWidgets.QVBoxLayout(right_w)
                right_lay.setContentsMargins(4, 0, 0, 0)
                right_lay.setSpacing(4)

                active_header = QtWidgets.QHBoxLayout()
                active_lbl = QtWidgets.QLabel('Active')
                active_hint = QtWidgets.QLabel('  drag to reorder')
                active_hint.setStyleSheet('color: palette(mid); font-size: 10px;')
                remove_btn = QtWidgets.QPushButton('← Remove')
                remove_btn.setIconSize(QtCore.QSize(13, 13))
                remove_btn.setStyleSheet('font-size: 11px; padding: 1px 6px;')
                active_header.addWidget(active_lbl)
                active_header.addWidget(active_hint)
                active_header.addStretch(1)
                active_header.addWidget(remove_btn)

                active_list = QtWidgets.QListWidget()
                active_list.setDragDropMode(QtWidgets.QAbstractItemView.InternalMove)
                active_list.setDefaultDropAction(Qt.MoveAction)
                self_inner.active_list = active_list

                right_lay.addLayout(active_header)
                right_lay.addWidget(active_list)

                splitter.addWidget(left_w)
                splitter.addWidget(right_w)
                splitter.setStretchFactor(0, 1)
                splitter.setStretchFactor(1, 1)
                vbox.addWidget(splitter, 1)

                # ── Mod inspector panel ───────────────────────────────────────
                # Shown below the lists whenever any mod is selected in either panel.
                inspector = QtWidgets.QFrame()
                inspector.setFrameShape(QtWidgets.QFrame.StyledPanel)
                inspector.setVisible(False)
                self_inner.inspector = inspector

                insp_lay = QtWidgets.QVBoxLayout(inspector)
                insp_lay.setContentsMargins(10, 8, 10, 8)
                insp_lay.setSpacing(4)

                insp_name = QtWidgets.QLabel()
                insp_name.setStyleSheet('font-size: 13px; font-weight: bold;')
                self_inner.insp_name = insp_name
                insp_lay.addWidget(insp_name)

                insp_sep = QtWidgets.QFrame()
                insp_sep.setFrameShape(QtWidgets.QFrame.HLine)
                insp_sep.setFrameShadow(QtWidgets.QFrame.Sunken)
                insp_lay.addWidget(insp_sep)

                insp_desc = QtWidgets.QLabel()
                insp_desc.setStyleSheet('color: palette(mid); font-size: 11px;')
                insp_desc.setWordWrap(True)
                self_inner.insp_desc = insp_desc
                insp_lay.addWidget(insp_desc)

                insp_btn_row = QtWidgets.QHBoxLayout()
                insp_btn_row.setSpacing(6)
                insp_btn_row.setContentsMargins(0, 4, 0, 0)
                configure_btn = QtWidgets.QPushButton(GetIcon('settings'), 'Configure…')
                configure_btn.setIconSize(QtCore.QSize(14, 14))
                open_mod_folder_btn = QtWidgets.QPushButton(GetIcon('open'), 'Open Folder')
                open_mod_folder_btn.setIconSize(QtCore.QSize(14, 14))
                insp_btn_row.addWidget(configure_btn)
                insp_btn_row.addWidget(open_mod_folder_btn)
                insp_btn_row.addStretch(1)
                insp_lay.addLayout(insp_btn_row)
                vbox.addWidget(inspector)

                # In-memory cache for mod paths (no setSetting until OK)
                self_inner._mod_path_cache = {}
                self_inner._current_mod_folder = None

                # ── Populate lists ────────────────────────────────────────────
                active_set = set(current_mods)
                for def_, folder in all_mods:
                    is_broken = bool(getattr(def_, 'error', None))
                    if not is_broken and folder in active_set:
                        continue
                    item = QtWidgets.QListWidgetItem(def_.name)
                    item.setData(Qt.UserRole, folder)
                    item.setData(Qt.UserRole + 1, def_.description)
                    if is_broken:
                        item.setForeground(QtGui.QColor('#cc3333'))
                        item.setToolTip(f'⚠ {def_.error}')
                    else:
                        item.setToolTip(def_.description)
                    avail_list.addItem(item)

                for folder in current_mods:
                    if folder in all_folders:
                        def_ = all_folders[folder]
                        if getattr(def_, 'error', None):
                            continue
                        item = QtWidgets.QListWidgetItem(def_.name if hasattr(def_, 'name') else folder)
                        item.setData(Qt.UserRole, folder)
                        item.setData(Qt.UserRole + 1, getattr(def_, 'description', ''))
                        active_list.addItem(item)

                # ── Signals ───────────────────────────────────────────────────
                def _show_inspector(display_name, folder):
                    """Show the inspector for the selected mod (either list)."""
                    self_inner._current_mod_folder = folder
                    insp_name.setText(display_name)
                    sel = avail_list.currentItem() or active_list.currentItem()
                    insp_desc.setText((sel.data(Qt.UserRole + 1) if sel else '') or '')
                    inspector.setVisible(True)

                def _on_avail_selection():
                    sel = avail_list.currentItem()
                    if sel is None:
                        return
                    active_list.blockSignals(True)
                    active_list.clearSelection()
                    active_list.setCurrentItem(None)
                    active_list.blockSignals(False)
                    _show_inspector(sel.text(), sel.data(Qt.UserRole))

                def _on_active_selection():
                    sel = active_list.currentItem()
                    if sel is None:
                        return
                    avail_list.blockSignals(True)
                    avail_list.clearSelection()
                    avail_list.setCurrentItem(None)
                    avail_list.blockSignals(False)
                    _show_inspector(sel.text(), sel.data(Qt.UserRole))

                def _add_mod():
                    sel = avail_list.currentItem()
                    if sel is None:
                        return
                    avail_list.takeItem(avail_list.row(sel))
                    active_list.addItem(sel)
                    active_list.setCurrentItem(sel)

                def _remove_mod():
                    sel = active_list.currentItem()
                    if sel is None:
                        return
                    active_list.takeItem(active_list.row(sel))
                    avail_list.addItem(sel)
                    avail_list.setCurrentItem(sel)
                    self_inner._current_mod_folder = None

                def _new_mod():
                    """Show dialog to create a new user-patch folder."""
                    import re as _re
                    dlg_new = QtWidgets.QDialog(self_inner)
                    dlg_new.setWindowTitle('Create a New Mod')
                    dlg_new.setMinimumWidth(380)
                    form_new = QtWidgets.QFormLayout()
                    form_new.setLabelAlignment(Qt.AlignRight | Qt.AlignVCenter)
                    name_edit_n = QtWidgets.QLineEdit()
                    name_edit_n.setPlaceholderText('Newer U')
                    form_new.addRow('Name:', name_edit_n)
                    desc_edit_n = QtWidgets.QLineEdit()
                    desc_edit_n.setPlaceholderText('Description (optional)')
                    form_new.addRow('Description:', desc_edit_n)
                    btns_new = QtWidgets.QDialogButtonBox(
                        QtWidgets.QDialogButtonBox.Ok | QtWidgets.QDialogButtonBox.Cancel)
                    btns_new.button(QtWidgets.QDialogButtonBox.Ok).setText('Create')
                    btns_new.button(QtWidgets.QDialogButtonBox.Ok).setEnabled(False)
                    name_edit_n.textChanged.connect(
                        lambda t: btns_new.button(
                            QtWidgets.QDialogButtonBox.Ok).setEnabled(bool(t.strip())))
                    btns_new.accepted.connect(dlg_new.accept)
                    btns_new.rejected.connect(dlg_new.reject)
                    lay_new = QtWidgets.QVBoxLayout(dlg_new)
                    lay_new.addLayout(form_new)
                    lay_new.addWidget(btns_new)
                    if dlg_new.exec_() != QtWidgets.QDialog.Accepted:
                        return
                    mod_name_n = name_edit_n.text().strip()
                    mod_desc_n = desc_edit_n.text().strip()
                    # Build a filesystem-safe slug from the name
                    slug = _re.sub(r'[^\w\-]', '_', mod_name_n).strip('_') or 'mod'
                    user_patches = os.path.join(globals.user_data_path, 'patches')
                    base_slug, ctr = slug, 1
                    while os.path.exists(os.path.join(user_patches, slug)):
                        slug = f'{base_slug}_{ctr}'; ctr += 1
                    from .patchxml import PatchXmlEditor
                    PatchXmlEditor.create_mod(user_patches, slug, mod_name_n, mod_desc_n)
                    item_n = QtWidgets.QListWidgetItem(mod_name_n)
                    item_n.setData(Qt.UserRole, slug)
                    item_n.setData(Qt.UserRole + 1, mod_desc_n)
                    item_n.setToolTip(mod_desc_n)
                    avail_list.addItem(item_n)
                    avail_list.setCurrentItem(item_n)

                def _open_configure():
                    """Show Configure modal for the currently selected mod."""
                    folder = self_inner._current_mod_folder
                    if folder is None:
                        return
                    _upd = os.path.join(globals.user_data_path, 'patches')
                    is_user = os.path.isfile(os.path.join(_upd, folder, 'main.xml'))
                    sel_c = avail_list.currentItem() or active_list.currentItem()
                    cur_name = sel_c.text() if sel_c else folder
                    cur_desc = (sel_c.data(Qt.UserRole + 1) if sel_c else '') or ''
                    cur_path = self_inner._mod_path_cache.get(
                        folder, setting('GamePath_mod_' + folder, '') or '')
                    dlg_cfg = QtWidgets.QDialog(self_inner)
                    dlg_cfg.setWindowTitle(f'Configure — {cur_name}')
                    dlg_cfg.setMinimumWidth(420)
                    form_cfg = QtWidgets.QFormLayout()
                    form_cfg.setLabelAlignment(Qt.AlignRight | Qt.AlignVCenter)
                    if not is_user:
                        note_c = QtWidgets.QLabel('Name and description are read-only for bundled mods.')
                        note_c.setStyleSheet('color: palette(mid); font-size: 11px;')
                        form_cfg.addRow('', note_c)
                    name_edit_c = QtWidgets.QLineEdit(cur_name)
                    name_edit_c.setEnabled(is_user)
                    form_cfg.addRow('Name:', name_edit_c)
                    desc_edit_c = QtWidgets.QLineEdit(cur_desc)
                    desc_edit_c.setEnabled(is_user)
                    form_cfg.addRow('Description:', desc_edit_c)
                    # Game path row with Browse
                    path_w_c = QtWidgets.QWidget()
                    ph_c = QtWidgets.QHBoxLayout(path_w_c)
                    ph_c.setContentsMargins(0, 0, 0, 0)
                    path_edit_c = QtWidgets.QLineEdit(cur_path)
                    path_edit_c.setPlaceholderText('Leave blank to use base game path')
                    browse_c = QtWidgets.QPushButton('Browse…')
                    ph_c.addWidget(path_edit_c)
                    ph_c.addWidget(browse_c)
                    form_cfg.addRow('Game path:', path_w_c)
                    valid_c = QtWidgets.QLabel()
                    valid_c.setStyleSheet('color: palette(mid); font-size: 11px;')
                    form_cfg.addRow('', valid_c)
                    def _vc():
                        p = path_edit_c.text().strip()
                        ok = isValidGamePath(p) if p else None
                        if ok is None:
                            valid_c.setText('Uses base game path by default')
                            valid_c.setStyleSheet('color: palette(mid); font-size: 11px;')
                        elif ok:
                            valid_c.setText('✓ Valid')
                            valid_c.setStyleSheet('color: green; font-size: 11px;')
                        else:
                            valid_c.setText('✗ Invalid path')
                            valid_c.setStyleSheet('color: red; font-size: 11px;')
                    path_edit_c.textChanged.connect(_vc)
                    _vc()
                    def _browse_c():
                        p = QtWidgets.QFileDialog.getExistingDirectory(
                            None, 'Select mod game folder', path_edit_c.text())
                        if p:
                            path_edit_c.setText(p)
                    browse_c.clicked.connect(_browse_c)
                    btns_cfg = QtWidgets.QDialogButtonBox(
                        QtWidgets.QDialogButtonBox.Ok | QtWidgets.QDialogButtonBox.Cancel)
                    btns_cfg.accepted.connect(dlg_cfg.accept)
                    btns_cfg.rejected.connect(dlg_cfg.reject)
                    lay_cfg = QtWidgets.QVBoxLayout(dlg_cfg)
                    lay_cfg.addLayout(form_cfg)
                    lay_cfg.addWidget(btns_cfg)
                    if dlg_cfg.exec_() != QtWidgets.QDialog.Accepted:
                        return
                    new_name = name_edit_c.text().strip() or cur_name
                    new_desc = desc_edit_c.text().strip()
                    new_path = path_edit_c.text().strip()
                    self_inner._mod_path_cache[folder] = new_path
                    if is_user and (new_name != cur_name or new_desc != cur_desc):
                        from .patchxml import PatchXmlEditor
                        PatchXmlEditor(os.path.join(_upd, folder)).set_metadata(new_name, new_desc)
                    if sel_c:
                        sel_c.setText(new_name)
                        sel_c.setData(Qt.UserRole + 1, new_desc)
                    insp_name.setText(new_name)
                    insp_desc.setText(new_desc)

                def _open_mod_folder():
                    """Open the selected mod's own directory."""
                    folder = self_inner._current_mod_folder
                    if folder is None:
                        return
                    _upd = os.path.join(globals.user_data_path, 'patches')
                    _bpd = os.path.join(globals.miyamoto_path, 'miyamotodata', 'patches')
                    mod_dir = (os.path.join(_upd, folder)
                               if os.path.isdir(os.path.join(_upd, folder))
                               else os.path.join(_bpd, folder)
                               if os.path.isdir(os.path.join(_bpd, folder))
                               else None)
                    if mod_dir:
                        QtGui.QDesktopServices.openUrl(
                            QtCore.QUrl.fromLocalFile(mod_dir))

                def _open_mods_folder():
                    user_patches = os.path.join(globals.user_data_path, 'patches')
                    os.makedirs(user_patches, exist_ok=True)
                    QtGui.QDesktopServices.openUrl(
                        QtCore.QUrl.fromLocalFile(user_patches))

                def _refresh_mods():
                    current_active = set()
                    for i in range(active_list.count()):
                        current_active.add(active_list.item(i).data(Qt.UserRole))
                    # Block signals on both lists so clearing/repopulating
                    # doesn't spuriously fire selection handlers mid-rebuild.
                    avail_list.blockSignals(True)
                    active_list.blockSignals(True)
                    avail_list.clear()
                    active_list.clear()
                    # Rebuild active list (dropping any broken mods)
                    all_mods = _gd.getAvailableMods()
                    all_folders = {f: d for d, f in all_mods}
                    for folder in current_active:
                        if folder in all_folders:
                            def_ = all_folders[folder]
                            if getattr(def_, 'error', None):
                                continue
                            item = QtWidgets.QListWidgetItem(def_.name if hasattr(def_, 'name') else folder)
                            item.setData(Qt.UserRole, folder)
                            item.setData(Qt.UserRole + 1, getattr(def_, 'description', ''))
                            active_list.addItem(item)
                    # Rebuild available list
                    for def_, folder in all_mods:
                        is_broken = bool(getattr(def_, 'error', None))
                        if not is_broken and folder in current_active:
                            continue
                        item = QtWidgets.QListWidgetItem(def_.name)
                        item.setData(Qt.UserRole, folder)
                        item.setData(Qt.UserRole + 1, def_.description)
                        if is_broken:
                            item.setForeground(QtGui.QColor('#cc3333'))
                            item.setToolTip(f'⚠ {def_.error}')
                        else:
                            item.setToolTip(def_.description)
                        avail_list.addItem(item)
                    avail_list.blockSignals(False)
                    active_list.blockSignals(False)
                    # Reset inspector state cleanly after the rebuild.
                    self_inner._current_mod_folder = None
                    inspector.setVisible(False)

                avail_list.currentItemChanged.connect(lambda *_: _on_avail_selection())
                active_list.currentItemChanged.connect(lambda *_: _on_active_selection())
                add_btn.clicked.connect(_add_mod)
                remove_btn.clicked.connect(_remove_mod)
                new_mod_btn.clicked.connect(_new_mod)
                configure_btn.clicked.connect(_open_configure)
                open_mod_folder_btn.clicked.connect(_open_mod_folder)
                open_folder_btn.clicked.connect(_open_mods_folder)
                refresh_btn.clicked.connect(_refresh_mods)

            def getSelectedBaseGame(self_inner):
                for folder, radio in self_inner._game_radios.items():
                    if radio.isChecked():
                        return folder
                return 'NSMBU'

            def getActiveMods(self_inner):
                result = []
                for i in range(self_inner.active_list.count()):
                    folder = self_inner.active_list.item(i).data(Qt.UserRole)
                    if folder:
                        result.append(folder)
                return result

            def getModPaths(self_inner):
                """Return in-memory mod path cache (paths are written by the Configure modal)."""
                return self_inner._mod_path_cache

        return GameSetupTab()

    @staticmethod
    def getThemesTab(parent):
        """
        Returns the Themes Tab
        """

        class ThemesTab(parent):
            """
            Themes Tab
            """
            info = "<b>Themes</b><br>Pick a theme to change the application's colors and icons."

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
                previewGB = QtWidgets.QGroupBox('Preview')
                previewGB.setLayout(L)

                # Create the options box options
                keys = QtWidgets.QStyleFactory().keys()
                self.NonWinStyle = QtWidgets.QComboBox()
                self.NonWinStyle.setToolTip('<b>Use Nonstandard Window Style</b><br>If this is checkable, the selected theme specifies a<br>window style other than the default. In most cases, you<br>should leave this checked. Uncheck this if you dislike<br>the style this theme uses.')
                self.NonWinStyle.addItems(keys)
                uistyle = setting('uiStyle', "Fusion")
                if uistyle is not None:
                    self.NonWinStyle.setCurrentIndex(keys.index(setting('uiStyle', "Fusion")))

                # Create the options groupbox
                L = QtWidgets.QVBoxLayout()
                L.addWidget(self.NonWinStyle)
                optionsGB = QtWidgets.QGroupBox('Options')
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

                self._initial_theme = self.themeBox.currentText()
                self._initial_style = self.NonWinStyle.currentText()

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
                        text = '<b>[name]</b><br>By [creator]<br>[description]'.replace('[name]', str(t.themeName)).replace('[creator]', str(t.creator)).replace('[description]', str(t.description))
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


class WelcomeDialog(QtWidgets.QDialog):
    """
    Shown at startup when no level can be auto-loaded.
    Check .action after exec_(). If ACTION_OPEN_RECENT, .recent_path holds the file.
    """

    ACTION_OPEN_FILE   = 'open_file'
    ACTION_OPEN_NAME   = 'open_name'
    ACTION_NEW_LEVEL   = 'new_level'
    ACTION_OPEN_RECENT = 'open_recent'

    def __init__(self):
        super().__init__()
        self.action = None
        self.recent_path = None

        self.setWindowTitle('Pyamoto')
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)

        import platform as _platform
        icon_name = 'pyamoto1024mac.png' if _platform.system() == 'Darwin' else 'pyamoto1024.png'
        icon_path = os.path.join(globals.miyamoto_path, 'miyamotodata', icon_name)
        if os.path.isfile(icon_path):
            self.setWindowIcon(QtGui.QIcon(icon_path))

        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(36, 28, 36, 20)
        layout.setSpacing(0)

        # Logo
        if os.path.isfile(icon_path):
            logo = QtWidgets.QLabel()
            logo.setAlignment(Qt.AlignHCenter)
            dpr = QtWidgets.QApplication.instance().devicePixelRatio()
            physical = int(108 * dpr)
            pix = QtGui.QPixmap(icon_path).scaled(physical, physical, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            pix.setDevicePixelRatio(dpr)
            logo.setPixmap(pix)
            logo.setFixedHeight(108)
            layout.addWidget(logo)
            layout.addSpacing(14)

        # Heading
        heading = QtWidgets.QLabel('Welcome to Pyamoto')
        heading.setAlignment(Qt.AlignHCenter)
        hf = heading.font()
        hf.setPointSize(hf.pointSize() + 5)
        hf.setBold(True)
        heading.setFont(hf)
        layout.addWidget(heading)
        layout.addSpacing(6)

        # Subtitle
        sub = QtWidgets.QLabel('Open an existing level or start fresh.')
        sub.setAlignment(Qt.AlignHCenter)
        sub.setStyleSheet('color: palette(mid);')
        layout.addWidget(sub)
        layout.addSpacing(22)

        # Action buttons
        _has_name_sources = hasLevelNameSources()
        for label, action in (
            ('New Level',           self.ACTION_NEW_LEVEL),
            ('Open Level by Name…', self.ACTION_OPEN_NAME),
            ('Open Level by File…', self.ACTION_OPEN_FILE),
        ):
            btn = QtWidgets.QPushButton(label)
            btn.setFixedHeight(36)
            btn.clicked.connect(lambda _checked, a=action: self._choose(a))
            if action == self.ACTION_OPEN_NAME and not _has_name_sources:
                btn.setEnabled(False)
                btn.setToolTip('No game path configured — set one in Interactive Setup first.')
            layout.addWidget(btn)
            layout.addSpacing(6)

        # Recent files section
        recent_entries = globals.mainWindow.RecentMenu.getEntries() if globals.mainWindow else []
        self._recentList = None
        self._clearBtn = None

        if recent_entries:
            layout.addSpacing(10)

            sep = QtWidgets.QFrame()
            sep.setFrameShape(QtWidgets.QFrame.HLine)
            sep.setFrameShadow(QtWidgets.QFrame.Sunken)
            layout.addWidget(sep)
            layout.addSpacing(10)

            rec_hdr = QtWidgets.QLabel('Recent Files')
            hdr_font = rec_hdr.font()
            hdr_font.setPointSize(hdr_font.pointSize() - 1)
            hdr_font.setBold(True)
            rec_hdr.setFont(hdr_font)
            rec_hdr.setStyleSheet('color: palette(mid);')
            layout.addWidget(rec_hdr)
            layout.addSpacing(6)

            lst = QtWidgets.QListWidget()
            lst.setFrameShape(QtWidgets.QFrame.NoFrame)
            lst.setFocusPolicy(Qt.NoFocus)
            lst.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
            lst.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
            lst.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)
            lst.setSpacing(1)
            for rec_label, rec_path in recent_entries:
                item = QtWidgets.QListWidgetItem(rec_label)
                item.setToolTip(rec_path)
                item.setData(Qt.UserRole, rec_path)
                lst.addItem(item)
            lst.setMaximumHeight(min(len(recent_entries), 6) * 26 + 4)
            lst.itemActivated.connect(self._openRecent)
            lst.itemClicked.connect(self._openRecent)
            self._recentList = lst
            layout.addWidget(lst)
            layout.addSpacing(6)

            clear_btn = QtWidgets.QPushButton('Clear Recent Files')
            clear_btn.setFixedHeight(28)
            clear_btn.clicked.connect(self._clearRecent)
            self._clearBtn = clear_btn
            layout.addWidget(clear_btn)

        layout.addStretch(1)

        self.adjustSize()
        self.setFixedSize(440, self.sizeHint().height())

    def _choose(self, action):
        self.action = action
        self.accept()

    def _openRecent(self, item):
        path = item.data(Qt.UserRole)
        if path:
            self.recent_path = path
            self.action = self.ACTION_OPEN_RECENT
            self.accept()

    def _clearRecent(self):
        if globals.mainWindow:
            globals.mainWindow.RecentMenu.clearAll()
        if self._recentList:
            self._recentList.clear()
        if self._clearBtn:
            self._clearBtn.setVisible(False)
        # Resize dialog to remove the now-empty recent section
        self.adjustSize()
        self.setFixedSize(440, self.sizeHint().height())


class ChooseLevelNameDialog(QtWidgets.QDialog):
    """
    Dialog to open a level by name.  Shows one tab per loaded patch (base game + active mods
    that provide levelnames or have levels in their game path), each with its own level list
    and game path.  Right-clicking a level in a user-patch tab lets you assign it a name.
    """

    def __init__(self):
        super().__init__()
        self.setWindowTitle('Choose Level')
        self.setWindowIcon(GetIcon('open'))

        self.currentlevel = None
        self.current_game_path = None
        self.current_display_name = None
        self.current_tab_name = None

        tabs = QtWidgets.QTabWidget()
        self._tabs = tabs
        self._tab_game_paths = []       # game path per tab (parallel)
        self._tab_user_patches = []     # user-patch folder name per tab, or None

        self._buildTabs()

        self.buttonBox = QtWidgets.QDialogButtonBox(
            QtWidgets.QDialogButtonBox.Ok | QtWidgets.QDialogButtonBox.Cancel)
        self.buttonBox.button(QtWidgets.QDialogButtonBox.Ok).setEnabled(False)
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)

        # "Edit Level Info…" button — visible only for user-patch tabs, enabled on selection
        self._rename_btn = QtWidgets.QPushButton('Edit Level Info…')
        self._rename_btn.setEnabled(False)
        self._rename_btn.setVisible(False)
        self._rename_btn.clicked.connect(self._doRename)
        self.buttonBox.addButton(self._rename_btn, QtWidgets.QDialogButtonBox.ActionRole)

        tabs.currentChanged.connect(self._onTabChanged)

        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(tabs)
        layout.addWidget(self.buttonBox)
        self.setLayout(layout)
        self.setMinimumWidth(360)
        self.setMinimumHeight(420)

    # ── Tab builder ────────────────────────────────────────────────────────
    def _buildTabs(self):
        from . import gamedefs as _gd
        from .loading import LoadLevelNamesForDef

        base_game_folder = setting('LastBaseGame', 'NSMBU')
        active_mods = setting('LastMods') or []
        if isinstance(active_mods, str):
            active_mods = [active_mods]

        # entries: (label, names_list, game_path, user_patch_folder_or_None)
        entries = []

        # ── Base game ───────────────────────────────────────────────────────
        base_def = _gd.MiyamotoGameDefinition(base_game_folder, source='game')
        base_names = LoadLevelNamesForDef(base_def)
        if not base_names:
            try:
                from xml.etree import ElementTree as _et
                from .loading import LoadLevelNames_Category
                tree = _et.parse(os.path.join(globals.miyamoto_path, 'miyamotodata', 'levelnames.xml'))
                base_names = LoadLevelNames_Category(tree.getroot())
            except Exception:
                base_names = []
        if not base_names:
            base_names = self._scanGamePathForLevels(base_def.GetGamePath())
        if base_names:
            entries.append((base_def.name, base_names, base_def.GetGamePath(), None))

        # ── Active mods ─────────────────────────────────────────────────────
        _user_patches_dir = os.path.join(globals.user_data_path, 'patches')
        for mod_folder in active_mods:
            if not mod_folder:
                continue
            mod_def = _gd.MiyamotoGameDefinition(mod_folder, source='mod')
            if not mod_def.custom:
                continue
            mod_names = LoadLevelNamesForDef(mod_def)
            if not mod_names:
                mod_names = self._scanGamePathForLevels(mod_def.GetGamePath())
            if not mod_names:
                continue
            is_user = os.path.isfile(
                os.path.join(_user_patches_dir, mod_folder, 'main.xml'))
            entries.append((mod_def.name, mod_names, mod_def.GetGamePath(),
                            mod_folder if is_user else None))

        del _gd

        if not entries:
            gpath = globals.gamedef.GetGamePath() if globals.gamedef else ''
            entries.append(('Levels', globals.LevelNames, gpath, None))

        for label, names, gpath, user_patch in entries:
            tree = self._makeTree(names, gpath, user_patch)
            self._tabs.addTab(tree, label)
            self._tab_game_paths.append(gpath)
            self._tab_user_patches.append(user_patch)

    # ── Tree builder ───────────────────────────────────────────────────────
    def _makeTree(self, names, game_path='', user_patch_folder=None):
        tree = QtWidgets.QTreeWidget()
        tree.setColumnCount(1)
        tree.setHeaderHidden(True)
        tree.setIndentation(16)
        tree.currentItemChanged.connect(self._onItemChange)
        tree.itemActivated.connect(self._onItemActivated)
        tree.addTopLevelItems(self._parseCategory(names, game_path))

        return tree

    def _parseCategory(self, items, game_path=''):
        nodes = []
        for item in items:
            node = QtWidgets.QTreeWidgetItem()
            node.setText(0, item[0])
            if isinstance(item[1], str):
                code = item[1]
                # Tooltip shows the full filename, checking which extension exists
                if game_path:
                    ext = next(
                        (e for e in ('.szs', '.sarc')
                         if os.path.isfile(os.path.join(game_path, code + e))),
                        '.szs')
                else:
                    ext = '.szs'
                node.setData(0, Qt.UserRole, code)
                node.setToolTip(0, code + ext)
            else:
                for child in self._parseCategory(item[1], game_path):
                    node.addChild(child)
                node.setToolTip(0, item[0])
            nodes.append(node)
        return tuple(nodes)

    # ── Unnamed level discovery ────────────────────────────────────────────
    @staticmethod
    def _scanGamePathForLevels(game_path):
        """Scan a game path directory for .szs/.sarc files, returns synthetic names list."""
        if not game_path or not os.path.isdir(game_path):
            return []
        files = []
        for fname in sorted(os.listdir(game_path)):
            for ext in ('.szs', '.sarc'):
                if fname.lower().endswith(ext):
                    files.append([fname, fname[:-len(ext)]])  # display full filename, code is stem
                    break
        return [['Unnamed', files]] if files else []

    # ── Rename level (user patches only) ──────────────────────────────────
    def _promptRename(self, item, user_patch_folder):
        """Show the rename dialog for a tree leaf item (called from context menu)."""
        if item is None or item.data(0, Qt.UserRole) is None:
            return
        code = item.data(0, Qt.UserRole)
        current_display = item.text(0)
        suggest = '' if current_display == code else current_display
        new_name, ok = QtWidgets.QInputDialog.getText(
            self, 'Name Level',
            f'Enter a display name for {code}:',
            text=suggest)
        if not ok or not new_name.strip():
            return
        new_name = new_name.strip()
        from .patchxml import PatchXmlEditor
        user_patch_dir = os.path.join(globals.user_data_path, 'patches', user_patch_folder)
        PatchXmlEditor(user_patch_dir).set_level_name(code, new_name)
        item.setText(0, new_name)

    # ── Selection signals ──────────────────────────────────────────────────
    def _onTabChanged(self, index):
        self.currentlevel = None
        self.current_game_path = self._tab_game_paths[index] if index < len(self._tab_game_paths) else ''
        self.buttonBox.button(QtWidgets.QDialogButtonBox.Ok).setEnabled(False)
        self._updateRenameBtn()

    def _onItemChange(self, current, previous):
        if current is None:
            return
        self.currentlevel = current.data(0, Qt.UserRole)
        idx = self._tabs.currentIndex()
        self.current_game_path = self._tab_game_paths[idx] if idx < len(self._tab_game_paths) else ''
        self.current_tab_name = self._tabs.tabText(idx)
        self.current_display_name = current.text(0)
        ok = self.currentlevel is not None
        self.buttonBox.button(QtWidgets.QDialogButtonBox.Ok).setEnabled(ok)
        if ok:
            self.currentlevel = str(self.currentlevel)
        self._updateRenameBtn()

    def _updateRenameBtn(self):
        idx = self._tabs.currentIndex()
        is_user_patch = (idx < len(self._tab_user_patches)
                         and self._tab_user_patches[idx] is not None)
        self._rename_btn.setVisible(is_user_patch)
        if is_user_patch:
            tree = self._tabs.widget(idx)
            item = tree.currentItem() if isinstance(tree, QtWidgets.QTreeWidget) else None
            self._rename_btn.setEnabled(item is not None
                                        and item.data(0, Qt.UserRole) is not None)

    def _doRename(self):
        idx = self._tabs.currentIndex()
        if idx >= len(self._tab_user_patches):
            return
        user_patch_folder = self._tab_user_patches[idx]
        if user_patch_folder is None:
            return
        tree = self._tabs.widget(idx)
        if not isinstance(tree, QtWidgets.QTreeWidget):
            return
        self._promptRename(tree.currentItem(), user_patch_folder)

    def _onItemActivated(self, item, column):
        self.currentlevel = item.data(0, Qt.UserRole)
        if self.currentlevel is not None:
            self.currentlevel = str(self.currentlevel)
            idx = self._tabs.currentIndex()
            self.current_game_path = self._tab_game_paths[idx] if idx < len(self._tab_game_paths) else ''
            self.accept()

    # Legacy aliases
    def ParseCategory(self, items):
        return self._parseCategory(items)

    def HandleItemChange(self, current, previous):
        self._onItemChange(current, previous)

    def HandleItemActivated(self, item, column):
        self._onItemActivated(item, column)
