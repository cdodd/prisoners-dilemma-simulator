#!/usr/bin/env python
# Copyright (c) 2013 Craig Dodd <github@craigdodd.co.uk>
#
# This file is part of the "Prisoner's Dilemma Simulator" application.
#
# The "Prisoner's Dilemma Simulator" is free software: you can redistribute it
# and/or modify it under the terms of the GNU General Public License as
# published by the Free Software Foundation, either version 3 of the License,
# or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE. See the GNU General Public License for more
# details.
#
# You should have received a copy of the GNU General Public License along with
# this program. If not, see <http://www.gnu.org/licenses/>.

"""
Top level application file for the Prisoner's Dilemma Simulator application.
"""
__version__ = '1.0'
APP_NAME = "Prisoner's Dilemma Simulator"
AUTHOR = 'Craig Dodd'
ORGANIZATION = 'CraigDodd'
COPYRIGHT = 'GNU General Public License v3'

# Try to import required modules
try:

    # Standard library modules
    import sys

    # 3rd party modules
    import matplotlib
    from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
    from matplotlib.backends.backend_qt4agg import NavigationToolbar2QTAgg as NavigationToolbar
    from matplotlib.figure import Figure
    from PyQt4.QtCore import *
    from PyQt4.QtGui import *

    # Local application modules
    from dialogs import AddPlayerDlg
    from dialogs import ProcessDataDlg
    from optionsmenu import OptionsMenu
    import resources
    import strategy

# Display a Tkinter messagebox if a module failed to import (assumes
# that the Tkinter modules are available, which they should be)
except ImportError, e:
    import Tkinter, tkMessageBox
    root = Tkinter.Tk()
    root.withdraw()

    # Get the name of the item that could not be imported and display an error messagebox.
    module_name = e.message.split()[-1]
    tkMessageBox.showerror('Import Error',
                           'Failed to import "%s". This is required for the %s to run.' % (module_name, APP_NAME))
    sys.exit(1)

# Set the global font size for the matplotlib module
font = {'size': 8}
matplotlib.rc('font', **font)

class AppForm(QMainWindow):
    """
    This class defines the GUI and behaviour of the main application window.
    """
    def __init__(self, parent=None):
        QMainWindow.__init__(self, parent)

        # Set the window title
        self.setWindowTitle("Prisoner's Dilemma Simulator")

        # Create the options menu in a dock widget
        self.options_menu = OptionsMenu()
        dock = QDockWidget('Options', self)
        dock.setFeatures(
            QDockWidget.NoDockWidgetFeatures |
            QDockWidget.DockWidgetMovable |
            QDockWidget.DockWidgetFloatable
        )
        dock.setAllowedAreas(Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea)
        dock.setWidget(self.options_menu)
        self.addDockWidget(Qt.LeftDockWidgetArea, dock)

        self.connect(self.options_menu.legend_cb, SIGNAL('stateChanged(int)'), self.redraw_graph)
        self.connect(self.options_menu.grid_cb, SIGNAL('stateChanged(int)'), self.redraw_graph)
        self.connect(self.options_menu.update_btn, SIGNAL('clicked()'), self.run_game)
        self.connect(self.options_menu.add_player_btn, SIGNAL('clicked()'), self.add_player)
        self.connect(self.options_menu.clear_player_btn, SIGNAL('clicked()'), self.clear_player_list)
        self.connect(self.options_menu.legend_loc_cb, SIGNAL('currentIndexChanged(int)'), self.redraw_graph)

        # Set up the graph plot
        fig = Figure((7.0, 3.0), dpi=100)
        self.canvas = FigureCanvas(fig)
        self.canvas.setParent(self)
        self.axes = fig.add_subplot(111)

        # Create the navigation toolbar
        self.mpl_toolbar = NavigationToolbar(self.canvas, self.canvas)

        hbox = QHBoxLayout()
        vbox = QVBoxLayout()
        vbox.addWidget(self.canvas)
        vbox.addLayout(hbox)

        self.setCentralWidget(self.canvas)
        self.graph_data = {}

        # Create menubar actions
        file_exit_action = QAction('E&xit', self)
        file_exit_action.setToolTip('Exit')
        file_exit_action.setIcon(QIcon(':/images/door_open.png'))
        self.connect(file_exit_action, SIGNAL('triggered()'), self.close)

        about_action = QAction('About', self)
        about_action.setToolTip('About')
        about_action.setIcon(QIcon(':/images/icon_info.gif'))
        self.connect(about_action, SIGNAL('triggered()'), self.show_about)

        # Create the menubar
        file_menu = self.menuBar().addMenu('&File')
        file_menu.addAction(file_exit_action)

        help_menu = self.menuBar().addMenu('&Help')
        help_menu.addAction(about_action)

        self.redraw_graph()
        self.strategy_list = []

    def add_player(self):
        add_player_dlg = AddPlayerDlg(self)
        if add_player_dlg.exec_():
            c = add_player_dlg.c_sb.value()
            d = add_player_dlg.d_sb.value()
            i = add_player_dlg.i_sb.value()
            quantity = add_player_dlg.quantity_sb.value()

            for x in range(quantity):
                self.strategy_list.append(strategy.CDIStrategy(c, d, i))
    
            self.update_player_list()

    def run_game(self):
        if not len(self.strategy_list):
            QMessageBox.critical(self, 'Error', 'You have not added any players.', QMessageBox.Ok)
            return

        self.options_menu.legend_cb.setEnabled(True)
        self.options_menu.legend_loc_cb.setEnabled(True)
        self.options_menu.legend_loc_lbl.setEnabled(True)

        # Create the desired amount of players
        player_list = [strategy.Player(x) for x in self.strategy_list]

        # Get the number of rounds to play
        rounds = self.options_menu.iterations_sb.value()

        process_dlg = ProcessDataDlg(player_list, rounds, self)
        if process_dlg.exec_():

            # Save the processed data & update the graph
            self.graph_data = process_dlg.results
            self.redraw_graph()

        self.update_player_list()

    def update_player_list(self):
        data = {}

        for i in self.strategy_list:
            try:
                data[i.name] += 1
            except KeyError:
                data[i.name] = 1

        self.options_menu.player_list.clear()
        for k, v in data.items():
            self.options_menu.player_list.addItem('%s (%d)' % (k, v))

    def clear_player_list(self):
        self.strategy_list = []
        self.update_player_list()

    def clear_graph(self):
        self.graph_data = {}

        # Redraw the graph
        self.redraw_graph()

        self.options_menu.legend_cb.setDisabled(True)
        self.options_menu.legend_loc_cb.setDisabled(True)
        self.options_menu.legend_loc_lbl.setDisabled(True)

    def redraw_graph(self):
        """
        Updates the graph. Should be called after any graph options have been
        changed. (i.e. new plot data or turning the legend on/off)
        """

        # Clear the graph
        self.axes.clear()

        # Create the graph labels
        self.axes.set_xlabel('Iterations')
        self.axes.set_ylabel('Player Population Size')

        # Plot the strategy data if there is any
        if self.graph_data:
            # Plot the data
            for strategy_name, count in self.graph_data.items():
                self.axes.plot(count, label=strategy_name)

            # Create the legend if necessary
            if self.options_menu.legend_cb.isChecked():
                legend_loc = str(self.options_menu.legend_loc_cb.currentText()).lower()
                legend = matplotlib.font_manager.FontProperties(size=10)
                self.axes.legend(loc=legend_loc, prop=legend)

        # Set the grid lines if necessary
        self.axes.grid(self.options_menu.grid_cb.isChecked())

        # Draw the graph
        self.canvas.draw()

    def show_about(self):
        """Display the "about" dialog box."""
        message = '''<font size="+2">%s</font> v%s
                     <p>Evolutionary Prisoner's Dilemma Simulator.
                     <p>Written by %s
                     <br>&copy; %s
                     <p>Icons by <a href="http://www.famfamfam.com/">famfamfam</a> and
                     <a href="http://dryicons.com/">dryicons</a>.''' % (APP_NAME,
                                                                        __version__,
                                                                        AUTHOR,
                                                                        COPYRIGHT)

        QMessageBox.about(self, 'About ' + APP_NAME, message)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setWindowIcon(QIcon(':/images/icon.png'))
    form = AppForm()
    form.show()
    app.exec_()
