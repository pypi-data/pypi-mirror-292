# simple-latex-checker

This was created to help debug the __most common problem__ students face when trying to download their jupyter Notebooks as PDFs, erroneous spaces in their in-line latex. I spun this up in a few hours, so it would definitely be useful to add a few more features. 

To use:

1. Download the package

`pip install simple-latex-checker`

2. Import the package into your jupyter notebook

`import simple_latex_checker as slc`

3. Run the check

`slc.run_check("<Your Notbook Name>.ipynb")`