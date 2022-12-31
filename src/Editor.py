import random
import sys

from PySide6.QtGui import Qt
from PySide6.QtWidgets import QApplication, QMainWindow, QTreeWidgetItem, QWidget, QListWidgetItem

from src.Config import Config, ConfigKeys, ConfigDataKeys
from src.Connection import Connection
from src.Location import Location
from src.StorageProvider import StorageProvider
from src.ui_mainwindow import Ui_MainWindow
from src.ui_editor_sidewindow import Ui_Form


class MainWindow(QMainWindow):
    def __init__(self, app, storage: StorageProvider, config: Config):
        super().__init__()
        self.app = app
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.storage = storage
        self.config = config

        self.window_title = "Bilbcraft Route Planner Editor"
        self.save_required = False
        self.current_editing_location_id = None
        self.ui_form = None

        self.setup_signals()
        self.init_storage_view()

    def setup_signals(self):
        self.ui.actionQuit.triggered.connect(sys.exit)
        self.ui.actionAddLocation.triggered.connect(self.on_add_location)
        self.ui.actionSave.triggered.connect(self.on_save)

    def init_storage_view(self):
        self.update_title()
        self.ui.storageView.clear()

        locations = self.storage.get_locations()
        locations_item = QTreeWidgetItem()
        locations_item.setText(0, "Locations")
        for location in locations:
            location_item = QTreeWidgetItem()
            location_item.setText(0, "{} {}".format(location.get_label(), location.get_pos()))
            location_item.setData(0, Qt.UserRole, location)
            locations_item.addChild(location_item)
        self.ui.storageView.addTopLevelItem(locations_item)

        connections = self.storage.get_connections()
        connections_item = QTreeWidgetItem()
        connections_item.setText(0, "Connections")
        for connection in connections:
            connection_item = QTreeWidgetItem()
            location_text = [x.get_label() for x in connection.get_locations()]
            connection_item.setText(0, "{} and {}".format(location_text[0], location_text[1]))
            connection_item.setData(0, Qt.UserRole, connection)
            connections_item.addChild(connection_item)
        self.ui.storageView.addTopLevelItem(connections_item)

        self.ui.storageView.expandAll()
        self.ui.storageView.itemActivated.connect(self.on_storage_view_item_activated)

    def update_title(self):
        self.setWindowTitle("{} {}".format(self.window_title, "*" if self.save_required else ""))

    def on_save(self):
        if self.save_required:
            self.storage.save()
            self.save_required = False
            self.update_title()
            self.ui.statusbar.showMessage("Saved Successfully", 5000)

    def on_storage_view_item_activated(self, item: QTreeWidgetItem, column: int):
        data = item.data(0, Qt.UserRole)
        if isinstance(data, Location):
            self.load_location_sidebar(data)
        elif isinstance(data, Connection):
            pass
        else:
            pass

    def load_location_sidebar(self, location: Location):
        if self.current_editing_location_id != location.get_id():
            pass
        self.ui_form = Ui_Form()
        widget = QWidget()
        self.ui_form.setupUi(widget)
        self.fill_location_sidebar_data(location)
        if self.current_editing_location_id is not None:
            for i in reversed(range(self.ui.sidebar_widget.count())):
                removing = self.ui.sidebar_widget.itemAt(i)
                if removing:
                    removing = removing.widget()
                    self.ui.sidebar_widget.removeWidget(removing)
                    removing.setParent(None)
        self.ui.sidebar_widget.addWidget(widget)
        self.current_editing_location_id = location.get_id()

    def fill_location_sidebar_data(self, location: Location):
        self.ui_form.id_edit.setText(location.get_id())
        self.ui_form.id_edit.textChanged.connect(self.on_location_id_change)
        self.ui_form.label_edit.setText(location.get_label())
        self.ui_form.label_edit.textChanged.connect(self.on_location_label_change)
        x, y = location.get_pos()
        world_dimensions = self.config.get_config_value(ConfigKeys.WorldBorderDimensions)
        self.ui_form.x_edit.setMinimum(world_dimensions.get(ConfigDataKeys.WorldBorderDimensionsMinX))
        self.ui_form.x_edit.setMaximum(world_dimensions.get(ConfigDataKeys.WorldBorderDimensionsMaxX))
        self.ui_form.x_edit.setValue(x)
        self.ui_form.x_edit.valueChanged.connect(self.on_location_x_change)
        self.ui_form.y_edit.setMinimum(world_dimensions.get(ConfigDataKeys.WorldBorderDimensionsMinY))
        self.ui_form.y_edit.setMaximum(world_dimensions.get(ConfigDataKeys.WorldBorderDimensionsMaxY))
        self.ui_form.y_edit.setValue(y)
        self.ui_form.y_edit.valueChanged.connect(self.on_location_y_change)

        for connection in location.get_connections():
            other_location = connection.get_other_side(location)
            item = QListWidgetItem()
            item.setText("{} {}, via {}".format(other_location.get_label(), other_location.get_pos(),
                                                connection.get_label()))
            item.setData(Qt.UserRole, connection)
            self.ui_form.connections_list.addItem(item)

    def on_location_id_change(self, text):
        self.save_required = True
        location = self.storage.get_location_by_id(self.current_editing_location_id)
        location.set_id(text)
        self.storage.update_location(location)

        self.init_storage_view()
        self.current_editing_location_id = location.get_id()

    def on_location_label_change(self, text):
        self.save_required = True
        location = self.storage.get_location_by_id(self.current_editing_location_id)
        location.set_label(text)
        self.storage.update_location(location)

        self.init_storage_view()

    def on_location_x_change(self, value):
        self.save_required = True
        location = self.storage.get_location_by_id(self.current_editing_location_id)
        pos = (value, location.get_pos()[1])
        location.set_pos(pos)
        self.storage.update_location(location)

        self.init_storage_view()

    def on_location_y_change(self, value):
        self.save_required = True
        location = self.storage.get_location_by_id(self.current_editing_location_id)
        pos = (location.get_pos()[0], value)
        location.set_pos(pos)
        self.storage.update_location(location)

        self.init_storage_view()

    @staticmethod
    def make_random_id(length=5):
        characters = []
        for i in range(ord('A'), ord('Z')):
            characters.append(chr(i))
        for i in range(ord('a'), ord('z')):
            characters.append(chr(i))
        for i in range(ord('0'), ord('9')):
            characters.append(chr(i))

        random_id = []
        for i in range(length):
            random_id.append(characters[random.randint(0, len(characters) - 1)])
        return ''.join(random_id)

    def on_add_location(self):
        self.save_required = True
        random_id = self.make_random_id()
        location = Location(random_id, random_id, 0, 0)
        self.storage.add_location(location)
        self.init_storage_view()
        self.load_location_sidebar(location)
        self.current_editing_location_id = location.get_id()


class EditorApplication:
    def __init__(self, storage, config):
        self.storage = storage
        self.config = config

    def run(self):
        app = QApplication(sys.argv)

        window = MainWindow(app, self.storage, self.config)
        window.show()

        sys.exit(app.exec())
