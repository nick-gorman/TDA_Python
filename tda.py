import sys
import os
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QLabel, QGridLayout, QGroupBox
from PyQt5.QtWidgets import QComboBox, QTableWidget, QFrame
from PyQt5.QtWidgets import QPushButton, QVBoxLayout, QHBoxLayout, QAction, qApp, QSizePolicy
from PyQt5 import QtGui, QtCore
import tda_graphs
import images
from data_interface import extract_load_options, get_demographics_table, extract_demographics_options, get_load_table
import pandas as pd


class Tda(QMainWindow):
    def __init__(self):
        # Provide default values.
        self.data_folder = os.getcwd() + '\data'
        self.mapping_file = 'demographics_load_lookup_table.csv'

        # Create widget to contain all the subwidgets and give it a grid layout.
        super().__init__()
        self.centralWidget = QWidget(self)
        self.setCentralWidget(self.centralWidget)
        self.gridlayout = QGridLayout()
        self.centralWidget.setLayout(self.gridlayout)

        # Create variables to store data tables and currently selected load.
        self.demographic_tables = {}
        self.load_tables = {}
        self.selected_load = None

        # Create subsections of gui.
        self.init_menu()
        self.gridlayout.addWidget(Logo('CEEMLogo.png'), 0, 0, 1, 1)
        self.gridlayout.addWidget(Logo('UNSWLogo.png'), 0, 1, 1, 1)
        self.load_selection = \
            LoadSelectionPanel('Select Load', self.give_load, self.get_load_options, self.get_demographics_options,
                               self.update_demographic_data, self.set_load_data)
        self.gridlayout.addWidget(self.load_selection, 1, 0, 2, 2)
        self.tariff_select_panel = TariffSelectionPanel('Select Tariff')
        self.gridlayout.addWidget(self.tariff_select_panel, 2, 2, 1, 1)
        self.results_panel = ResultsPanel('Results', load_data_getter=self.give_load)
        self.gridlayout.addWidget(self.results_panel, 0, 2, 2, 1)

        # Finalise the Gui settings
        self.setGeometry(200, 200, 1200, 700)
        self.centralWidget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.show()

    def init_menu(self):
        menu_bar = self.menuBar()
        project = menu_bar.addMenu('Project')
        save_project = QAction('Save Project', self)
        save_project.setShortcut('Ctrl+S')
        project.addAction(save_project)

    def set_load_data(self, load_data_name, criteria):
        # Check if the full set of load data has been loaded, if not load the data.
        if load_data_name not in self.load_tables:
            self.load_tables[load_data_name] = get_load_table(self.data_folder, load_data_name)
        # Get the demographic data for the particular load table.
        all_load_ids = self.demographic_tables[load_data_name]
        # Choose a subset of the demographic based on the criteria provided.
        demographic_subset = all_load_ids.loc[(all_load_ids[list(criteria)] == pd.Series(criteria)).all(axis=1)]
        # Use the IDs of the subset to select the loads that we need and set this load subset as the selected load.
        just_ids = demographic_subset['HomeID']
        whole_load_table = self.load_tables[load_data_name]
        self.selected_load = whole_load_table.loc[:, ('TimeStamp',) + tuple(just_ids)]

    def give_load(self):
        return self.selected_load

    def get_load_options(self):
        # Find the list of load files that users can select.
        return extract_load_options(self.data_folder)

    def update_demographic_data(self, new_load_data_name):
        # If the demographic data for a load table has not be loaded, then load it and store by reference to the load
        # table.
        if new_load_data_name not in self.demographic_tables:
            self.demographic_tables[new_load_data_name] = get_demographics_table(self.data_folder, new_load_data_name,
                                                                                 self.mapping_file)

    def get_demographics_options(self, load_data_name):
        # Find the demographic information that users can filter on and the potential filtering values.
        return extract_demographics_options(self.demographic_tables[load_data_name])


class Logo(QLabel):
    def __init__(self, name):
        super().__init__()
        self.setPixmap(QtGui.QPixmap(':/{}'.format(name)))
        self.setMinimumSize(50, 50)
        self.setMaximumSize(250, 100)
        self.setScaledContents(True)


class LoadSelectionPanel(QGroupBox):
    def __init__(self, name, get_load, get_load_options, get_demographics_options, update_demographic_data,
                 update_load_function):
        super().__init__(name)

        # Label the load selection bar.
        select_label = QLabel('Select:')

        # Create the main load selection bar.
        self.load_list = QComboBox()
        self.load_list.setMinimumWidth(100)
        self.load_list.addItem('None')
        for file in get_load_options():
            self.load_list.addItem(file)
        # Connect a change in the load bar selection to function that updates the demographic filtering options.
        self.load_list.currentIndexChanged.connect(
            lambda: self.update_demographics_options(self.load_list.currentText(),update_demographic_data,
                                                 get_demographics_options))

        # Create a button that set the selected load based on input from the load selection bar and the demographic
        # options.
        set_button = QPushButton('Set')
        set_button.clicked.connect(lambda: self.update_active_load_data(update_load_function, get_load))
        set_button.setFixedWidth(50)

        # Place the load selection widgets in a horizontal bar layout.
        self.top_bar = QHBoxLayout() # layout container for widgets we want aligned horizontally.
        self.top_bar.addWidget(select_label,  alignment=QtCore.Qt.AlignLeft)
        self.top_bar.addWidget(self.load_list, alignment=QtCore.Qt.AlignLeft)
        self.top_bar.addStretch(1) # Spacer between selection list and button.
        self.top_bar.addWidget(set_button)
        self.top_bar.setAlignment(QtCore.Qt.AlignTop)

        # Visually separate the load selection bar and the demographic selections with a line.
        separating_bar = QFrame()
        separating_bar.setFrameShape(QFrame.HLine)
        separating_bar.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Expanding)
        separating_bar.setLineWidth(1)
        separating_bar.setFrameShadow(QFrame.Sunken)

        # Create a mostly blank layout for the demographic selections, this get filled later once a load is selected.
        self.demographics = QVBoxLayout()
        self.demographics.insertWidget(0, QLabel('Select user group based on demongraphic info:'))
        self.demographics.addStretch(1)
        self.demographics.rows = []

        # Create a box to contain the load plot.
        self.plot_group = QGroupBox()
        self.plot_group.setFlat(True)
        self.plot = tda_graphs.LoadPlot('Annual Average Profile', None)
        self.plot_group.header_layout = QHBoxLayout()
        self.plot_group.user_selected_label = QLabel('Number of users: N/A')
        self.plot_group.show_label = QLabel('Show')
        self.plot_group.plot_selection = QComboBox()
        for plot_type in self.plot.types.keys():
            self.plot_group.plot_selection.addItem(plot_type)
        self.plot_group.header_layout.addWidget(self.plot_group.user_selected_label)
        self.plot_group.header_layout.addWidget(self.plot_group.show_label)
        self.plot_group.header_layout.addWidget(self.plot_group.plot_selection)
        # Create a vertical layout in group box and place the header layout at the top and the plot below.
        self.plot_group.plot_group_layout = QVBoxLayout()
        self.plot_group.plot_group_layout.addLayout(self.plot_group.header_layout)
        self.plot_group.plot_group_layout.addWidget(self.plot)
        self.plot_group.setLayout(self.plot_group.plot_group_layout)

        # Added the sub components to the main layout of the load selection panel.
        layout = QVBoxLayout()
        layout.addLayout(self.top_bar, 0)
        layout.addWidget(separating_bar, 0)
        layout.addLayout(self.demographics, 1)
        layout.addWidget(self.plot_group, 1)
        layout.setAlignment(QtCore.Qt.AlignTop)
        self.setLayout(layout)

        # Give the panel a maximum width.
        self.setMaximumWidth(500)

    def update_demographics_options(self, load_data_name, update_demographic_data, get_demographics_options):
        # Clear any previous options.
        for row in self.demographics.rows:
            self.clearLayout(row)
            self.demographics.removeItem(row)

        # If the option selected is not the None option then create the relevant demographic selection boxes.
        self.demographics.comboboxes = {}
        if load_data_name != 'None':
            # Make sure we have the demographic data for the load selected.
            update_demographic_data(load_data_name)
            # Get the options for the demographic data.
            demographic_options = get_demographics_options(load_data_name)
            # For each demographic data type add a combo box with all its possible values.
            for data_type, possible_values in demographic_options.items():
                label = QLabel(data_type)
                select_list = QComboBox()
                select_list.addItem('All')
                for value in possible_values:
                    select_list.addItem(str(value))
                row = QHBoxLayout()
                # Store reference to the selection boxes by name so they can be accessed later.
                self.demographics.comboboxes[data_type] = select_list
                row.addWidget(label)
                row.addWidget(select_list)
                row.addSpacing(50)
                self.demographics.rows.append(row)
                self.demographics.insertLayout(self.demographics.count()-1, row)

    def get_demographic_selection_criteria(self):
        # Read in the criteria from selection boxes.
        selection_criteria = {}
        for data_type, combo_box in self.demographics.comboboxes.items():
            if combo_box.currentText() != 'All':
                selection_criteria[data_type] = combo_box.currentText()
        return selection_criteria

    def update_active_load_data(self, update_load_function, get_load_function):
        # Get selection criteria.
        selection_criteria = self.get_demographic_selection_criteria()
        # Update the selected load.
        update_load_function(self.load_list.currentText(), selection_criteria)
        # Delete the current plot.
        self.plot.deleteLater()
        self.plot = tda_graphs.LoadPlot(self.plot_group.plot_selection.currentText(), get_load_function)
        self.plot_group.plot_group_layout.addWidget(self.plot)

    def clearLayout(self, layout):
        # Clear the widgets from a layout.
        while layout.count():
            child = layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()


class ResultsPanel(QGroupBox):
    def __init__(self, panel_name, load_data_getter):
        super().__init__(panel_name)
        set_button = QPushButton('report load')
        set_button.clicked.connect(self.print_load)
        set_button.setFixedWidth(100)
        dual_variable_canvas = tda_graphs.DualVariablePlot()
        layout = QVBoxLayout()
        layout.addWidget(set_button)
        layout.addWidget(dual_variable_canvas)
        self.setLayout(layout)
        self.load_data_getter = load_data_getter

    def print_load(self):
        # load the data
        self.load_data = None
        # Update demographics options
        self.demographic_options = None
        print(self.load_data_getter())
        pass


class TariffSelectionPanel(QGroupBox):
    def __init__(self, name):
        super().__init__(name)

        self.selection_column = QVBoxLayout()
        self.view_and_edit_column = QVBoxLayout()
        self.gridlayout = QGridLayout()
        self.gridlayout.addLayout(self.selection_column, 0, 0)
        self.gridlayout.addLayout(self.view_and_edit_column, 0, 1)
        self.setLayout(self.gridlayout)
        self.cases = None


app = QApplication(sys.argv)
x = Tda()
sys.exit(app.exec_())