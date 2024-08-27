import sys
from PyQt6.QtWidgets import QApplication, QStyle, QStyleFactory
import fmtransfer

def _main() -> None:
    app = QApplication(sys.argv)
    # print(QStyleFactory.keys())
    style: QStyle = app.style()
    # print(style.name())
    if style.name() == "windows11":
        app.setStyle(QStyleFactory.create('Fusion'))
    fm_transfer = fmtransfer.FmTransfer()
    fm_transfer.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    _main()
