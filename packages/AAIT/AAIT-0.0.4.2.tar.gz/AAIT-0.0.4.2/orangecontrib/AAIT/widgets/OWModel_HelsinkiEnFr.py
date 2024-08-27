import os
import sys
from transformers import MarianMTModel, AutoTokenizer

from Orange.widgets import widget
from Orange.widgets.utils.signals import Output

from PyQt5 import uic
from AnyQt.QtWidgets import QApplication

if "site-packages/Orange/widgets" in os.path.dirname(os.path.abspath(__file__)).replace("\\", "/"):
    from Orange.widgets.orangecontrib.AAIT.utils import thread_management, SimpleDialogQt
    from Orange.widgets.orangecontrib.AAIT.utils.MetManagement import get_local_store_path, GetFromRemote
else:
    from orangecontrib.AAIT.utils import thread_management, SimpleDialogQt
    from orangecontrib.AAIT.utils.MetManagement import get_local_store_path, GetFromRemote


class OWModel_HelsinkiEnFr(widget.OWWidget):
    name = "Model - Translation - Helsinki EN-FR"
    description = "Load the translation model Helsinki EN-FR from the AAIT Store"
    icon = "icons/owmodel_helsinki_en_fr.png"
    if "site-packages/Orange/widgets" in os.path.dirname(os.path.abspath(__file__)).replace("\\", "/"):
        icon = "icons_dev/owmodel_helsinki_en_fr.png"
    gui = os.path.join(os.path.dirname(os.path.abspath(__file__)), "designer/owmodel_helsinki_en_fr.ui")
    want_control_area = False

    class Outputs:
        model = Output("Model", (MarianMTModel, object))

    def __init__(self):
        super().__init__()
        # Path management
        self.current_ows = ""
        local_store_path = get_local_store_path()
        model_name = "helsinki_en_fr"
        self.model_path = os.path.join(local_store_path, "Models", "NLP", model_name)
        self.model = None
        self.tokenizer = None

        # Qt Management
        self.setFixedWidth(470)
        self.setFixedHeight(300)
        uic.loadUi(self.gui, self)
        if not os.path.exists(self.model_path):
            if not SimpleDialogQt.BoxYesNo("Model isn't in your computer. Do you want to download it from AAIT store?"):
                return
            try:
                GetFromRemote("Translation")
            except Exception as e:  # TODO ciblage de l'erreur
                SimpleDialogQt.BoxError("Unable to get the model:", e)
                return
        # Data Management
        self.progressBarInit()
        self.thread = thread_management.Thread(self.load_model, self.model_path)
        self.thread.finish.connect(self.handle_loading_finish)
        self.thread.start()

    def load_model(self, model_path):
        self.model = MarianMTModel.from_pretrained(model_path)
        self.tokenizer = AutoTokenizer.from_pretrained(model_path)

    def handle_loading_finish(self):
        output = (self.model, self.tokenizer)
        if self.model is not None:
            self.Outputs.model.send(output)
        else:
            SimpleDialogQt.BoxError("An Error Occurred when loading model.")
            self.Outputs.model.send(None)
        self.progressBarFinished()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    my_widget = OWModel_HelsinkiEnFr()
    my_widget.show()
    app.exec_()
