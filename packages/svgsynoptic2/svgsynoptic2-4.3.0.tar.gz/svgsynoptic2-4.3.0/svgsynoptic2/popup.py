from taurus.qt.qtgui.panel import TaurusForm
from taurus.qt.qtgui.container import TaurusWidget
from taurus.external.qt import Qt, QtGui, QtCore
from taurus.qt.qtgui.button import TaurusCommandButton
from taurus.qt.qtgui.display import TaurusLabel
import tango
import taurus


class TaurusFormExpanding(TaurusForm):
    """A TaurusForm that adapts its size to its children"""

    max_vertical_size = 500

    def sizeHint(self):
        frame = self.scrollArea.widget()
        framehint = frame.sizeHint()
        hint = Qt.QSize(
            framehint.width(), min(self.max_vertical_size, framehint.height())
        )
        return hint + self.buttonBox.sizeHint() + Qt.QSize(0, 20)


class StateComposerWidget(TaurusFormExpanding):
    """A widget for displaying devices listed in a StateComposer

    StateComposer is a Facade device that combines some states from
    a list of devices
    """

    _customWidgetMap = getattr(
        taurus.tauruscustomsettings, "T_FORM_CUSTOM_WIDGET_MAP", {}
    )

    def setModel(self, model):
        if model:
            # Get the devices from the device states property
            # (returns an array of "device/State" attributes)
            states = tango.Database().get_device_property(model, "states")["states"]
            # Remove the "State" attribute to get the device name
            devices = [state.rsplit("/", 1)[0] for state in states]
            self.setCustomWidgetMap(
                getattr(taurus.tauruscustomsettings, "T_FORM_CUSTOM_WIDGET_MAP", {})
            )
            self.setWithButtons(False)
            TaurusFormExpanding.setModel(self, devices)


class CommandsWidget(TaurusWidget):
    """
    Simple widget that shows a number of Command buttons.
    """

    def __init__(self, parent=None, commands=None):
        super().__init__(parent)
        self.commands = commands
        self.buttons = {}
        self.setupUi()

    def setupUi(self):
        w = TaurusWidget()
        self.setLayout(Qt.QHBoxLayout())
        self.layout().addWidget(w)

        self.modelLabel = QtGui.QLabel(w)
        self.layout().addWidget(self.modelLabel)

        self.stateLabel = TaurusLabel(w)
        self.layout().addWidget(self.stateLabel)

        for command, _ in self.commands:
            button = TaurusCommandButton(w, command=command)
            self.layout().addWidget(button)
            self.buttons[command] = button

    def setModel(self, model):
        super().setModel(model)
        self.setWindowTitle(str(model))
        self.modelLabel.setText(str(model))
        self.stateLabel.setModel(f"{model}/state")
        self.stateLabel.setBgRole("state")
        self.stateLabel.setFgRole("state")
        for button in self.buttons.values():
            button.setModel(str(model))


class CommandsWidgetPopup(CommandsWidget):
    """
    Popup variant of CommandsWidget.
    It moves to mouse on start and it closes on unfocus
    or after successful command.
    On show it hides irrelevant buttons (based on the state).
    It also closes automatically after 10 seconds.

    This class shouldn't be used directly.
    Define your own class with "commands" as class attribute
    """

    def __init__(self, parent=None):
        super().__init__(parent, self.commands)
        self.setWindowFlags(QtCore.Qt.FramelessWindowHint)
        self.installEventFilter(self)
        for button in self.buttons.values():
            button.clicked.connect(self.close)

    def eventFilter(self, object, event):
        """
        Event filter to close if no focus
        """
        if event.type() == QtCore.QEvent.WindowDeactivate:
            self.close()
        return super().eventFilter(object, event)

    def show(self):
        super().show()
        self.showhidebuttons()
        self.move_to_mouse()
        QtCore.QTimer.singleShot(10000, lambda: self.close())

    def showhidebuttons(self):
        dev = taurus.Device(self.model)
        for command, state in self.commands:
            button = self.buttons[command]
            if dev.State() == state:
                button.hide()
            else:
                button.show()
        self.adjustSize()

    def move_to_mouse(self):
        """
        Moves the window to the mouse cursor
        """
        try:
            pos = QtGui.QCursor.pos()
            self.move(
                round(pos.x() - 4 * (self.width() / 5)),
                round(pos.y() - (self.height() / 2)),
            )
        except Exception:
            pass


class ValvePopup(CommandsWidgetPopup):
    """Quick open/close for vacuum valves"""

    commands = (("Open", tango.DevState.OPEN), ("Close", tango.DevState.CLOSE))


class PlcResetPopup(CommandsWidgetPopup):
    """Variant of CommandsWidgetPopup with a single command
    to reset a PLC.

    This class doesn't use a tango command but writes a value
    to a specific attribute.
    """

    commands = (("Reset", None),)

    def __init__(self, parent=None):
        self.command = self.commands[0][0]
        super().__init__(parent)

    def setupUi(self):
        w = TaurusWidget()
        self.setLayout(Qt.QHBoxLayout())
        self.layout().addWidget(w)

        self.modelLabel = QtGui.QLabel(w)
        self.layout().addWidget(self.modelLabel)

        self.stateLabel = TaurusLabel(w)
        self.layout().addWidget(self.stateLabel)

        button = QtGui.QPushButton(self.command, self)
        button.clicked.connect(self.doReset)

        self.layout().addWidget(button)
        self.buttons[self.command] = button

    def doReset(self):
        print("Resetting PLC")
        self.resetAttr.write(1)

    def setModel(self, model):
        TaurusWidget.setModel(self, model)
        self.setWindowTitle(str(model))
        self.modelLabel.setText(str(model))
        self.stateLabel.setModel(f"{model}/state")
        self.stateLabel.setBgRole("rvalue")
        try:
            proxy = tango.DeviceProxy(model)
            attributes = proxy.get_attribute_list()
            # Depending on beamlines
            # reset attribute can be BXXXX_VAC_RESET_C or BXXXX_VAC_PLC01_RESET_C
            parts = model.split("/")
            reset_attributes = [
                attribute
                for attribute in attributes
                if attribute.upper().endswith("_RESET_C")
                and attribute.upper().startswith(
                    f"{parts[0].upper()}_{parts[1].upper()}_"
                )
            ]
            if len(reset_attributes) == 1:
                attr_name = reset_attributes[0]
                self.resetAttr = tango.AttributeProxy(f"{model}/{attr_name}")
                print(f"PLC reset attribute: {model}/{attr_name}")
            else:
                print(
                    f"Couldn't find reset attribute name... {attributes=} {reset_attributes=}"
                )
        except Exception as e:
            print(e)
