
import os
import random
import pylatex as pl


class EmptyPlaceholder(pl.base_classes.CommandBase):
    _latex_name = 'emptyPlaceholder'


def get_operands(first_digits=None, second_digits=None, fixed_second=None, op="mul"):

    first_operand = random.randint(1, 99999)
    if first_digits == 1:
        first_operand = random.randint(1, 9)
    elif first_digits == 2:
        first_operand = random.randint(10, 99)
    elif first_digits == 3:
        first_operand = random.randint(100, 999)
    elif first_digits == 4:
        first_operand = random.randint(1000, 9999)
    elif first_digits == 5:
        first_operand = random.randint(10000, 99999)

    second_operand = fixed_second
    if second_operand is None:
        second_operand_len = 99999
        if op == "sub":
            first_operand_len = len(str(first_operand))
            second_operand_len = int("9"*first_operand_len)
        second_operand = random.randint(1, second_operand_len)
        if second_digits == 1:
            second_operand = random.randint(1, 9)
        elif second_digits == 2:
            second_operand = random.randint(10, 99)
        elif second_digits == 3:
            second_operand = random.randint(100, 999)
        elif second_digits == 4:
            second_operand = random.randint(1000, 9999)
        elif second_digits == 5:
            second_operand = random.randint(10000, 99999)

    return first_operand, second_operand


def create_exercise(first_digits=None, second_digits=None, fixed_second=None, op="mul"):

    first_operand, second_operand = get_operands(
        first_digits=first_digits,
        second_digits=second_digits,
        fixed_second=fixed_second,
        op=op
    )

    if op == "mul":
        expression = "\opmul[resultstyle=\emptyPlaceholder,intermediarystyle=\emptyPlaceholder]{%i}{%i}" % (first_operand, second_operand)
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
    if operation == "mul":
        title_str = "Multiplication"
    elif operation == "div":
        title_str = "Division"
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
            data_table.add_empty_row()

    # Save PDF
    if os.path.isfile(filepath):
        os.remove(filepath)
    if filepath.endswith(".pdf"):
        filepath = filepath[:-4]

    doc.generate_pdf(filepath, clean_tex=True)


if __name__ == "__main__":

    filename = input("filename: ")
    operation = input("operation (mul, div, add, sub): ")
    num_exercises = input("number of exercises: ")

    first_operand_digits = input("Number of digits for first operand: ")
    if first_operand_digits == "":
        first_operand_digits = None
    if first_operand_digits is not None:
        first_operand_digits = int(first_operand_digits)

    second_operand_digits = input("Number of digits for second operand: ")
    if second_operand_digits == "":
        second_operand_digits = None
    if second_operand_digits is not None:
        second_operand_digits = int(second_operand_digits)

    second_operand = None
    if operation in ["mul", "div"]:
        second_operand = input("Use second operand: ")
        if second_operand == "":
            second_operand = None
        else:
            second_operand = int(second_operand)


    this_dir = os.path.dirname(os.path.realpath(__file__))
    filedir = os.path.join(this_dir, "PDFs")
    if not os.path.isdir(filedir):
        os.makedirs(filedir)
    filepath = os.path.join(filedir, filename + ".pdf")

    create_doc(
        filepath,
        num_exercises=int(num_exercises),
        operation=operation,
        first_operand_digits=first_operand_digits,
        second_operand_digits=second_operand_digits,
        second_operand=second_operand
    )
