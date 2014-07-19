# Standard library modules
import random

# 3rd party modules
from PyQt4.QtCore import *
from PyQt4.QtGui import *

# Local application modules
from game import SimpleGame

class RunGame(QThread):
    """Thread to run games in."""
    def __init__(self, players, rounds, parent):
        QThread.__init__(self, parent)
        self.players = players
        self.rounds = rounds
        self.parent = parent

    def run(self):
        # Create a dictionary to map each strategy to a list containing the
        # population count for that strategy for each round.
        population_data = {}
        for player in self.players:
            try:
                population_data[player.strategy.name][0] += 1
            except KeyError:
                population_data[player.strategy.name] = [1]

        for i in range(self.rounds):
            # Randomize the player list
            random.shuffle(self.players)

            # Create an iterable of the players & pair them up
            players_iter = iter(self.players)
            random_pairs = zip(players_iter, players_iter)

            # Play the games
            for player1, player2 in random_pairs:
                simple_game = SimpleGame(player1, player2)
                simple_game.run(iterations=5)    # SHOULD THIS BE HARD-CODED?
                self.emit(SIGNAL('gamePlayed()'))

            # Get all the players to "evolve"
            for player in self.players:
                player.evolve()

            # Count the strategies of the n'th generation
            for player in self.players:
                try:
                    population_data[player.strategy.name][i + 1] += 1
                except IndexError:
                    population_data[player.strategy.name].append(1)

        # Append a zero onto the population count of any strategy that died out
        for counts in population_data.values():
            if len(counts) < self.rounds:
                counts.append(0)

        # Save the results in the parent object & signal that processing is complete
        self.parent.results = population_data
        self.emit(SIGNAL('finished()'))


class ProcessDataDlg(QDialog):
    def __init__(self, players, rounds=10, parent=None):
        QDialog.__init__(self, parent, Qt.Tool |
                                       Qt.FramelessWindowHint |
                                       Qt.WindowTitleHint)

        # Set the dialog size & title
        self.resize(parent.width() * 0.5, 50)
        self.setWindowTitle('Processing...')

        # Create the progress bar & a mutex for accessing it
        self.progress = QProgressBar()
        self.progress.setValue(0)
        self.progress.setMaximum(rounds * (len(players) / 2))
        self.pb_mutex = QMutex()

        # Create the form layout
        layout = QVBoxLayout()
        layout.addWidget(self.progress)
        self.setLayout(layout)

        # Create a thread to run the game in
        thread = RunGame(players, rounds, parent=self)

        # Connect the thread signals to the appropriate methods
        self.connect(thread, SIGNAL('gamePlayed()'), self.increment_progress)
        self.connect(thread, SIGNAL('finished()'), self.accept)

        # Start the thread
        thread.start()

    def increment_progress(self):
        """Increments the progress bar on the GUI."""
        self.pb_mutex.lock()
        try:
            self.progress.setValue(self.progress.value() + 1)
        finally:
            self.pb_mutex.unlock()


class AddPlayerDlg(QDialog):
    def __init__(self, parent=None):
        QDialog.__init__(self, parent)

        # Set the dialog title
        self.setWindowTitle('Add Player(s)')

        # Create the CDI widgets
        self.c_sb = QDoubleSpinBox()
        self.d_sb = QDoubleSpinBox()
        self.i_sb = QDoubleSpinBox()
        self.quantity_sb = QSpinBox()

        for widget in (self.c_sb, self.d_sb, self.i_sb):
            widget.setRange(0, 1)
            widget.setSingleStep(0.1)

        # Create the CDI widgets layout
        cdi_box = QHBoxLayout()
        cdi_box = QHBoxLayout()
        cdi_box.addWidget(QLabel('C'))
        cdi_box.addWidget(self.c_sb)
        cdi_box.addWidget(QLabel('D'))
        cdi_box.addWidget(self.d_sb)
        cdi_box.addWidget(QLabel('I'))
        cdi_box.addWidget(self.i_sb)
        cdi_gb = QGroupBox('Initial Strategy')
        cdi_gb.setLayout(cdi_box)

        # Create the quantity widget
        self.quantity_sb.setRange(1, 10000)
        self.quantity_sb.setSingleStep(1)

        # Create the quantity widget layout
        quantity_box = QHBoxLayout()
        quantity_box.addWidget(self.quantity_sb)
        quantity_gb = QGroupBox('Quantity of Players')
        quantity_gb.setLayout(quantity_box)

        # Make the ok/cancel button box
        button_box = QDialogButtonBox(QDialogButtonBox.Ok |
                                      QDialogButtonBox.Cancel)
        self.connect(button_box, SIGNAL('accepted()'), self, SLOT('accept()'))
        self.connect(button_box, SIGNAL('rejected()'), self, SLOT('reject()'))

        # Create the main layout
        container = QVBoxLayout()
        container.addWidget(cdi_gb)
        container.addWidget(quantity_gb)
        container.addWidget(button_box)
        self.setLayout(container)
