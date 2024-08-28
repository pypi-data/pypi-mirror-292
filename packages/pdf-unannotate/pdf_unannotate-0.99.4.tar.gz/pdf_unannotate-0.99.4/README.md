# pdf-unannotate

`pdf-unannotate` facilitates easily removing annotations from PDFs using `PyPDF2`.

## Usage

After installing using `pip`, you can run `pdf-unannotate` as a command. It takes a single glob expression as an argument, and it will remove annotations from all PDFs matching the glob.

If you need to include spaces in a file name, make sure to escape them by using single quotes. If you do not escape the glob expression using single quotes, make sure to escape any `*` in the glob expression with a backslash, since otherwise they will be expanded by the shell before pdf-unannotate gets them.

- `regex`: (optional) only PDFs with filenames matching `regex` will have annotations removed.
- (`pattern`): (required, not named) a glob expression that matches PDFs to remove annotations from. Only files ending in `.pdf` that match the glob will be included. If a glob expression is insufficient to filter to just the scripts you want, you should use the `regex` argument.

## Description

`pdf-unannotate` finds all `.pdf` files matching `pattern` (and `regex`, if provided). If PDFs are found, it removes annotations from them one-by-one using PyPDF2.