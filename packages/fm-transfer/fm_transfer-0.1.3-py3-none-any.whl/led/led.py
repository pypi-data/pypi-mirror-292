from typing import Optional

from PyQt6.QtWidgets import QGraphicsDropShadowEffect, QWidget
from PyQt6.QtGui import QColor, QPainter, QPen, QRadialGradient, QMouseEvent, QPaintEvent
from PyQt6.QtCore import Qt, QPointF, pyqtSlot, QObject

# noinspection PyPep8Naming
class Led(QWidget):
    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent=parent)
        self.setFixedSize(24, 24)
        self.on = True
        self.light_color = QColor.fromRgbF(255, 0, 0)
        self.glow_effect = QGraphicsDropShadowEffect()
        self.glow_effect.setBlurRadius(48)
        self.glow_effect.setColor(self.light_color.lighter(150))
        self.glow_effect.setOffset(0, 0)
        self.glow_effect.setEnabled(False)
        self.setGraphicsEffect(self.glow_effect)
        self._parent: Optional[QObject] = None
        first_parent: Optional[QObject] = self.parent()
        if isinstance(first_parent, QWidget):
            self._parent = first_parent.parent()


    def isOn(self) -> bool:
        return self.on

    @pyqtSlot(bool)
    def setOn(self, on: bool) -> None:
        self.on = on
        self.glow_effect.setEnabled(self.on)
        self.update()

    def getLightColor(self) -> QColor:
        return self.light_color

    def mouseReleaseEvent(self, e: Optional[QMouseEvent]) -> None:
        if isinstance(self._parent, QWidget):
            if self._parent.pttPressedRadioButton.isChecked():  # type: ignore[attr-defined]
                self._parent.pttReleasedRadioButton.setChecked(True)  # type: ignore[attr-defined]
            else:
                self._parent.pttPressedRadioButton.setChecked(True)  # type: ignore[attr-defined]
        if e is not None:
            e.accept()

    @pyqtSlot(QColor)
    def setLightColor(self, color: QColor) -> None:
        self.light_color = color
        self.glow_effect.setColor(self.light_color.lighter(150))
        self.update()

    def paintEvent(self, event: Optional[QPaintEvent]) -> None:

        painter = QPainter(self)
        painter.setRenderHints(QPainter.RenderHint.Antialiasing)

        led_color = self.light_color if self.on else QColor(Qt.GlobalColor.darkGray)

        # defining a radial gradient to render the LED color and simulate a clear ambient reflection on its surface
        radius = self.width() / 2.0
        radial_gradient = QRadialGradient(QPointF(radius, radius), radius - 1, QPointF(radius, radius / 2.0))
        radial_gradient.setColorAt(0, led_color.lighter(300))
        radial_gradient.setColorAt(0.5, led_color)
        radial_gradient.setColorAt(1, led_color.darker(200))

        # set Pen for the outline and Brush for the filling
        painter.setPen(QPen(Qt.GlobalColor.gray, 2))
        painter.setBrush(radial_gradient)

        # draws the gray outline with a single directive and fills the circular area of the LED with the gradient
        painter.drawEllipse(QPointF(radius, radius), radius - 1, radius - 1)
