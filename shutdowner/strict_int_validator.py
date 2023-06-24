from PyQt6.QtGui import QValidator


class StrictIntValidator(QValidator):
    def __init__(self, showTip, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.showTip = showTip

    def validate(self, text, pos):
        if text == '':
            return QValidator.State.Acceptable, text, pos

        if all(ch.isdigit() for ch in text):
            val = int(text)
            text = str(val)
            if self.isCorrectVal(val):
                return QValidator.State.Acceptable, text, pos

        self.showTip(self.tipTextId())
        return QValidator.State.Invalid, text, pos

    def isCorrectVal(self, val):
        return True

    def tipTextId(self):
        return "Only int values!"
