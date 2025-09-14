"""Settings Dialog Class"""

from PyQt6 import QtWidgets, uic


class Settings(QtWidgets.QDialog):
    """Settings dialog"""

    def __init__(self, app_data_path, pref, parent=None):
        """initialize dialog"""
        super().__init__(parent)
        uic.loadUi(app_data_path, self)

        self.buttonBox.accepted.connect(self.save_changes)
        self.preference = pref
        self.setup()

    def setup(self):
        """setup dialog"""

        x = {
            "00": "Iambic B",
            "01": "Iambic A",
            "10": "Ultimatic",
            "11": "Bug Mode",
        }
        mode_register = self.preference.get("mode_register", "00000000")
        self.disable_paddle_watchdog.setChecked(bool(mode_register[0] == "1"))
        self.paddle_echo_back.setChecked(bool(mode_register[1] == "1"))
        themode = x.get(f"{mode_register[2]}{mode_register[3]}", "Unknown")
        index = self.key_mode.findText(themode)
        self.key_mode.setCurrentIndex(index)
        self.paddle_swap.setChecked(bool(mode_register[4] == "1"))
        self.serial_echo_back.setChecked(bool(mode_register[5] == "1"))
        self.auto_space.setChecked(bool(mode_register[6] == "1"))
        self.ct_spacing.setChecked(bool(mode_register[7] == "1"))

    def save_changes(self):
        """
        Write preferences to json file.
        """
        x = {
            "Iambic B": "00",
            "Iambic A": "01",
            "Ultimatic": "10",
            "Bug Mode": "11",
        }
        mode_register = "00000000"
        if self.disable_paddle_watchdog.isChecked():
            mode_register = "1" + mode_register[1:]
        if self.paddle_echo_back.isChecked():
            mode_register = mode_register[:1] + "1" + mode_register[2:]
        if self.paddle_swap.isChecked():
            mode_register = mode_register[:4] + "1" + mode_register[5:]
        if self.serial_echo_back.isChecked():
            mode_register = mode_register[:5] + "1" + mode_register[6:]
        if self.auto_space.isChecked():
            mode_register = mode_register[:6] + "1" + mode_register[7:]
        if self.ct_spacing.isChecked():
            mode_register = mode_register[:7] + "1"
        themode = x.get(self.key_mode.currentText(), "00")
        mode_register = mode_register[:2] + themode + mode_register[4:]
        self.preference["mode_register"] = mode_register
