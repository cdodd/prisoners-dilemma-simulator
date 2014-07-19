# 3rd party modules
from PyQt4.QtCore import *
from PyQt4.QtGui import *

class OptionsMenu(QWidget):
    def __init__(self, parent=None):
        QWidget.__init__(self, parent)

        self.player_list = QListWidget()
        player_box = QHBoxLayout()
        player_box.addWidget(self.player_list)

        self.add_player_btn = QPushButton(QIcon('images/add.png'), '')
        self.clear_player_btn = QPushButton(QIcon('images/delete.png'), '')
        button_box = QVBoxLayout()
        button_box.addWidget(self.add_player_btn)
        button_box.addWidget(QPushButton(QIcon('images/user_edit.png'), ''))
        button_box.addWidget(self.clear_player_btn)
        button_box.addStretch()

        player_box.addLayout(button_box)

        player_list_gb = QGroupBox('Player List:')
        player_list_gb.setLayout(player_box)

        # Create the "Game Options" options
        self.rounds_sb = QSpinBox()
        self.rounds_sb.setRange(0, 1000)
        self.rounds_sb.setSingleStep(1)
        self.rounds_sb.setValue(10)

        self.iterations_sb = QSpinBox()
        self.iterations_sb.setRange(0, 100000)
        self.iterations_sb.setSingleStep(0.1)
        self.iterations_sb.setValue(30)

        game_options_box = QGridLayout()
        game_options_box.addWidget(QLabel('Rounds per Game'), 0, 0)
        game_options_box.addWidget(self.rounds_sb, 0, 1)
        game_options_box.addWidget(QLabel('Iterations'), 1, 0)
        game_options_box.addWidget(self.iterations_sb, 1, 1)

        game_option_gb = QGroupBox('Game Options:')
        game_option_gb.setLayout(game_options_box)

        # Create the "Graph Options" options
        self.legend_cb = QCheckBox('Show Legend')
        self.legend_cb.setChecked(True)
        self.connect(self.legend_cb, SIGNAL('stateChanged(int)'), self.legend_change)
        self.grid_cb = QCheckBox('Show Grid')
        self.grid_cb.setChecked(True)
        self.legend_loc_lbl = QLabel('Legend Location')
        self.legend_loc_cb = QComboBox()
        self.legend_loc_cb = QComboBox()
        self.legend_loc_cb.addItems(
            [x.title() for x in [
                'right',
                'center',
                'lower left',
                'center right',
                'upper left',
                'center left',
                'upper right',
                'lower right',
                'upper center',
                'lower center',
                'best'
                ]
            ]
        )
        self.legend_loc_cb.setCurrentIndex(6)

        cb_box = QHBoxLayout()
        cb_box.addWidget(self.legend_cb)
        cb_box.addWidget(self.grid_cb)
        cb_box.addStretch()

        legend_box = QHBoxLayout()
        legend_box.addWidget(self.legend_loc_cb)
        legend_box.addStretch()

        graph_box = QVBoxLayout()
        graph_box.addLayout(cb_box)
        graph_box.addWidget(self.legend_loc_lbl)
        graph_box.addLayout(legend_box)

        graph_gb = QGroupBox('Graph Options:')
        graph_gb.setLayout(graph_box)

        self.update_btn = QPushButton(QIcon('images/calculator.png'), 'Run Iterations')

        # Create the main layout
        container = QVBoxLayout()
        container.addWidget(player_list_gb)
        container.addWidget(game_option_gb)
        container.addWidget(graph_gb)
        container.addWidget(self.update_btn)
        container.addStretch()
        self.setLayout(container)

    def legend_change(self):
        self.legend_loc_cb.setEnabled(self.legend_cb.isChecked())
        self.legend_loc_lbl.setEnabled(self.legend_cb.isChecked())
