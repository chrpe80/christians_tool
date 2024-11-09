import pandas as pd
from PySide6 import QtWidgets, QtCore
import sys
import os
import re

settings = {
    "fixed_width_container": 700,
    "x": 0,
    "y": 0,
    "w": 900,
    "h": 400
}


class Data:
    """
    Manages data and observers for various dataframes and provides
    methods to store them to CSV files.
    """

    def __init__(self):
        """
        Initializes the Data class with empty dataframes and an empty observer registry.
        """
        self._samsa_df = None
        self._tes_df = None
        self._korttid_df = None
        self._observers = {}

    def register_observer(self, observer, key):
        """
        Registers an observer with a specific key.

        :param observer: The observer to register.
        :param key: The key that identifies the observer.
        """
        self._observers[key] = observer

    def notify_sa_observer(self):
        """
        Notifies samsa-related observers.
        """
        self._observers["sd"].update_sd()
        self._observers["sc"].update_sc()
        self._observers["display_samsa"].update_samsa_table()

    def notify_te_observer(self):
        """
        Notifies tes-related observers.
        """
        self._observers["td"].update_td()
        self._observers["tc"].update_tc()
        self._observers["display_tes"].update_tes_table()

    def notify_ko_observer(self):
        """
        Notifies korttid-related observers.
        """
        self._observers["kd"].update_kd()
        self._observers["kc"].update_kc()
        self._observers["display_korttid"].update_korttid_table()

    def when_change_has_been_made_directly_on_samsa_table(self):
        """
        Updates observers when a direct change is made on the samsa dataframe.
        """
        self._observers["sd"].update_sd()
        self._observers["sc"].update_sc()

    def when_change_has_been_made_directly_on_tes_table(self):
        """
        Updates observers when a direct change is made on the tes dataframe.
        """
        self._observers["td"].update_td()
        self._observers["tc"].update_tc()

    def when_change_has_been_made_directly_on_korttid_table(self):
        """
        Updates observers when a direct change is made on the korttid dataframe.
        """
        self._observers["kd"].update_kd()
        self._observers["kc"].update_kc()

    @property
    def samsa_df(self):
        """
        Gets the samsa dataframe.

        :return: The samsa dataframe.
        """
        return self._samsa_df

    @samsa_df.setter
    def samsa_df(self, value):
        """
        Sets the samsa dataframe.

        :param value: The new value for the samsa dataframe.
        """
        self._samsa_df = value

    @property
    def tes_df(self):
        """
        Gets the tes dataframe.

        :return: The tes dataframe.
        """
        return self._tes_df

    @tes_df.setter
    def tes_df(self, value):
        """
        Sets the tes dataframe.

        :param value: The new value for the tes dataframe.
        """
        self._tes_df = value

    @property
    def korttid_df(self):
        """
        Gets the korttid dataframe.

        :return: The korttid dataframe.
        """
        return self._korttid_df

    @korttid_df.setter
    def korttid_df(self, value):
        """
        Sets the korttid dataframe.

        :param value: The new value for the korttid dataframe.
        """
        self._korttid_df = value

    def save_to_samsa_csv(self, skip_update=False):
        """
        Saves the samsa dataframe to a CSV file and notifies observers
        based on the value of skip_update.

        :param skip_update: Indicates whether to notify observers.
        """
        match skip_update:
            case False:
                self.samsa_df.to_csv("samsa.csv", index=False)
                self.notify_sa_observer()
            case True:
                self.samsa_df.to_csv("samsa.csv", index=False)
                self.when_change_has_been_made_directly_on_samsa_table()

    def save_to_tes_csv(self, skip_update=False):
        """
        Saves the tes dataframe to a CSV file and notifies observers
        based on the value of skip_update.

        :param skip_update: Indicates whether to notify observers.
        """
        match skip_update:
            case False:
                self.tes_df.to_csv("tes.csv", index=False)
                self.notify_te_observer()
            case True:
                self.tes_df.to_csv("tes.csv", index=False)
                self.when_change_has_been_made_directly_on_tes_table()

    def save_to_korttid_csv(self, skip_update=False):
        """
        Saves the korttid dataframe to a CSV file and notifies observers
        based on the value of skip_update.

        :param skip_update: Indicates whether to notify observers.
        """
        match skip_update:
            case False:
                self.korttid_df.to_csv("korttid.csv", index=False)
                self.notify_ko_observer()
            case True:
                self.korttid_df.to_csv("korttid.csv", index=False)
                self.when_change_has_been_made_directly_on_korttid_table()


data = Data()


class ADDPatient(QtWidgets.QWidget):
    """
    Provides a user interface to add a new patient,
    collecting their information and saving it to the appropriate dataframe.
    """

    def __init__(self):
        """
        Initializes the ADDPatient widget, sets up the layout, and runs the initial setup.
        """
        super().__init__()
        self.data = data

        self.layout = QtWidgets.QVBoxLayout()
        self.container_layout = QtWidgets.QVBoxLayout()

        self.container = QtWidgets.QGroupBox()
        self.personal_nr = QtWidgets.QLineEdit()
        self.first = QtWidgets.QLineEdit()
        self.last = QtWidgets.QLineEdit()
        self.area = QtWidgets.QComboBox()
        self.enrolled = QtWidgets.QComboBox()
        self.type_of_entry = QtWidgets.QComboBox()
        self.note = QtWidgets.QTextEdit()
        self.button = QtWidgets.QPushButton("Skicka")

        self.run()

    def apply_settings_to_container(self):
        """
        Applies specific settings to the container.
        """
        self.container.setFixedWidth(settings["fixed_width_container"])

    def connect_button(self):
        """
        Connects the submit button to its click event handler.
        """
        self.button.clicked.connect(lambda: self.button_clicked((
            self.personal_nr.text(),
            self.first.text() if self.first.text() != "" else "-",
            self.last.text() if self.last.text() != "" else "-",
            self.area.currentText(),
            self.enrolled.currentText(),
            self.type_of_entry.currentText(),
            self.note.toPlainText() if self.note.toPlainText() != "" else "-"
        )))

    def populate_combos(self):
        """
        Populates the comboboxes with predefined values.
        """
        self.area.addItems(["Centrum", "Norrmalm", "Österlånggatan 4", "Margaretagatan 9"])
        self.enrolled.addItems(["Ja", "Nej"])
        self.type_of_entry.addItems(["SAMSA", "TES", "KORTTID"])

    def add_widgets_to_container_layout(self):
        """
        Adds the input widgets to the container layout.
        """
        self.container_layout.addWidget(QtWidgets.QLabel("Personnummer"))
        self.container_layout.addWidget(self.personal_nr)
        self.container_layout.addWidget(QtWidgets.QLabel("Förnamn"))
        self.container_layout.addWidget(self.first)
        self.container_layout.addWidget(QtWidgets.QLabel("Efternamn"))
        self.container_layout.addWidget(self.last)
        self.container_layout.addWidget(QtWidgets.QLabel("Område"))
        self.container_layout.addWidget(self.area)
        self.container_layout.addWidget(QtWidgets.QLabel("Inskriven"))
        self.container_layout.addWidget(self.enrolled)
        self.container_layout.addWidget(QtWidgets.QLabel("Typ"))
        self.container_layout.addWidget(self.type_of_entry)
        self.container_layout.addWidget(QtWidgets.QLabel("Anteckning"))
        self.container_layout.addWidget(self.note)
        self.container_layout.addWidget(self.button)

    def add_container_to_layout(self):
        """
        Adds the container to the main layout.
        """
        self.layout.addWidget(self.container, alignment=QtCore.Qt.AlignCenter)
        self.layout.addStretch()

    def reset_inputs(self):
        """
        Resets all inputs to their default values.
        """
        self.personal_nr.clear()
        self.first.clear()
        self.last.clear()
        self.area.setCurrentIndex(0)
        self.enrolled.setCurrentIndex(0)
        self.type_of_entry.setCurrentIndex(0)
        self.note.clear()

    @staticmethod
    def check_format_personal_nr(input_string):
        """
        Checks the format of the personal number string.

        :param input_string: The input string to check.
        :return: True if the format matches, False otherwise.
        """
        pattern = r'^\d{6}-\d{4}$'
        return bool(re.match(pattern, input_string))

    @QtCore.Slot()
    def button_clicked(self, values):
        """
        Handles the submit button click event, updates the relevant dataframe
        based on the type of entry, and saves it to a CSV file.

        :param values: A tuple containing the values from the input fields.
        """
        header = ["Personnummer", "Förnamn", "Efternamn", "Område", "Inskriven", "Typ", "Anteckning"]
        values_dict = {header[i]: values[i] for i in range(7)}

        if self.check_format_personal_nr(values_dict["Personnummer"]):
            match values_dict["Typ"]:
                case "SAMSA":
                    try:
                        self.data.samsa_df = pd.read_csv("samsa.csv")
                        length_samsa_df = self.data.samsa_df.shape[0]
                        new_row = pd.DataFrame(values_dict, index=[length_samsa_df])
                        updated_samsa_df = pd.concat([self.data.samsa_df, new_row], axis=0)
                        self.data.samsa_df = updated_samsa_df
                        self.data.save_to_samsa_csv()

                    except pd.errors.EmptyDataError:
                        new_row = pd.DataFrame(values_dict, index=[0])
                        self.data.samsa_df = new_row
                        self.data.save_to_samsa_csv()

                case "TES":
                    try:
                        self.data.tes_df = pd.read_csv("tes.csv")
                        length_tes_df = self.data.tes_df.shape[0]
                        new_row = pd.DataFrame(values_dict, index=[length_tes_df])
                        updated_tes_df = pd.concat([self.data.tes_df, new_row], axis=0)
                        self.data.tes_df = updated_tes_df
                        self.data.save_to_tes_csv()

                    except pd.errors.EmptyDataError:
                        new_row = pd.DataFrame(values_dict, index=[0])
                        self.data.tes_df = new_row
                        self.data.save_to_tes_csv()

                case "KORTTID":
                    try:
                        self.data.korttid_df = pd.read_csv("korttid.csv")
                        length_korttid_df = self.data.korttid_df.shape[0]
                        new_row = pd.DataFrame(values_dict, index=[length_korttid_df])
                        updated_korttid_df = pd.concat([self.data.korttid_df, new_row], axis=0)
                        self.data.korttid_df = updated_korttid_df
                        self.data.save_to_korttid_csv()

                    except pd.errors.EmptyDataError:
                        new_row = pd.DataFrame(values_dict, index=[0])
                        self.data.korttid_df = new_row
                        self.data.save_to_korttid_csv()

            self.reset_inputs()
        else:
            pass

    def run(self):
        """
        Runs the initial setup for the widget, applying settings,
        connecting signals, populating comboboxes, and adding widgets to the layout.
        """
        self.apply_settings_to_container()
        self.setLayout(self.layout)
        self.container.setLayout(self.container_layout)
        self.connect_button()
        self.populate_combos()
        self.add_widgets_to_container_layout()
        self.add_container_to_layout()


class DeletePatient(QtWidgets.QWidget):
    """
    Provides a user interface to delete patients from the SAMSA, TES, and KORTTID dataframes.
    """

    def __init__(self):
        """
        Initializes the DeletePatient widget, sets up the layout,
        registers the widget as an observer, and runs the initial setup.
        """
        super().__init__()
        self.data = data
        self.data.register_observer(self, "sd")
        self.data.register_observer(self, "td")
        self.data.register_observer(self, "kd")

        self.layout = QtWidgets.QVBoxLayout()
        self.main_container_layout = QtWidgets.QHBoxLayout()
        self.container1_layout = QtWidgets.QVBoxLayout()
        self.container2_layout = QtWidgets.QVBoxLayout()
        self.container3_layout = QtWidgets.QVBoxLayout()

        self.main_container = QtWidgets.QGroupBox()
        self.container1 = QtWidgets.QGroupBox()
        self.container2 = QtWidgets.QGroupBox()
        self.container3 = QtWidgets.QGroupBox()

        self.patient_samsa = QtWidgets.QComboBox()
        self.button_samsa = QtWidgets.QPushButton("Radera")

        self.patient_tes = QtWidgets.QComboBox()
        self.button_tes = QtWidgets.QPushButton("Radera")

        self.patient_korttid = QtWidgets.QComboBox()
        self.button_korttid = QtWidgets.QPushButton("Radera")

        self.run()

    def populate_combos(self):
        """
        Populates the comboboxes with patient data from SAMSA, TES, and KORTTID dataframes.
        """
        try:
            self.data.samsa_df = pd.read_csv("samsa.csv")
            self.data.tes_df = pd.read_csv("tes.csv")
            self.data.korttid_df = pd.read_csv("korttid.csv")

            self.patient_samsa.addItems([f"{p[1]} {p[2]} {p[3]}" for p in self.data.samsa_df.itertuples()])
            self.patient_tes.addItems([f"{p[1]} {p[2]} {p[3]}" for p in self.data.tes_df.itertuples()])
            self.patient_korttid.addItems([f"{p[1]} {p[2]} {p[3]}" for p in self.data.korttid_df.itertuples()])

        except pd.errors.EmptyDataError:
            pass

    def connect_buttons(self):
        """
        Connects the delete buttons to their click event handlers.
        """
        self.button_samsa.clicked.connect(lambda: self.button_clicked(self.patient_samsa.currentText(), "s"))
        self.button_tes.clicked.connect(lambda: self.button_clicked(self.patient_tes.currentText(), "t"))
        self.button_korttid.clicked.connect(lambda: self.button_clicked(self.patient_korttid.currentText(), "k"))

    def add_widgets_to_container_layout(self):
        """
        Adds the comboboxes and buttons to their respective container layouts.
        """
        self.container1_layout.addWidget(QtWidgets.QLabel("SAMSA"))
        self.container1_layout.addWidget(self.patient_samsa)
        self.container1_layout.addWidget(self.button_samsa)
        self.container2_layout.addWidget(QtWidgets.QLabel("TES"))
        self.container2_layout.addWidget(self.patient_tes)
        self.container2_layout.addWidget(self.button_tes)
        self.container3_layout.addWidget(QtWidgets.QLabel("KORTTID"))
        self.container3_layout.addWidget(self.patient_korttid)
        self.container3_layout.addWidget(self.button_korttid)

    def add_containers_to_layouts(self):
        """
        Adds the containers to the main layout.
        """
        self.main_container_layout.addWidget(self.container1)
        self.main_container_layout.addWidget(self.container2)
        self.main_container_layout.addWidget(self.container3)
        self.layout.addWidget(self.main_container, alignment=QtCore.Qt.AlignCenter)
        self.layout.addStretch()

    def run(self):
        """
        Runs the initial setup for the widget, setting the layout,
        populating comboboxes, connecting buttons, and adding widgets to the layout.
        """
        self.setLayout(self.layout)
        self.main_container.setLayout(self.main_container_layout)
        self.main_container.setFixedWidth(settings["fixed_width_container"])
        self.container1.setLayout(self.container1_layout)
        self.container2.setLayout(self.container2_layout)
        self.container3.setLayout(self.container3_layout)

        self.populate_combos()
        self.connect_buttons()
        self.add_widgets_to_container_layout()
        self.add_containers_to_layouts()

    def update_sd(self):
        """
        Updates the SAMSA combobox with the latest data.
        """
        self.data.samsa_df = pd.read_csv("samsa.csv")
        self.patient_samsa.clear()
        self.patient_samsa.addItems([f"{p[1]} {p[2]} {p[3]}" for p in self.data.samsa_df.itertuples()])

    def update_td(self):
        """
        Updates the TES combobox with the latest data.
        """
        self.data.tes_df = pd.read_csv("tes.csv")
        self.patient_tes.clear()
        self.patient_tes.addItems([f"{p[1]} {p[2]} {p[3]}" for p in self.data.tes_df.itertuples()])

    def update_kd(self):
        """
        Updates the KORTTID combobox with the latest data.
        """
        self.data.korttid_df = pd.read_csv("korttid.csv")
        self.patient_korttid.clear()
        self.patient_korttid.addItems([f"{p[1]} {p[2]} {p[3]}" for p in self.data.korttid_df.itertuples()])

    @QtCore.Slot()
    def button_clicked(self, text, flag):
        """
        Handles the delete button click event, removes the selected
        patient from the relevant dataframe, and saves the dataframe to a CSV file.

        :param text: The text from the combobox indicating the patient to delete.
        :param flag: A flag indicating which dataframe to update ("s" for SAMSA, "t" for TES, "k" for KORTTID).
        """
        personal_nr = text.split(sep=" ")[0]
        match flag:
            case "s":
                try:
                    row_to_drop = self.data.samsa_df[self.data.samsa_df["Personnummer"] == personal_nr].index.item()
                    self.data.samsa_df = self.data.samsa_df.drop(row_to_drop, axis="index")
                    self.data.save_to_samsa_csv()
                except ValueError:
                    pass
            case "t":
                try:
                    row_to_drop = self.data.tes_df[self.data.tes_df["Personnummer"] == personal_nr].index.item()
                    self.data.tes_df = self.data.tes_df.drop(row_to_drop, axis="index")
                    self.data.save_to_tes_csv()
                except ValueError:
                    pass
            case "k":
                try:
                    row_to_drop = self.data.korttid_df[
                        self.data.korttid_df["Personnummer"] == personal_nr].index.item()
                    self.data.korttid_df = self.data.korttid_df.drop(row_to_drop, axis="index")
                    self.data.save_to_korttid_csv()
                except ValueError:
                    pass


class UpdateSamsa(QtWidgets.QWidget):
    """
    Provides a user interface to delete discharged patients from the SAMSA dataframe.
    """

    def __init__(self):
        """
        Initializes the UpdateSamsa widget, sets up the layout, and runs the initial setup.
        """
        super().__init__()
        self.data = data
        self.layout = QtWidgets.QVBoxLayout()
        self.container_layout = QtWidgets.QVBoxLayout()
        self.container = QtWidgets.QGroupBox()
        self.textbox = QtWidgets.QTextEdit()
        self.button = QtWidgets.QPushButton("Uppdatera")
        self.run()

    def apply_settings_to_container(self):
        """
        Applies specific settings to the container.
        """
        self.container.setFixedWidth(settings["fixed_width_container"])

    def connect_button(self):
        """
        Connects the submit button to its click event handler.
        """
        self.button.clicked.connect(lambda: self.button_clicked(self.textbox.toPlainText()))

    def add_widgets_to_container_layout(self):
        """
        Adds the input textbox and button to the container layout.
        """
        self.container_layout.addWidget(self.textbox)
        self.container_layout.addWidget(self.button)

    def add_container_to_layout(self):
        """
        Adds the container to the main layout.
        """
        self.layout.addWidget(self.container, alignment=QtCore.Qt.AlignCenter)
        self.layout.addStretch()

    def run(self):
        """
        Runs the initial setup for the widget, applying settings,
        connecting signals, and adding widgets to the layout.
        """
        self.apply_settings_to_container()
        self.setLayout(self.layout)
        self.container.setLayout(self.container_layout)
        self.connect_button()
        self.add_widgets_to_container_layout()
        self.add_container_to_layout()

    @QtCore.Slot()
    def button_clicked(self, values):
        """
        Handles the submit button click event, processes the input values,
        updates the SAMSA dataframe, and provides feedback on the changes.

        :param values: A comma-separated string of personal numbers to be processed.
        """
        values = values.replace(" ", "").split(sep=",")
        pattern = r'^\d{6}-\d{4}$'

        is_correct_format = all([re.match(pattern, item) for item in values])

        if is_correct_format:
            # Removes discharged patients from the dataframe
            list_of_personal_numbers = self.data.samsa_df["Personnummer"].tolist()
            discharged = set(list_of_personal_numbers).difference(set(values))
            indexes = [i for i in self.data.samsa_df.index if self.data.samsa_df.at[i, "Personnummer"] in discharged]

            self.data.samsa_df = self.data.samsa_df.drop(indexes).reset_index(drop=True)
            self.data.save_to_samsa_csv()

            # Adds new patients to the dataframe
            new = set(values).difference(set(list_of_personal_numbers))
            self.data.samsa_df = pd.read_csv("samsa.csv")
            columns = [column for column in self.data.samsa_df.columns]

            for item in new:
                new_entry = pd.DataFrame(data=[[item, "-", "-", "-", "-", "-", "-"]], columns=columns)
                self.data.samsa_df = pd.concat([self.data.samsa_df, new_entry], axis=0)

            self.data.save_to_samsa_csv()
            self.textbox.clear()

            # Provides feedback on the changes
            deleted = list(discharged)
            added = list(new)
            self.textbox.setPlainText(f"Removed: {deleted}\nAdded: {added}".replace("'", ""))

        else:  # If the format is incorrect, do nothing.
            pass


class UpdateNote(QtWidgets.QWidget):
    """
    Provides a user interface to update notes for patients in the SAMSA, TES, and KORTTID dataframes.
    """

    def __init__(self):
        """
        Initializes the UpdateNote widget, sets up the layout, registers the widget as an observer,
        and runs the initial setup.
        """
        super().__init__()
        self.data = data
        self.data.register_observer(self, "sc")
        self.data.register_observer(self, "tc")
        self.data.register_observer(self, "kc")

        self.layout = QtWidgets.QVBoxLayout()
        self.main_container_layout = QtWidgets.QHBoxLayout()
        self.container1_layout = QtWidgets.QVBoxLayout()
        self.container2_layout = QtWidgets.QVBoxLayout()
        self.container3_layout = QtWidgets.QVBoxLayout()

        self.main_container = QtWidgets.QGroupBox()
        self.main_container.setFixedWidth(settings["fixed_width_container"])
        self.container1 = QtWidgets.QGroupBox("SAMSA")
        self.container2 = QtWidgets.QGroupBox("TES")
        self.container3 = QtWidgets.QGroupBox("KORTTID")

        self.patient1 = QtWidgets.QComboBox()
        self.patient2 = QtWidgets.QComboBox()
        self.patient3 = QtWidgets.QComboBox()

        self.note1 = QtWidgets.QTextEdit()
        self.note2 = QtWidgets.QTextEdit()
        self.note3 = QtWidgets.QTextEdit()

        self.button1 = QtWidgets.QPushButton("Uppdatera")
        self.button2 = QtWidgets.QPushButton("Uppdatera")
        self.button3 = QtWidgets.QPushButton("Uppdatera")

        self.run()

    def add_items_to_combos(self):
        """
        Adds patient items to the comboboxes from the SAMSA, TES, and KORTTID dataframes.
        """
        self.data.samsa_df = pd.read_csv("samsa.csv")
        self.data.tes_df = pd.read_csv("tes.csv")
        self.data.korttid_df = pd.read_csv("korttid.csv")

        self.patient1.addItems([f"{p[1]} {p[2]} {p[3]}" for p in self.data.samsa_df.itertuples()])
        self.patient2.addItems([f"{p[1]} {p[2]} {p[3]}" for p in self.data.tes_df.itertuples()])
        self.patient3.addItems([f"{p[1]} {p[2]} {p[3]}" for p in self.data.korttid_df.itertuples()])

    def set_default_values(self):
        """
        Sets default values for the notes fields based on the currently selected patient.
        """
        try:
            active_samsa_personal_nr = self.patient1.currentText()[0:11]
            active_samsa = self.data.samsa_df[self.data.samsa_df["Personnummer"] == active_samsa_personal_nr]
            default_value_note_samsa = active_samsa.at[0, "Anteckning"]
            self.note1.setPlainText(default_value_note_samsa) if isinstance(default_value_note_samsa, str) else "-"

            active_tes_personal_nr = self.patient2.currentText()[0:11]
            active_tes = self.data.tes_df[self.data.tes_df["Personnummer"] == active_tes_personal_nr]
            default_value_note_tes = active_tes.at[0, "Anteckning"]
            self.note2.setPlainText(default_value_note_tes) if isinstance(default_value_note_tes, str) else "-"

            active_korttid_personal_nr = self.patient3.currentText()[0:11]
            active_korttid = self.data.korttid_df[self.data.korttid_df["Personnummer"] == active_korttid_personal_nr]
            default_value_note_korttid = active_korttid.at[0, "Anteckning"]
            self.note3.setPlainText(default_value_note_korttid) if isinstance(default_value_note_korttid, str) else "-"
        except KeyError:
            pass

    def connect_buttons(self):
        """
        Connects the update buttons to their click event handlers.
        """
        samsa_flag = "sa"
        tes_flag = "te"
        korttid_flag = "ko"

        self.button1.clicked.connect(lambda: self.button_clicked(
            (self.patient1.currentText(), self.note1.toPlainText()), samsa_flag))

        self.button2.clicked.connect(lambda: self.button_clicked(
            (self.patient2.currentText(), self.note2.toPlainText()), tes_flag))

        self.button3.clicked.connect(lambda: self.button_clicked(
            (self.patient3.currentText(), self.note3.toPlainText()), korttid_flag))

    def connect_patient_combo_items(self):
        """
        Connects the patient comboboxes to their index changed event handlers.
        """
        self.patient1.currentIndexChanged.connect(lambda: self.current_index_changed(self.patient1.currentText(), 0))
        self.patient2.currentIndexChanged.connect(lambda: self.current_index_changed(self.patient2.currentText(), 1))
        self.patient3.currentIndexChanged.connect(lambda: self.current_index_changed(self.patient3.currentText(), 2))

    def add_widgets_to_container_layouts(self):
        """
        Adds the comboboxes, notes fields, and buttons to their respective container layouts.
        """
        self.container1_layout.addWidget(QtWidgets.QLabel("Patient"))
        self.container1_layout.addWidget(self.patient1)
        self.container2_layout.addWidget(QtWidgets.QLabel("Patient"))
        self.container2_layout.addWidget(self.patient2)
        self.container3_layout.addWidget(QtWidgets.QLabel("Patient"))
        self.container3_layout.addWidget(self.patient3)

        self.container1_layout.addWidget(QtWidgets.QLabel("Anteckning"))
        self.container1_layout.addWidget(self.note1)
        self.container2_layout.addWidget(QtWidgets.QLabel("Anteckning"))
        self.container2_layout.addWidget(self.note2)
        self.container3_layout.addWidget(QtWidgets.QLabel("Anteckning"))
        self.container3_layout.addWidget(self.note3)

        self.container1_layout.addWidget(self.button1)
        self.container2_layout.addWidget(self.button2)
        self.container3_layout.addWidget(self.button3)

    def add_containers_to_layouts(self):
        """
        Adds the containers to the main layout.
        """
        self.main_container_layout.addWidget(self.container1)
        self.main_container_layout.addWidget(self.container2)
        self.main_container_layout.addWidget(self.container3)
        self.layout.addWidget(self.main_container, alignment=QtCore.Qt.AlignCenter)
        self.layout.addStretch()

    def run(self):
        """
        Runs the initial setup for the widget, setting the layout,
        populating comboboxes, connecting buttons and signals, and adding widgets to the layout.
        """
        self.setLayout(self.layout)
        self.main_container.setLayout(self.main_container_layout)
        self.container1.setLayout(self.container1_layout)
        self.container2.setLayout(self.container2_layout)
        self.container3.setLayout(self.container3_layout)
        self.add_items_to_combos()
        self.set_default_values()
        self.connect_buttons()
        self.connect_patient_combo_items()
        self.add_widgets_to_container_layouts()
        self.add_containers_to_layouts()

    def update_sc(self):
        """
        Updates the SAMSA combobox with the latest data.
        """
        self.patient1.currentIndexChanged.disconnect()
        self.data.samsa_df = pd.read_csv("samsa.csv")
        self.patient1.clear()
        self.patient1.addItems([f"{p[1]} {p[2]} {p[3]}" for p in self.data.samsa_df.itertuples()])

        personal_nr = self.patient1.currentText()[0:11]
        record = self.data.samsa_df[self.data.samsa_df["Personnummer"] == personal_nr]
        value = record["Anteckning"].item()
        self.note1.setPlainText(value)

        self.patient1.currentIndexChanged.connect(lambda: self.current_index_changed(self.patient1.currentText(), 0))

    def update_tc(self):
        """
        Updates the TES combobox with the latest data.
        """
        self.patient2.currentIndexChanged.disconnect()
        self.data.tes_df = pd.read_csv("tes.csv")
        self.patient2.clear()
        self.patient2.addItems([f"{p[1]} {p[2]} {p[3]}" for p in self.data.tes_df.itertuples()])

        personal_nr = self.patient2.currentText()[0:11]
        record = self.data.tes_df[self.data.tes_df["Personnummer"] == personal_nr]
        value = record["Anteckning"].item()
        self.note2.setPlainText(value)

        self.patient2.currentIndexChanged.connect(lambda: self.current_index_changed(self.patient2.currentText(), 1))

    def update_kc(self):
        """
        Updates the KORTTID combobox with the latest data.
        """
        self.patient3.currentIndexChanged.disconnect()
        self.data.korttid_df = pd.read_csv("korttid.csv")
        self.patient3.clear()
        self.patient3.addItems([f"{p[1]} {p[2]} {p[3]}" for p in self.data.korttid_df.itertuples()])

        personal_nr = self.patient3.currentText()[0:11]
        record = self.data.korttid_df[self.data.korttid_df["Personnummer"] == personal_nr]
        value = record["Anteckning"].item()
        self.note3.setPlainText(value)

        self.patient3.currentIndexChanged.connect(lambda: self.current_index_changed(self.patient3.currentText(), 2))

    @QtCore.Slot()
    def current_index_changed(self, text, flag):
        """
        Handles the combobox index change event, updates the respective note field with the selected patient's note.

        :param text: The text from the combobox indicating the selected patient.
        :param flag: A flag indicating which note field to update (0 for SAMSA, 1 for TES, 2 for KORTTID).
        """
        personal_nr = text[:11]
        match flag:
            case 0:
                record = self.data.samsa_df[self.data.samsa_df["Personnummer"] == personal_nr]
                note = record.iloc[0]["Anteckning"]
                self.note1.setPlainText(note)

            case 1:
                record = self.data.tes_df[self.data.tes_df["Personnummer"] == personal_nr]
                note = record.iloc[0]["Anteckning"]
                self.note2.setPlainText(note)

            case 2:
                record = self.data.korttid_df[self.data.korttid_df["Personnummer"] == personal_nr]
                note = record.iloc[0]["Anteckning"]
                self.note3.setPlainText(note)

    @QtCore.Slot()
    def button_clicked(self, values, flag):
        """
        Handles the update button click event, updates the selected patient's note in the relevant dataframe,
        and saves the dataframe to a CSV file.

        :param values: A tuple containing the patient's identifier and the note text.
        :param flag: A flag indicating which dataframe to update ("sa" for SAMSA, "te" for TES, "ko" for KORTTID).
        """
        match flag:
            case "sa":
                try:
                    record = self.data.samsa_df[self.data.samsa_df["Personnummer"] == values[0][0:11]]
                    record_index = record.index.item()
                    self.data.samsa_df.at[record_index, "Anteckning"] = values[1] if values[1] != "" else "-"
                    self.data.save_to_samsa_csv()
                except ValueError:
                    pass

            case "te":
                try:
                    record = self.data.tes_df[self.data.tes_df["Personnummer"] == values[0][0:11]]
                    record_index = record.index.item()
                    self.data.tes_df.at[record_index, "Anteckning"] = values[1] if values[1] != "" else "-"
                    self.data.save_to_tes_csv()
                except ValueError:
                    pass

            case "ko":
                try:
                    record = self.data.korttid_df[self.data.korttid_df["Personnummer"] == values[0][0:11]]
                    record_index = record.index.item()
                    self.data.korttid_df.at[record_index, "Anteckning"] = values[1] if values[1] != "" else "-"
                    self.data.save_to_korttid_csv()
                except ValueError:
                    pass


class Manage(QtWidgets.QWidget):
    """
    Provides a user interface with multiple tabs to manage patients and update their information.
    """

    def __init__(self):
        """
        Initializes the Manage widget, sets up the layout, and adds the tabs.
        """
        super().__init__()
        self.layout = QtWidgets.QVBoxLayout()
        self.setLayout(self.layout)
        self.add_tabs()

    def add_tabs(self):
        """
        Adds tabs to the interface for adding, deleting, and updating patient information.
        """
        tabs = QtWidgets.QTabWidget()
        tabs.addTab(ADDPatient(), "Ny Patient")
        tabs.addTab(DeletePatient(), "Radera Patient")
        tabs.addTab(UpdateSamsa(), "Uppdatera SAMSA")
        tabs.addTab(UpdateNote(), "Uppdatera Anteckning")
        self.layout.addWidget(tabs)


class Display(QtWidgets.QWidget):
    """
    Provides a user interface to display and manage data tables for SAMSA, TES, and KORTTID datasets.
    """

    def __init__(self):
        """
        Initializes the Display widget, sets up the layout, registers as an observer for data updates,
        and creates the tables and buttons for each dataset.
        """
        super().__init__()
        self.data = data
        self.data.register_observer(self, "display_samsa")
        self.data.register_observer(self, "display_tes")
        self.data.register_observer(self, "display_korttid")

        self.layout = QtWidgets.QHBoxLayout()
        self.samsa_container_layout = QtWidgets.QVBoxLayout()
        self.tes_container_layout = QtWidgets.QVBoxLayout()
        self.korttid_container_layout = QtWidgets.QVBoxLayout()

        self.samsa_container = QtWidgets.QGroupBox()
        self.tes_container = QtWidgets.QGroupBox()
        self.korttid_container = QtWidgets.QGroupBox()

        self.samsa_table = self.create_table(self.data.samsa_df)
        self.tes_table = self.create_table(self.data.tes_df)
        self.korttid_table = self.create_table(self.data.korttid_df)
        self.samsa_conn = None
        self.tes_conn = None
        self.korttid_conn = None

        self.button_container_samsa = QtWidgets.QGroupBox()
        self.button_first_samsa = QtWidgets.QPushButton("Förnamn")
        self.button_last_samsa = QtWidgets.QPushButton("Efternamn")
        self.button_area_samsa = QtWidgets.QPushButton("Område")
        self.button_enrolled_samsa = QtWidgets.QPushButton("Inskriven")

        self.button_container_tes = QtWidgets.QGroupBox()
        self.button_first_tes = QtWidgets.QPushButton("Förnamn")
        self.button_last_tes = QtWidgets.QPushButton("Efternamn")
        self.button_area_tes = QtWidgets.QPushButton("Område")
        self.button_enrolled_tes = QtWidgets.QPushButton("Inskriven")

        self.button_container_korttid = QtWidgets.QGroupBox()
        self.button_first_korttid = QtWidgets.QPushButton("Förnamn")
        self.button_last_korttid = QtWidgets.QPushButton("Efternamn")
        self.button_area_korttid = QtWidgets.QPushButton("Område")
        self.button_enrolled_korttid = QtWidgets.QPushButton("Inskriven")

        self.run()

    def set_layouts(self):
        """
        Sets the layout for the main container and the individual group boxes.
        """
        self.setLayout(self.layout)
        self.samsa_container.setLayout(self.samsa_container_layout)
        self.tes_container.setLayout(self.tes_container_layout)
        self.korttid_container.setLayout(self.korttid_container_layout)
        self.button_container_samsa.setLayout(QtWidgets.QHBoxLayout())
        self.button_container_tes.setLayout(QtWidgets.QHBoxLayout())
        self.button_container_korttid.setLayout(QtWidgets.QHBoxLayout())

    def connect_tables(self):
        """
        Connects the cell change events for each table to their respective handlers.
        """
        self.samsa_conn = lambda row, column: self.cell_changed(row, column, self.samsa_table.item(row, column), "S")
        self.samsa_table.cellChanged.connect(self.samsa_conn)

        self.tes_conn = lambda row, column: self.cell_changed(row, column, self.tes_table.item(row, column), "T")
        self.tes_table.cellChanged.connect(self.tes_conn)

        self.korttid_conn = lambda row, column: self.cell_changed(row, column, self.korttid_table.item(row, column),
                                                                  "K")
        self.korttid_table.cellChanged.connect(self.korttid_conn)

    def connect_buttons(self):
        """
        Connects the sorting buttons for each dataset to their respective handlers.
        """
        self.button_first_samsa.clicked.connect(lambda: self.button_clicked("S", "first"))
        self.button_last_samsa.clicked.connect(lambda: self.button_clicked("S", "last"))
        self.button_area_samsa.clicked.connect(lambda: self.button_clicked("S", "area"))
        self.button_enrolled_samsa.clicked.connect(lambda: self.button_clicked("S", "enrolled"))

        self.button_first_tes.clicked.connect(lambda: self.button_clicked("T", "first"))
        self.button_last_tes.clicked.connect(lambda: self.button_clicked("T", "last"))
        self.button_area_tes.clicked.connect(lambda: self.button_clicked("T", "area"))
        self.button_enrolled_tes.clicked.connect(lambda: self.button_clicked("T", "enrolled"))

        self.button_first_korttid.clicked.connect(lambda: self.button_clicked("K", "first"))
        self.button_last_korttid.clicked.connect(lambda: self.button_clicked("K", "last"))
        self.button_area_korttid.clicked.connect(lambda: self.button_clicked("K", "area"))
        self.button_enrolled_korttid.clicked.connect(lambda: self.button_clicked("K", "enrolled"))

    def add_widgets(self):
        """
        Adds the tables and buttons to their respective containers and layouts.
        """
        self.button_container_samsa.layout().addWidget(self.button_first_samsa)
        self.button_container_samsa.layout().addWidget(self.button_last_samsa)
        self.button_container_samsa.layout().addWidget(self.button_area_samsa)
        self.button_container_samsa.layout().addWidget(self.button_enrolled_samsa)
        self.samsa_container_layout.addWidget(QtWidgets.QLabel("SAMSA"), alignment=QtCore.Qt.AlignCenter)
        samsa_scroll_area = QtWidgets.QScrollArea()
        samsa_scroll_area.setWidgetResizable(True)
        samsa_scroll_area.setWidget(self.samsa_table)
        self.samsa_container_layout.addWidget(samsa_scroll_area)
        self.samsa_container_layout.addWidget(self.button_container_samsa)

        self.button_container_tes.layout().addWidget(self.button_first_tes)
        self.button_container_tes.layout().addWidget(self.button_last_tes)
        self.button_container_tes.layout().addWidget(self.button_area_tes)
        self.button_container_tes.layout().addWidget(self.button_enrolled_tes)
        self.tes_container_layout.addWidget(QtWidgets.QLabel("TES"), alignment=QtCore.Qt.AlignCenter)
        tes_scroll_area = QtWidgets.QScrollArea()
        tes_scroll_area.setWidgetResizable(True)
        tes_scroll_area.setWidget(self.tes_table)
        self.tes_container_layout.addWidget(tes_scroll_area)
        self.tes_container_layout.addWidget(self.button_container_tes)

        self.button_container_korttid.layout().addWidget(self.button_first_korttid)
        self.button_container_korttid.layout().addWidget(self.button_last_korttid)
        self.button_container_korttid.layout().addWidget(self.button_area_korttid)
        self.button_container_korttid.layout().addWidget(self.button_enrolled_korttid)
        self.korttid_container_layout.addWidget(QtWidgets.QLabel("KORTTID"), alignment=QtCore.Qt.AlignCenter)
        korttid_scroll_area = QtWidgets.QScrollArea()
        korttid_scroll_area.setWidgetResizable(True)
        korttid_scroll_area.setWidget(self.korttid_table)
        self.korttid_container_layout.addWidget(korttid_scroll_area)
        self.korttid_container_layout.addWidget(self.button_container_korttid)

        self.layout.addWidget(self.samsa_container)
        self.layout.addWidget(self.tes_container)
        self.layout.addWidget(self.korttid_container)

    @staticmethod
    def create_table(df):
        """
        Creates a QTableWidget from a given DataFrame.

        :param df: The DataFrame containing the data to be displayed in the table.
        :return: A QTableWidget populated with the DataFrame data.
        """
        table = QtWidgets.QTableWidget()
        table.setRowCount(df.shape[0])
        table.setColumnCount(df.shape[1])
        table.setHorizontalHeaderLabels(df.columns)
        table.hideColumn(5)
        table.verticalHeader().setVisible(False)
        header = table.horizontalHeader()

        for i in range(df.shape[1]):
            header.setSectionResizeMode(i, QtWidgets.QHeaderView.ResizeToContents)

        for i in range(df.shape[0]):
            for j in range(df.shape[1]):
                item = QtWidgets.QTableWidgetItem(str(df.iloc[i, j]))
                item.setToolTip(str(df.iloc[i, j]))
                table.setItem(i, j, item)

        table.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOn)
        table.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOn)

        table.resizeColumnsToContents()
        table.viewport().update()

        return table

    def update_samsa_table(self):
        """
        Updates the SAMSA table with the latest data.
        """
        self.samsa_table.setRowCount(0)
        self.data.samsa_df = pd.read_csv("samsa.csv")
        self.samsa_table.setRowCount(self.data.samsa_df.shape[0])

        for i in range(self.data.samsa_df.shape[0]):
            for j in range(self.data.samsa_df.shape[1]):
                item = QtWidgets.QTableWidgetItem(str(self.data.samsa_df.iloc[i, j]))
                item.setToolTip(str(self.data.samsa_df.iloc[i, j]))
                self.samsa_table.setItem(i, j, item)

    def update_tes_table(self):
        """
        Updates the TES table with the latest data.
        """
        self.tes_table.setRowCount(0)
        self.data.tes_df = pd.read_csv("tes.csv")
        self.tes_table.setRowCount(self.data.tes_df.shape[0])

        for i in range(self.data.tes_df.shape[0]):
            for j in range(self.data.tes_df.shape[1]):
                item = QtWidgets.QTableWidgetItem(str(self.data.tes_df.iloc[i, j]))
                item.setToolTip(str(self.data.tes_df.iloc[i, j]))
                self.tes_table.setItem(i, j, item)

    def update_korttid_table(self):
        """
        Updates the KORTTID table with the latest data.
        """
        self.korttid_table.setRowCount(0)
        self.data.korttid_df = pd.read_csv("korttid.csv")
        self.korttid_table.setRowCount(self.data.korttid_df.shape[0])

        for i in range(self.data.korttid_df.shape[0]):
            for j in range(self.data.korttid_df.shape[1]):
                item = QtWidgets.QTableWidgetItem(str(self.data.korttid_df.iloc[i, j]))
                item.setToolTip(str(self.data.korttid_df.iloc[i, j]))
                self.korttid_table.setItem(i, j, item)

    @staticmethod
    def repopulate_table(df, table):
        """
        Repopulates a QTableWidget with data from a DataFrame.

        :param df: The DataFrame containing the new data.
        :param table: The QTableWidget to be repopulated.
        """
        for i in range(df.shape[0]):
            for j in range(df.shape[1]):
                item = QtWidgets.QTableWidgetItem(str(df.iloc[i, j]))
                item.setToolTip(str(df.iloc[i, j]))
                table.setItem(i, j, item)

    @QtCore.Slot()
    def button_clicked(self, flag1, flag2):
        """
        Handles the sorting button click event, sorts the respective dataset,
        and updates the corresponding table.

        :param flag1: A flag indicating which dataset to sort ("S" for SAMSA, "T" for TES, "K" for KORTTID).
        :param flag2: A flag indicating which column to sort by ("first", "last", "area", "enrolled").
        """
        match flag1:
            case "S":
                self.samsa_table.cellChanged.disconnect(self.samsa_conn)
                self.samsa_table.setRowCount(0)
                self.samsa_table.setRowCount(self.data.samsa_df.shape[0])
                match flag2:
                    case "first":
                        self.data.samsa_df = pd.read_csv("samsa.csv").sort_values("Förnamn")
                        self.repopulate_table(self.data.samsa_df, self.samsa_table)
                    case "last":
                        self.data.samsa_df = pd.read_csv("samsa.csv").sort_values("Efternamn")
                        self.repopulate_table(self.data.samsa_df, self.samsa_table)
                    case "area":
                        self.data.samsa_df = pd.read_csv("samsa.csv").sort_values("Område")
                        self.repopulate_table(self.data.samsa_df, self.samsa_table)
                    case "enrolled":
                        self.data.samsa_df = pd.read_csv("samsa.csv").sort_values(["Inskriven", "Område"])
                        self.repopulate_table(self.data.samsa_df, self.samsa_table)

                self.samsa_table.cellChanged.connect(self.samsa_conn)

            case "T":
                self.tes_table.cellChanged.disconnect(self.tes_conn)
                self.tes_table.setRowCount(0)
                self.tes_table.setRowCount(self.data.tes_df.shape[0])
                match flag2:
                    case "first":
                        self.data.tes_df = pd.read_csv("tes.csv").sort_values("Förnamn")
                        self.repopulate_table(self.data.tes_df, self.tes_table)
                    case "last":
                        self.data.tes_df = pd.read_csv("tes.csv").sort_values("Efternamn")
                        self.repopulate_table(self.data.tes_df, self.tes_table)
                    case "area":
                        self.data.tes_df = pd.read_csv("tes.csv").sort_values("Område")
                        self.repopulate_table(self.data.tes_df, self.tes_table)
                    case "enrolled":
                        self.data.tes_df = pd.read_csv("tes.csv").sort_values(["Inskriven", "Område"])
                        self.repopulate_table(self.data.tes_df, self.tes_table)

                self.tes_table.cellChanged.connect(self.tes_conn)

            case "K":
                self.korttid_table.cellChanged.disconnect(self.korttid_conn)
                self.korttid_table.setRowCount(0)
                self.korttid_table.setRowCount(self.data.korttid_df.shape[0])
                match flag2:
                    case "first":
                        self.data.korttid_df = pd.read_csv("korttid.csv").sort_values("Förnamn")
                        self.repopulate_table(self.data.korttid_df, self.korttid_table)
                    case "last":
                        self.data.korttid_df = pd.read_csv("korttid.csv").sort_values("Efternamn")
                        self.repopulate_table(self.data.korttid_df, self.korttid_table)
                    case "area":
                        self.data.korttid_df = pd.read_csv("korttid.csv").sort_values("Område")
                        self.repopulate_table(self.data.korttid_df, self.korttid_table)
                    case "enrolled":
                        self.data.korttid_df = pd.read_csv("korttid.csv").sort_values(["Inskriven", "Område"])
                        self.repopulate_table(self.data.korttid_df, self.korttid_table)

                self.korttid_table.cellChanged.connect(self.korttid_conn)

    @staticmethod
    def check_format_personal_nr(input_string):
        """
        Checks if the provided personal number string matches the required format.

        :param input_string: The personal number string to be checked.
        :return: True if the format matches, False otherwise.
        """
        pattern = r'^\d{6}-\d{4}$'
        return bool(re.match(pattern, input_string))

    def check_if_valid(self, column, item):
        """
        Checks if the provided table item is valid based on the column it's in.

        :param column: The column index of the item.
        :param item: The QTableWidgetItem to be checked.
        :return: True if the item is valid, False otherwise.
        """
        match column:
            case 0:
                return self.check_format_personal_nr(item.text())
            case 3:
                return item.text() in ("Centrum", "Norrmalm", "Österlånggatan 4", "Margaretagatan 9")
            case 4:
                return item.text() in ("Ja", "Nej")
            case 1 | 2 | 6:
                return item.text() != ""

    @QtCore.Slot()
    def cell_changed(self, row, column, item, t):
        """
        Handles the cell change event, checks the validity of the new value,
        and updates the corresponding dataset and CSV file if valid.

        :param row: The row index of the changed cell.
        :param column: The column index of the changed cell.
        :param item: The QTableWidgetItem containing the new value.
        :param t: A flag indicating which dataset to update ("S" for SAMSA, "T" for TES, "K" for KORTTID).
        """
        if not self.check_if_valid(column, item):
            return

        match t:
            case "S":
                df = self.data.samsa_df.copy()
                df.iat[row, column] = item.text()
                self.data.samsa_df = df
                self.data.save_to_samsa_csv(skip_update=True)
            case "T":
                df = self.data.tes_df.copy()
                df.iat[row, column] = item.text()
                self.data.tes_df = df
                self.data.save_to_tes_csv(skip_update=True)
            case "K":
                df = self.data.korttid_df.copy()
                df.iat[row, column] = item.text()
                self.data.korttid_df = df
                self.data.save_to_korttid_csv(skip_update=True)

    def run(self):
        """
        Runs the initial setup for the Display widget, setting layouts, connecting tables and buttons,
        and adding widgets to the interface.
        """
        self.set_layouts()
        self.connect_tables()
        self.connect_buttons()
        self.add_widgets()


class Window(QtWidgets.QMainWindow):
    """
    Represents the main window of the application, with navigation, settings, and pages for the SAMSA, TES, and KORTTID datasets.
    """

    def __init__(self):
        """
        Initializes the main window, creates necessary files, sets up the UI elements, and connects actions.
        """
        super().__init__()
        # Create files
        self.create_files()

        # Apply settings to window
        self.setWindowFlags(QtCore.Qt.FramelessWindowHint)
        self.setGeometry(settings["x"], settings["y"], settings["w"], settings["h"])

        # Set central widget
        self.central_widget = QtWidgets.QStackedWidget()
        self.setCentralWidget(self.central_widget)

        # Create navigation menu
        menubar = self.menuBar()
        pages_menu = menubar.addMenu("Sidor")
        actions_menu = menubar.addMenu("Handlingar")
        self.manage = pages_menu.addAction("Hantera")
        self.overview = pages_menu.addAction("Översikt")
        self.f = actions_menu.addAction("Fullscreen läge")
        self.l = actions_menu.addAction("Lämna fullscreen")
        self.t = actions_menu.addAction("Placera i vänstra övre hörnet")
        self.c = actions_menu.addAction("Placera i mitten")
        self.q = actions_menu.addAction("Avsluta")

        # Connect actions to the respective slots
        self.connect_actions()

        # Add pages to the central widget
        self.add_pages()

    def connect_actions(self):
        """
        Connects the menu actions to their corresponding methods.
        """
        self.manage.triggered.connect(lambda: self.show_page(0))
        self.overview.triggered.connect(lambda: self.show_page(1))
        self.f.triggered.connect(self.showFullScreen)
        self.l.triggered.connect(self.showNormal)
        self.t.triggered.connect(self.top_left)
        self.c.triggered.connect(self.center)
        self.q.triggered.connect(QtWidgets.QApplication.instance().quit)

    def add_pages(self):
        """
        Adds the pages (Manage and Display) to the central widget.
        """
        self.central_widget.addWidget(Manage())
        self.central_widget.addWidget(Display())

    @staticmethod
    def create_files():
        """
        Creates CSV files for SAMSA, TES, and KORTTID datasets if they don't already exist.
        """
        if not os.path.exists("samsa.csv"):
            with open("samsa.csv", "w"):
                columns = ["Personnummer", "Förnamn", "Efternamn", "Område", "Inskriven", "Typ", "Anteckning"]
                empty_df = pd.DataFrame(columns=columns)
                empty_df.to_csv("samsa.csv", index=False)

        if not os.path.exists("tes.csv"):
            with open("tes.csv", "w"):
                columns = ["Personnummer", "Förnamn", "Efternamn", "Område", "Inskriven", "Typ", "Anteckning"]
                empty_df = pd.DataFrame(columns=columns)
                empty_df.to_csv("tes.csv", index=False)

        if not os.path.exists("korttid.csv"):
            with open("korttid.csv", "w"):
                columns = ["Personnummer", "Förnamn", "Efternamn", "Område", "Inskriven", "Typ", "Anteckning"]
                empty_df = pd.DataFrame(columns=columns)
                empty_df.to_csv("korttid.csv", index=False)

    def top_left(self):
        """
        Moves the window to the top-left corner of the screen.
        """
        self.move(0, 0)

    def center(self):
        """
        Centers the window on the screen.
        """
        screen = QtWidgets.QApplication.primaryScreen()
        screen_geometry = screen.availableGeometry()
        window_geometry = self.frameGeometry()
        center_point = screen_geometry.center()
        window_geometry.moveCenter(center_point)
        self.move(window_geometry.topLeft())

    @QtCore.Slot()
    def show_page(self, index):
        """
        Shows the page corresponding to the given index.

        :param index: The index of the page to show (0 for Manage, 1 for Display).
        """
        match index:
            case 0:
                self.central_widget.setCurrentIndex(0)
            case 1:
                self.central_widget.setCurrentIndex(1)


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    app.setStyle("Fusion")
    window = Window()
    window.show()
    app.exec()
