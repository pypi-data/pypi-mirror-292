import nbformat
import re


def run_check(notebook_path):
    # Load current notebook
    with open(notebook_path, 'r', encoding='utf-8') as f:
        notebook = nbformat.read(f, as_version=4)

    # Access raw content from Markdown cells
    raw_markdown_cells = list()
    for cell_num, cell in enumerate(notebook.cells, 1):
        if cell.cell_type == 'markdown':
            raw_markdown_cells.append((cell.source, cell_num))

    if raw_markdown_cells:
        one_time_warning = False
        for cell_meta in raw_markdown_cells:
            cell, cell_num = cell_meta
            latex_only_arr = find_latex(cell)
            # Finds if any warnings have been printed to display the 'fix' message
            if not one_time_warning:
                one_time_warning = latex_warning(latex_only_arr, cell_num)
            else:
                latex_warning(latex_only_arr, cell_num)
        if one_time_warning:
            print("\n\nLatex expressions cannot contain spaces after '\$' when entering math mode or before '\$' when exiting.\nPlease fix these errors before exporting.")
    else:
        print("No Markdown cells to check!")

def find_latex(markdown):
    """Uses Regex Pattern matching to find all instances of Latex math mode in a markdown cell and adds
    to a list

    Args:
        markdown (string): string containing the raw markdown of a cell

    Returns:
        List: list containing all the markdown instances in a latex cell
    """
    latex_finder = r"\$(.*?(?:\\\$[^$]*?)*)\$"
    latex_array = re.findall(latex_finder, markdown)
    return latex_array

def latex_warning(latex_array, cell):
    """prints a warning when errors are found in the latex cell. These warnings are only space's in the
    incorrect location in math mode for now. 

    Args:
        latex_array (List): List containing all the latex expressions for a cell 
        cell (Integer): the number of the cell containing the error 
    """
    for expr in latex_array:
        if expr.startswith(" ") or expr.endswith(" "):
            print(f"Error found in\033[31m cell {cell}\033[0m. Bad expression: {expr}")
            return True

        
    