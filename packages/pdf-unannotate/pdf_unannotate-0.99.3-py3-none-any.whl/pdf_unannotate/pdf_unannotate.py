import os
import re
import sys

from tqdm import tqdm
from glob import glob
from PyPDF2 import PdfReader, PdfWriter

def _unannotate_pdfs(files: list[str], suffix: str) -> None:
	print('Removing annotations from PDFs.')
	for file in tqdm(files):
		with open(file, 'rb') as pdf_obj:
			pdf = PdfReader(pdf_obj)
			out = PdfWriter()
			for page in pdf.pages:
				if page.annotations:
					page.annotations.clear()
				out.add_page(page)
		
		outfile = re.sub(r'\.pdf$', f'{suffix}.pdf', file)
		with open(outfile, 'wb') as out_pdf:
			out.write(out_pdf)

def unannotate_pdfs(s) -> None:
	'''
	Remove annotations from all PDFs matching glob expressions.
	s consists of command line args except for 'pdf-unannotate'
	the final argument should be the glob pattern.
	'''
	breakpoint()
	try:
		files = s[-1].split(':')
	except IndexError:
		raise IndexError('You need to provide some PDFs!')
	
	suffix = [arg.split('=')[1] for arg in s[:-1] if arg.startswith('suffix=')]
	suffix = suffix[0] if suffix else [' - unannotated']
	
	regex = [arg.split('=')[1] for arg in s[:-1] if arg.startswith('regex=')]
	regex = regex[0] if regex else []
	
	globbed = []
	for file in files:
		globbed.append(glob(file, recursive=True))
	
	globbed = [file for l in globbed for file in l if file.endswith('.pdf')]
	
	if regex:
		globbed = [file for file in globbed if re.match(regex, file)]
	
	if len(globbed) == 0:
		print('No PDFs matching expression "' + s[-1] + '" found.')
		sys.exit(0)
	
	globbed = sorted(globbed)
	
	try:
		_unnanotate_pdfs(files=globbed, suffix=suffix)
	except KeyboardInterrupt:
		print('User terminated.')
		sys.exit(0)
	except Exception:
		print('Error removing annotations.')

if __name__ == '__main__':
	args = [arg for arg in sys.argv[1:] if not arg == 'pdf_unannotate.py']
	unannotate_pdfs(args)