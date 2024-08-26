# ViCodePy - A video coder for Experimental Psychology
#
# Copyright (C) 2024 Esteban Milleret
# Copyright (C) 2024 Rafael Laboissière
#
# This program is free software: you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by the
# Free Software Foundation, either version 3 of the License, or (at your
# option) any later version.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General
# Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program. If not, see <https://www.gnu.org/licenses/>.

from enum import IntEnum

from PySide6.QtWidgets import (
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QLineEdit,
    QMessageBox,
)


class TimelineDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Add a new timeline")

        self.name_edit = QLineEdit(self)
        layout = QFormLayout(self)
        layout.addRow("Enter name of the new timeline:", self.name_edit)

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok
            | QDialogButtonBox.StandardButton.Cancel,
            self,
        )
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def get_text(self):
        return self.name_edit.text()


class ConfirmMessageBox(QMessageBox):
    def __init__(self, message, parent=None):
        super().__init__(
            QMessageBox.Icon.Warning,
            "Warning",
            message,
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            parent,
        )

        self.button(QMessageBox.StandardButton.Yes).clicked.connect(self.accept)
        self.button(QMessageBox.StandardButton.No).clicked.connect(self.reject)
        self.exec()


class DialogCode(IntEnum):
    Accepted: int = QDialog.DialogCode.Accepted  # 0
    Canceled: int = QDialog.DialogCode.Rejected  # 1
    Aborted: int = 2
