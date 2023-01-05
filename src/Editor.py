import multiprocessing
import random
import sys
import typing

from PySide6 import QtCore
from PySide6.QtCore import QPoint, QThread, QObject
from PySide6.QtGui import Qt, QIcon, QAction, QCursor
from PySide6.QtWidgets import QApplication, QMainWindow, QTreeWidgetItem, QWidget, QListWidgetItem, QDialog, QMenu, \
    QMessageBox

from src.Config import Config, ConfigKeys, ConfigDataKeys
from src.Connection import Connection
from src.Location import Location
from src.StorageProvider import StorageProvider
from src.ui_mainwindow import Ui_MainWindow
from src.ui_editor_sidewindow import Ui_Form as EditorSideWindowForm
from src.ui_editor_connection import Ui_Form as EditorConnectionForm
from src.ui_editor_cachewindow import Ui_Form as EditorCacheForm


class CacheThreadWorker(QObject):
    finished = QtCore.Signal()
    progress = QtCore.Signal(int, int)

    def __init__(self, storage, max_x, min_x, max_y, min_y, threads):
        super().__init__()
        self.storage = storage
        self.max_x = max_x
        self.min_x = min_x
        self.max_y = max_y
        self.min_y = min_y
        self.threads = threads

    def run(self):
        total_num = (self.max_x - self.min_x) * (self.max_y - self.min_y)
        self.storage.make_cache(self.min_x, self.max_x, self.min_y, self.max_y, self.threads,
                                lambda v: self.progress.emit(v, total_num))
        self.finished.emit()


class MainWindow(QMainWindow):
    def __init__(self, app, storage: StorageProvider, config: Config):
        super().__init__()
        self.app = app
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.storage = storage
        self.config = config

        self.cra_icon = QIcon("./icon.png")
        self.window_title = "Bilbcraft Route Planner Editor"
        self.save_required = False
        self.current_editing_location_id = None
        self.ui_form = None
        self.connection_form_modal = None
        self.connection_form_modal_dialog = None
        self.current_editing_connection: typing.Optional[Connection] = None
        self.ui_cache_modal: typing.Optional[EditorCacheForm] = None
        self.ui_cache_dialog_modal = None
        self.cache_worker = None
        self.cache_thread = None

        self.setWindowIcon(self.cra_icon)
        self.setup_signals()
        self.init_storage_view()

    def setup_signals(self):
        self.ui.actionQuit.triggered.connect(sys.exit)
        self.ui.actionAddLocation.triggered.connect(self.on_add_location)
        self.ui.actionAddConnection.triggered.connect(self.on_add_connection)
        self.ui.actionBuild_Cache.triggered.connect(self.on_build_cache)
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
            if connection.get_is_train():
                connection_item.setIcon(0, self.cra_icon)
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

    def on_storage_view_item_activated(self, item: QTreeWidgetItem, _):
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
        self.ui_form = EditorSideWindowForm()
        widget = QWidget()
        self.ui_form.setupUi(widget)
        self.fill_location_sidebar_data(location)
        if self.current_editing_location_id is not None:
            self.clear_location_sidebar()
        self.ui.sidebar_widget.addWidget(widget)
        self.current_editing_location_id = location.get_id()
        self.ui_form.delete_location.clicked.connect(self.on_sidebar_delete)

    def clear_location_sidebar(self):
        for i in reversed(range(self.ui.sidebar_widget.count())):
            removing = self.ui.sidebar_widget.itemAt(i)
            if removing:
                removing = removing.widget()
                self.ui.sidebar_widget.removeWidget(removing)
                removing.setParent(None)

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
            if connection.get_is_train():
                item.setIcon(self.cra_icon)
            self.ui_form.connections_list.addItem(item)
        self.ui_form.connections_list.itemActivated.connect(self.on_connection_activated_edit)

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
        location = Location(random_id, random_id, 0, 0, None)
        self.storage.add_location(location)
        self.init_storage_view()
        self.load_location_sidebar(location)
        self.current_editing_location_id = location.get_id()

    def on_add_connection(self):
        if self.current_editing_location_id is None:
            return

        editing_location = self.storage.get_location_by_id(self.current_editing_location_id)
        self.show_connection_modal(editing_location, self._add_connection_button_modifier, title="Create Connection")

    def _add_connection_button_modifier(self, connection_form: EditorConnectionForm):
        connection_form.ok_button.clicked.connect(self.on_add_connection_modal_ok)
        connection_form.cancel_button.clicked.connect(self.on_add_connection_modal_cancel)
        connection_form.delete_connection.setDisabled(True)

    @staticmethod
    def _unique(data: typing.List):
        values = []
        for x in data:
            if x in values:
                continue
            values.append(x)
        return values

    def show_connection_modal(self, editing_location: Location,
                              button_modifier: typing.Callable[[EditorConnectionForm], None],
                              default_2nd_location=None, title=None):
        connection_form = EditorConnectionForm()
        widget = QWidget()
        connection_form.setupUi(widget)

        connection_form.location_combo1.addItem("{} {}".format(editing_location.get_label(),
                                                               editing_location.get_pos()),
                                                userData=editing_location)
        connection_form.location_combo1.setDisabled(True)
        description = ""
        if self.current_editing_connection is None:
            connection_label = self.make_random_id()
        else:
            connection_label = self.current_editing_connection.get_label()
            connection_form.edit_train.setCheckState(Qt.Checked if self.current_editing_connection.get_is_train()
                                                     else Qt.Unchecked)
            connection_form.edit_weight.setValue(self.current_editing_connection.get_weight())
            description = self.current_editing_connection.get_description()
        connection_form.edit_description.setPlainText(description)

        connection_labels = self._unique([x.get_label() for x in self.storage.get_connections()])
        label_index = None
        for i, label in enumerate(connection_labels):
            if label == connection_label:
                label_index = i
            connection_form.edit_label.addItem(label)
        if label_index is not None:
            connection_form.edit_label.setCurrentIndex(label_index)

        default_index = None
        for i, location in enumerate(self.storage.get_locations()):
            connection_form.location_combo2.addItem("{} {}".format(location.get_label(), location.get_pos()),
                                                    userData=location)
            if default_2nd_location is not None and location.get_id() == default_2nd_location:
                default_index = i
        if default_index is not None:
            connection_form.location_combo2.setCurrentIndex(default_index)

        self.connection_form_modal = connection_form

        button_modifier(connection_form)

        widget.setWindowModality(Qt.WindowModality.ApplicationModal)
        if title is not None:
            widget.setWindowTitle(title)

        widget.show()
        self.connection_form_modal_dialog = widget

    def on_add_connection_modal_ok(self):
        self.save_required = True

        connection = Connection(self.connection_form_modal.edit_weight.value(),
                                self.connection_form_modal.edit_train.checkState() == Qt.Checked,
                                self.connection_form_modal.edit_label.currentText(),
                                self.connection_form_modal.edit_description.toPlainText())

        location_1 = self.connection_form_modal.location_combo1.itemData(
            self.connection_form_modal.location_combo1.currentIndex())
        location_2 = self.connection_form_modal.location_combo2.itemData(
            self.connection_form_modal.location_combo2.currentIndex())

        connection.add_location(location_1)
        connection.add_location(location_2)
        self.storage.add_connection(connection)

        self.init_storage_view()
        self.load_location_sidebar(self.storage.get_location_by_id(self.current_editing_location_id))
        self.connection_form_modal = None
        self.connection_form_modal_dialog.close()
        self.connection_form_modal_dialog = None

    def on_add_connection_modal_cancel(self):
        self.connection_form_modal = None
        self.connection_form_modal_dialog.close()
        self.connection_form_modal_dialog = None

    def on_connection_activated_edit(self, item: QListWidgetItem):
        connection = item.data(Qt.UserRole)
        location = self.storage.get_location_by_id(self.current_editing_location_id)
        self.current_editing_connection = connection
        self.show_connection_modal(location, self._edit_connection_button_modifier,
                                   connection.get_other_side(location).get_id(), title="Update Connection")

    def _edit_connection_button_modifier(self, connection_form: EditorConnectionForm):
        connection_form.ok_button.clicked.connect(self.on_edit_connection_modal_ok)
        connection_form.ok_button.setText("Update")
        connection_form.cancel_button.clicked.connect(self.on_edit_connection_modal_cancel)
        connection_form.delete_connection.clicked.connect(self.on_edit_connection_modal_delete)

    def on_edit_connection_modal_ok(self):
        self.save_required = True

        connection = self.current_editing_connection
        connection.set_weight(self.connection_form_modal.edit_weight.value())
        connection.set_is_train(self.connection_form_modal.edit_train.checkState() == Qt.Checked)
        connection.set_label(self.connection_form_modal.edit_label.currentText())

        location_1 = self.connection_form_modal.location_combo1.itemData(
            self.connection_form_modal.location_combo1.currentIndex())
        old_location = connection.get_other_side(location_1)
        location_2 = self.connection_form_modal.location_combo2.itemData(
            self.connection_form_modal.location_combo2.currentIndex())

        connection.remove_location(old_location)
        connection.add_location(location_2)
        self.storage.update_connection(connection)

        connection.set_description(self.connection_form_modal.edit_description.toPlainText())

        self.init_storage_view()
        self.load_location_sidebar(self.storage.get_location_by_id(self.current_editing_location_id))
        self.connection_form_modal = None
        self.connection_form_modal_dialog.close()
        self.connection_form_modal_dialog = None

    def on_edit_connection_modal_cancel(self):
        self.connection_form_modal = None
        self.connection_form_modal_dialog.close()
        self.connection_form_modal_dialog = None
        self.current_editing_connection = None

    def on_edit_connection_modal_delete(self):
        message_box = QMessageBox()
        message_box.setWindowTitle("Confirm delete connection")
        message_box.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        message_box.setDefaultButton(QMessageBox.No)
        locations = self.current_editing_connection.get_locations()
        location_1 = locations[0].get_label()
        location_2 = locations[1].get_label()
        via = self.current_editing_connection.get_label()
        message_box.setText("Are you sure you want to delete the connection between {} and {} via {}?".format(
            location_1, location_2, via
        ))
        if message_box.exec_() == QMessageBox.Yes:
            self.save_required = True
            self.storage.delete_connection(self.current_editing_connection)
            self.init_storage_view()
            self.load_location_sidebar(self.storage.get_location_by_id(self.current_editing_location_id))
            self.on_edit_connection_modal_cancel()
            self.ui.statusbar.showMessage("Deleted connection between {} and {} via {}".format(
                location_1, location_2, via
            ), 5000)

    def on_sidebar_delete(self):
        message_box = QMessageBox()
        message_box.setWindowTitle("Confirm delete location")
        message_box.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        message_box.setDefaultButton(QMessageBox.No)
        location = self.storage.get_location_by_id(self.current_editing_location_id)
        num_connections = len(location.get_connections())
        message_box.setText("Are you sure you want to delete the location {} and all {} connections?".format(
            location.get_label(), num_connections
        ))
        if message_box.exec_() == QMessageBox.Yes:
            self.save_required = True
            self.storage.delete_location(location)
            self.init_storage_view()
            self.clear_location_sidebar()
            self.ui.statusbar.showMessage("Deleted location {} and {} connections".format(
                location.get_label(), num_connections
            ), 5000)

    def on_build_cache(self):
        cache_form = EditorCacheForm()
        self.ui_cache_modal = cache_form
        widget = QWidget()
        cache_form.setupUi(widget)

        cache_form.start_button.pressed.connect(self.on_begin_cache)
        cache_form.edit_threads.setMinimum(1)
        num_cpus = multiprocessing.cpu_count()
        cache_form.edit_threads.setMaximum(num_cpus)
        cache_form.edit_threads.setValue(num_cpus)

        dimensions = self.config.get_config_value(ConfigKeys.WorldBorderDimensions)
        for x in [cache_form.edit_x_max, cache_form.edit_x_min]:
            x.setMinimum(dimensions.get(ConfigDataKeys.WorldBorderDimensionsMinX))
            x.setMaximum(dimensions.get(ConfigDataKeys.WorldBorderDimensionsMaxX))
        for y in [cache_form.edit_y_max, cache_form.edit_y_min]:
            y.setMinimum(dimensions.get(ConfigDataKeys.WorldBorderDimensionsMinY))
            y.setMaximum(dimensions.get(ConfigDataKeys.WorldBorderDimensionsMaxY))

        dialog = QDialog()
        self.ui_cache_dialog_modal = dialog
        dialog.children().append(widget)
        widget.setParent(dialog)
        dialog.setWindowModality(Qt.WindowModality.ApplicationModal)
        dialog.setWindowTitle("Cache")
        dialog.show()
        dialog.exec_()

    def on_begin_cache(self):
        for x in [self.ui_cache_modal.edit_x_min, self.ui_cache_modal.edit_x_max,
                  self.ui_cache_modal.edit_y_min, self.ui_cache_modal.edit_y_max]:
            x.setDisabled(True)
        self.ui_cache_modal.start_button.setDisabled(True)
        self.ui_cache_modal.edit_threads.setDisabled(True)

        min_x = self.ui_cache_modal.edit_x_min.value()
        max_x = self.ui_cache_modal.edit_x_max.value()
        min_y = self.ui_cache_modal.edit_y_min.value()
        max_y = self.ui_cache_modal.edit_y_max.value()
        threads = self.ui_cache_modal.edit_threads.value()

        self.cache_worker = CacheThreadWorker(self.storage, max_x, min_x, max_y, min_y, threads)
        self.cache_thread = QThread()
        self.cache_worker.moveToThread(self.cache_thread)

        self.cache_worker.finished.connect(self.cache_thread.quit)
        self.cache_worker.finished.connect(self.cache_worker.deleteLater)
        self.cache_thread.started.connect(self.cache_worker.run)
        self.cache_thread.finished.connect(self.cache_thread.deleteLater)
        self.cache_worker.finished.connect(self.on_cache_end)
        self.cache_worker.progress.connect(self.update_percent_bar)

        self.cache_thread.start()

    def on_cache_end(self):
        self.ui_cache_dialog_modal.close()
        self.ui_cache_dialog_modal = None
        self.ui_cache_modal = None
        self.cache_worker = None

    def update_percent_bar(self, v, total_num):
        self.ui_cache_modal.progressBar.setValue(v // total_num * 100)
        self.ui_cache_modal.progress_text.setText("{} / {}".format(v, total_num))


class EditorApplication:
    def __init__(self, storage, config):
        self.storage = storage
        self.config = config

    def run(self):
        app = QApplication(sys.argv)

        window = MainWindow(app, self.storage, self.config)
        window.show()

        sys.exit(app.exec_())
