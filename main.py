
# Standard
import os
import random
import sys

# Qt
from PySide2 import QtCore
from PySide2 import QtGui
from PySide2 import QtWidgets

# PyLatex
import pylatex as pl


class EmptyPlaceholder(pl.base_classes.CommandBase):
    _latex_name = 'emptyPlaceholder'


def get_operands(first_digits=None,
                 second_digits=None,
                 fixed_second=None,
                 op="mul",
                 force_nice_solution=True):

    max_digits = 5

    first_min_limit = 1
    first_max_limit = int("9"*max_digits)
    if first_digits is not None:
        first_min_limit = int("1" + "0"*(first_digits-1))
        first_max_limit = int("9"*(first_digits))
    first_operand = random.randint(first_min_limit, first_max_limit)
    if (op == "div") and (force_nice_solution) and (fixed_second is not None):
        # we want the first operand to be a multiple of the provided fixed_second
        first_operand = random.randrange(first_min_limit, first_max_limit, fixed_second)

    second_min_limit = 1
    second_max_limit = int("9"*max_digits)
    if second_digits is not None:
        second_min_limit = int("1" + "0"*(second_digits-1))
        second_max_limit = int("9"*(second_digits))
    second_operand = random.randint(second_min_limit, second_max_limit)
    if fixed_second is not None:
        second_operand = fixed_second
    elif (op == "sub") and (force_nice_solution):
        # we want the result to be a positive number
        if second_min_limit < first_operand:
            second_operand = random.randint(second_min_limit, first_operand)

    return first_operand, second_operand


def create_exercise(first_digits=None, second_digits=None, fixed_second=None, op="mul"):

    first_operand, second_operand = get_operands(
        first_digits=first_digits,
        second_digits=second_digits,
        fixed_second=fixed_second,
        op=op
    )

    if op == "mul":
        expression = "\opmul[resultstyle=\emptyPlaceholder,displayshiftintermediary=none,displayintermediary=None]{%i}{%i}" % (first_operand, second_operand)
    elif op == "div":
        expression = "\intlongdivision[stage=0,style=tikz]{%i}{%i} \quad" % (first_operand, second_operand)
    elif op == "add":
        expression = "\opadd[resultstyle=\emptyPlaceholder,carryadd=false]{%i}{%i}" % (first_operand, second_operand)
    elif op == "sub":
        expression = "\opsub[resultstyle=\emptyPlaceholder,carryadd=false]{%i}{%i}" % (first_operand, second_operand)

    return pl.NoEscape(expression)


def create_doc(filepath,
               num_exercises=25,
               operation="mul",
               first_operand_digits=None,
               second_operand_digits=None,
               second_operand=None):

    title_str = ""
    num_empty_rows = 1
    if operation == "mul":
        title_str = "Multiplication"
        num_empty_rows = 2
    elif operation == "div":
        title_str = "Division"
        num_empty_rows = 2
    elif operation == "add":
        title_str = "Addition"
    elif operation == "sub":
        title_str = "Subtraction"

    # Create doc
    geometry_options = {
        "head": "40pt",
        "margin": "0.5in",
        "bottom": "0.6in",
        "includeheadfoot": True
    }
    doc = pl.Document(
        indent=False,
        geometry_options=geometry_options,
        page_numbers=True
    )
    doc.packages.append(pl.Package('xlop'))
    doc.packages.append(pl.Package('xcolor'))
    doc.packages.append(pl.Package('longdivision'))
    doc.packages.append(pl.Package('tikz'))

    new_cmd = pl.UnsafeCommand(
        'newcommand',
        '\emptyPlaceholder',
        options=1,
        extra_arguments=''
    )
    doc.append(new_cmd)

    # Header
    header = pl.PageStyle("header")
    with header.create(pl.Head("C")):
        header.append(title_str)
    doc.preamble.append(header)
    doc.change_document_style("header")

    # Create table
    num_per_row = 5
    if num_exercises < num_per_row:
        num_per_row = 1
    num_rows = int(num_exercises/num_per_row)
    row_spec = " ".join(["X[c]" for i in range(num_per_row)])
    table = pl.LongTabu(row_spec, row_height=1.5)

    # Populate table
    with doc.create(table) as data_table:
        for i in range(num_rows):
            row = []
            for j in range(num_per_row):
                e = create_exercise(
                    first_digits=first_operand_digits,
                    second_digits=second_operand_digits,
                    fixed_second=second_operand,
                    op=operation
                )
                row.append(e)
            data_table.add_row(row)
            for r in range(num_empty_rows):
                data_table.add_empty_row()

    # Save PDF
    if os.path.isfile(filepath):
        os.remove(filepath)
    if filepath.endswith(".pdf"):
        filepath = filepath[:-4]

    doc.generate_pdf(filepath, clean_tex=True)


class GenerateMathPDF(QtWidgets.QDialog):

    UI_OBJECT_NAME = "GenerateMathPDF"

    def __init__(self, parent=None):
        super(GenerateMathPDF, self).__init__(parent)

        self.setObjectName(self.UI_OBJECT_NAME)
        self.setWindowTitle("Generate Math PDF")
        self.setWindowFlags(QtCore.Qt.Window)

        self.setup()
        self.show()

    def sizeHint(self):
        return (QtCore.QSize(300, 300))

    def line(self, orientation="horizontal"):
        line = QtWidgets.QFrame()
        if orientation == "vertical":
            line.setFrameShape(QtWidgets.QFrame.VLine)
        elif orientation == "horizontal":
            line.setFrameShape(QtWidgets.QFrame.HLine)

        line.setFrameShadow(QtWidgets.QFrame.Sunken)

        return line

    def setup(self):

        # -------------------------------------
        # Filename
        # -------------------------------------
        self.filename = QtWidgets.QLineEdit()

        filename_layout = QtWidgets.QHBoxLayout()
        filename_layout.addWidget(QtWidgets.QLabel("Filename:"))
        filename_layout.addWidget(self.filename)
        filename_layout.addStretch()

        # -------------------------------------
        # Number of exercises
        # -------------------------------------
        self.num_exercises = QtWidgets.QSpinBox()
        self.num_exercises.setMinimum(1)
        self.num_exercises.setMaximum(999)
        self.num_exercises.setValue(50)
        num_exercises_layout = QtWidgets.QHBoxLayout()
        num_exercises_layout.addWidget(QtWidgets.QLabel("Number of exercises:"))
        num_exercises_layout.addWidget(self.num_exercises)
        num_exercises_layout.addStretch()

        # -------------------------------------
        # First operand
        # -------------------------------------
        self.use_first_operand_digits = QtWidgets.QCheckBox()
        self.use_first_operand_digits.setChecked(True)
        self.first_operand_digits = QtWidgets.QSpinBox()
        self.first_operand_digits.setMinimum(1)
        self.first_operand_digits.setMaximum(999999)
        self.first_operand_digits.setValue(3)

        first_operand_layout = QtWidgets.QHBoxLayout()
        first_operand_layout.addWidget(QtWidgets.QLabel("First operant digits:"))
        first_operand_layout.addWidget(self.use_first_operand_digits)
        first_operand_layout.addWidget(self.first_operand_digits)
        first_operand_layout.addStretch()

        # -------------------------------------
        # Second operand
        # -------------------------------------
        self.use_second_operand_digits = QtWidgets.QCheckBox()
        self.use_second_operand_digits.setChecked(False)
        self.second_operand_digits = QtWidgets.QSpinBox()
        self.second_operand_digits.setMinimum(1)
        self.second_operand_digits.setMaximum(999999)
        self.second_operand_digits.setValue(2)

        second_operand_layout = QtWidgets.QHBoxLayout()
        second_operand_layout.addWidget(QtWidgets.QLabel("Second operant digits:"))
        second_operand_layout.addWidget(self.use_second_operand_digits)
        second_operand_layout.addWidget(self.second_operand_digits)
        second_operand_layout.addStretch()

        # -------------------------------------
        # Fixed second operand
        # -------------------------------------
        self.use_fixed_second_operand = QtWidgets.QCheckBox()
        self.use_fixed_second_operand.setChecked(True)
        self.fixed_second_operand = QtWidgets.QSpinBox()
        self.fixed_second_operand.setMinimum(1)
        self.fixed_second_operand.setMaximum(999999)
        self.fixed_second_operand.setValue(2)

        fixed_second_operand_layout = QtWidgets.QHBoxLayout()
        fixed_second_operand_layout.addWidget(QtWidgets.QLabel("Fixed second operant:"))
        fixed_second_operand_layout.addWidget(self.use_fixed_second_operand)
        fixed_second_operand_layout.addWidget(self.fixed_second_operand)
        fixed_second_operand_layout.addStretch()

        # -------------------------------------
        # Operations
        # -------------------------------------
        self.op_add = QtWidgets.QRadioButton("Addition")
        self.op_add.id = "add"
        self.op_sub = QtWidgets.QRadioButton("Subtraction")
        self.op_sub.id = "sub"
        self.op_mul = QtWidgets.QRadioButton("Multiplication")
        self.op_mul.id = "mul"
        self.op_div = QtWidgets.QRadioButton("Division")
        self.op_div.id = "div"

        self.op_add.setChecked(True)

        self.op_btngrp = QtWidgets.QButtonGroup()
        self.op_btngrp.setExclusive(True)
        self.op_btngrp.addButton(self.op_add)
        self.op_btngrp.addButton(self.op_sub)
        self.op_btngrp.addButton(self.op_mul)
        self.op_btngrp.addButton(self.op_div)

        op_layout = QtWidgets.QVBoxLayout()
        op_layout.addWidget(self.op_add)
        op_layout.addWidget(self.op_sub)
        op_layout.addWidget(self.op_mul)
        op_layout.addWidget(self.op_div)
        op_layout.addStretch()
        op_layout.setContentsMargins(0, 0, 0, 0)

        # -------------------------------------
        # Action
        # -------------------------------------
        self.run_btn = QtWidgets.QPushButton("Generate")
        self.run_btn.clicked.connect(self.run)

        # -------------------------------------
        # Main layout
        # -------------------------------------
        main_layout = QtWidgets.QVBoxLayout()
        main_layout.addLayout(filename_layout)
        main_layout.addLayout(num_exercises_layout)
        main_layout.addLayout(first_operand_layout)
        main_layout.addLayout(second_operand_layout)
        main_layout.addLayout(fixed_second_operand_layout)
        main_layout.addWidget(self.line())
        main_layout.addLayout(op_layout)
        main_layout.addWidget(self.line())
        main_layout.addStretch()
        main_layout.addWidget(self.run_btn)
        main_layout.setContentsMargins(5, 5, 5, 5)

        self.setLayout(main_layout)

    def run(self):

        filename = self.filename.text()
        this_dir = os.path.dirname(os.path.realpath(__file__))
        filedir = os.path.join(this_dir, "PDFs")
        if not os.path.isdir(filedir):
            os.makedirs(filedir)
        filepath = os.path.join(filedir, filename + ".pdf")

        num_exercises = int(self.num_exercises.value())

        use_first_operand_digits = self.use_first_operand_digits.isChecked()
        first_operand_digits = int(self.first_operand_digits.value())
        if not use_first_operand_digits:
            first_operand_digits = None

        use_second_operand_digits = self.use_second_operand_digits.isChecked()
        second_operand_digits = int(self.second_operand_digits.value())
        if not use_second_operand_digits:
            second_operand_digits = None

        use_fixed_second_operand = self.use_fixed_second_operand.isChecked()
        fixed_second_operand = int(self.fixed_second_operand.value())
        if not use_fixed_second_operand:
            fixed_second_operand = None

        op = self.op_btngrp.checkedButton().id

        create_doc(
            filepath,
            num_exercises=num_exercises,
            operation=op,
            first_operand_digits=first_operand_digits,
            second_operand_digits=second_operand_digits,
            second_operand=fixed_second_operand
        )

        diag = QtWidgets.QMessageBox(self)
        diag.setWindowTitle("Result")
        if os.path.isfile(filepath):
            diag.setText("PDF created")
        else:
            diag.setText("Failed")
        diag.exec_()


if __name__ == "__main__":

    app = QtWidgets.QApplication(sys.argv)

    app.setStyle("Fusion")
    dark_palette = QtGui.QPalette()
    dark_palette.setColor(QtGui.QPalette.Window, QtGui.QColor(53, 53, 53))
    dark_palette.setColor(QtGui.QPalette.WindowText, QtGui.QColorConstants.White)
    dark_palette.setColor(QtGui.QPalette.Base, QtGui.QColor(35, 35, 35))
    dark_palette.setColor(QtGui.QPalette.AlternateBase, QtGui.QColor(53, 53, 53))
    dark_palette.setColor(QtGui.QPalette.ToolTipBase, QtGui.QColor(25, 25, 25))
    dark_palette.setColor(QtGui.QPalette.ToolTipText, QtGui.QColorConstants.White)
    dark_palette.setColor(QtGui.QPalette.Text, QtGui.QColorConstants.White)
    dark_palette.setColor(QtGui.QPalette.Button, QtGui.QColor(53, 53, 53))
    dark_palette.setColor(QtGui.QPalette.ButtonText, QtGui.QColorConstants.White)
    dark_palette.setColor(QtGui.QPalette.BrightText, QtGui.QColorConstants.Red)
    dark_palette.setColor(QtGui.QPalette.Link, QtGui.QColor(42, 130, 218))
    dark_palette.setColor(QtGui.QPalette.Highlight, QtGui.QColor(42, 130, 218))
    dark_palette.setColor(QtGui.QPalette.HighlightedText, QtGui.QColor(35, 35, 35))
    dark_palette.setColor(QtGui.QPalette.Active, QtGui.QPalette.Button, QtGui.QColor(53, 53, 53))
    dark_palette.setColor(QtGui.QPalette.Disabled, QtGui.QPalette.ButtonText, QtGui.QColorConstants.DarkGray)
    dark_palette.setColor(QtGui.QPalette.Disabled, QtGui.QPalette.WindowText, QtGui.QColorConstants.DarkGray)
    dark_palette.setColor(QtGui.QPalette.Disabled, QtGui.QPalette.Text, QtGui.QColorConstants.DarkGray)
    dark_palette.setColor(QtGui.QPalette.Disabled, QtGui.QPalette.Light, QtGui.QColor(53, 53, 53))
    app.setPalette(dark_palette)

    win = GenerateMathPDF(parent=None)

    sys.exit(app.exec_())
