# https://orange3.readthedocs.io/projects/orange-development/en/latest/tutorial-settings.html


import ctypes
import os
import sys

import Orange.data
from Orange.data import Domain, ContinuousVariable
from Orange.data.table import Table
from Orange.widgets import widget

from Orange.widgets.utils.signals import Input, Output
from PyQt5 import QtCore, QtGui, QtWidgets
import time

if "site-packages/Orange/widgets" in os.path.dirname(os.path.abspath(__file__)).replace("\\","/"):
    from Orange.widgets.orangecontrib.AAIT.utils.shared_functions import setup_shared_variables
    from Orange.widgets.orangecontrib.AAIT.optimiser import optuna_multi
else:
    from orangecontrib.AAIT.utils.shared_functions import setup_shared_variables
    from Orange.widgets.orangecontrib.AAIT.optimiser import optuna_multi

class Optimisation(widget.OWWidget):
    name = "Optimisation"
    description = "Optimisation avec optuna"
    icon = "icons/owoptimisation.svg"
    priority = 10
    dossier_du_script = os.path.dirname(os.path.abspath(__file__))
    want_control_area = False
    partie_1 = ""
    partie_2 = ""
    CaptionDuLabelPourGoto = ""
    AddAcondition = 0
    liste_a_afficher_comboBox_selection_label = []

    class Inputs:
        data_standard_input = Input("User Proposition Data", Orange.data.Table)
        data_search_space = Input("Search Space Limits", Orange.data.Table)
        data_number_iterations = Input("Number of iterations", Orange.data.Table)
        data_previous_study = Input("Previous Study Data", Orange.data.Table)

    class Outputs:
        data_out = Output("Data", Orange.data.Table)
        best_trial_out = Output("Best trial", Orange.data.Table)
        current_proposition_out = Output("Current proposition (preview)", Orange.data.Table)
        user_proposition_out = Output("Current User Proposition (preview)", Orange.data.Table)
        studies_out = Output("Last Studies ", Orange.data.Table)
        out_pointer = Output("begin of the loop", str)  # sended as the widget is created

    # c est ce decorateur qui est fait qu il se passe quelque
    @Inputs.data_standard_input
    def set_data_standard_input(self, dataset):
        if self.current_data_previous_study is not None and self.current_data_search_space is not None and dataset is not None and self.len_score is not None:
            self.current_data_standard_input = dataset
            if self.current_data_standard_input.domain != self.current_data_search_space.domain:
                print("Domain différent de l espace de recherche")
                return
            score = None
            last_ligne = self.current_data_previous_study[-1]
            if self.current_data_previous_study[-1][len(last_ligne)-1] == '?':
                self.current_data_previous_study = self.current_data_previous_study[:-1]
            data, domain = optuna_multi.get_domain_and_data_from_previous_study(score, self.len_score, self.current_data_search_space, self.current_data_previous_study)
            d = []
            for i in range(len(self.current_data_standard_input.domain)):
                d.append(self.current_data_standard_input[0][i].value)
            for i in range(self.len_score):
                d.append("?")
            data.append(d)

            #envoie de l'étude du create instance
            #self.Outputs.current_proposition_out.send(Table.from_list(Domain([ContinuousVariable(h) for h in domain]),[d]))
            self.current_data_previous_study = Table.from_list(Domain([ContinuousVariable(h) for h in domain]),
                                                               data[3:])
            self.Outputs.user_proposition_out.send(Table.from_list(Domain([ContinuousVariable(h) for h in domain]), [data[-1]]))


    @Inputs.data_number_iterations
    def set_data_number_iterations(self, dataset):
        if dataset is not None:
            self.current_data_number_iterations = dataset[0][0]
            self.compteur_iteration = 1
            # pour relancer une etude
            self.itere(score=None)

    @Inputs.data_search_space
    def set_data_search_space(self, dataset):
        if dataset is not None:
            self.current_data_search_space = dataset
            self.len_file_current_data_search_space = len(dataset)

    @Inputs.data_previous_study
    def set_data_previous_study(self, dataset):
        self.current_data_previous_study = dataset


    # on lance l'étude et définition des data table en sortie
    def launch_study(self, score):
        ligne_best_etude, data, domain, current_proposition_out = optuna_multi.launch_study(score, self.len_score, self.current_data_search_space, self.current_data_previous_study, self.stop)

        if ligne_best_etude != []:
            table_best_etude = Table.from_list(Domain([ContinuousVariable(h) for h in domain]), ligne_best_etude)
            self.Outputs.best_trial_out.send(table_best_etude)

        if current_proposition_out != []:
            table = Table.from_list(Domain([ContinuousVariable(h) for h in domain]), current_proposition_out)
            self.Outputs.current_proposition_out.send(table)

        self.current_data_previous_study = Table.from_list(Domain([ContinuousVariable(h) for h in domain]), data[3:])
        self.Outputs.studies_out.send(self.current_data_previous_study)

        if self.stop == True:
            self.stop = False
            return


    # appelé depuis un focntion tierce
    def itere(self, score=[]):
        if self.current_data_search_space is None:
            print('Erreur il n y a pas de paramètres de configuration en entree')
            return

        if self.current_data_number_iterations is None:
            if self.compteur_iteration > 10:
                self.stop = True
        else:
            if self.compteur_iteration > self.current_data_number_iterations:
                self.stop = True

        self.compteur_iteration = self.compteur_iteration + 1

        # dans le cas du chargement d'une ancienne étude
        if self.current_data_previous_study is not None:
            self.len_score = len(self.current_data_previous_study.domain) - len(self.current_data_search_space.domain)

        if score is not None:
            new_score = []
            for i in range(len(score[0])):
                if score[0][i] != '?':
                   new_score.append(score[0][i].value)
            # ajouter car le feature constructor peut garder les anciens scores
            if self.len_score is None:
                self.len_score = len(new_score)

            #if len(new_score) != self.len_score:
                #print('Erreur les nombres de scores entre les études sont différents')
                #return
            self.launch_study(new_score)

        else:
            self.launch_study(score)



    def __init__(self):

        self.current_data_standard_input = None
        self.current_data_search_space = None
        self.current_data_previous_study = None
        self.current_data_number_iterations = None
        self.etude = None
        self.stop = False
        self.len_score = None
        # compteur_iteration
        self.compteur_iteration = 1
        self.len_file_current_data_search_space = 0

        # on envoie l identifiant pour pouvoir boucler
        self.Outputs.out_pointer.send(str(id(self)))

        super().__init__()  # je pense que c'est pour garder les config entre deux executions
        setup_shared_variables(self)

        self.setFixedWidth(480)
        self.setFixedHeight(354)
        self.setAutoFillBackground(True)



if __name__ == "__main__":
    from AnyQt.QtWidgets import QApplication
    app = QApplication(sys.argv)
    mon_objet = Optimisation()
    mon_objet.show()
    app.exec_()



