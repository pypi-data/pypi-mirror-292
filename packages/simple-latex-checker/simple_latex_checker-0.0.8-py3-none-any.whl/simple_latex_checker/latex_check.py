import nbformat
import re


class Nb_checker:
    _has_errors = False
    _one_time_latex_warning = False

    def run_check(self, notebook_path, correct_cells = None):
        """Checks that there are no erroneous spaces in the latex math mode and that the number of cells is what 
        the autograder expects

        Args:
            notebook_path (string): path to the notebook. Should just be <My Notebook Name>.ipynb
        """
        # Load current notebook
        with open(notebook_path, 'r', encoding='utf-8') as f:
            notebook = nbformat.read(f, as_version=4)

        # Access raw content from Markdown cells
        raw_markdown_cells = list()
        for cell_num, cell in enumerate(notebook.cells, 1):
            if cell.cell_type == 'markdown':
                raw_markdown_cells.append((cell.source, cell_num))
        if(correct_cells is not None):
            self.verify_cells(notebook, correct_cells)
        if raw_markdown_cells:
            one_time_warning = False
            for cell_meta in raw_markdown_cells:
                cell, cell_num = cell_meta
                latex_only_arr = self.find_latex(cell)
                self.latex_warning(latex_only_arr, cell_num)
            if self._one_time_latex_warning:
                print("\n\nLatex expressions cannot contain spaces after '\$' when entering math mode or before '\$' when exiting.\nPlease fix these errors before exporting.")
        else:
            print("No Markdown cells to check!")
        self.no_errors_print()

    def verify_cells(self, notebook, correct_cells):
        """Ensures the number of cells matches the number of cells that should be in the notebook for the autograder.

        Args:
            notebook (nb): current notebook the user is using
            correct_cells (integer):number of cells the notebook should have
        """
        num_cells = len(notebook.cells)
        if num_cells != correct_cells:
            print(f"\033[31mIncorrect number of cells\033[0m. Your notebook has {num_cells}, but should have {correct_cells}.")
            self._has_errors = True

    def find_latex(self, markdown):
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

    def latex_warning(self, latex_array, cell):
        """prints a warning when errors are found in the latex cell. These warnings are only space's in the
        incorrect location in math mode for now. 

        Args:
            latex_array (List): List containing all the latex expressions for a cell 
            cell (Integer): the number of the cell containing the error 
        """
        for expr in latex_array:
            if expr.startswith(" ") or expr.endswith(" "):
                print(f"Error found in\033[31m cell {cell}\033[0m. Bad expression: {expr}")
                self._has_errors = True
                self._one_time_latex_warning = True
    
    def no_errors_print(self):
        if not self._has_errors:
            print("No detected errors. Export can be run.")

        
    