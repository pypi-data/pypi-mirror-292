# __main__.py

import sys

from .pdf_unannotate import unannotate_pdfs

def main():
	'''
	Run sbatch_all to submit scripts matching
	a glob expression as job arrays using Yale's dSQ.
	'''
	args = [arg for arg in sys.argv[1:] if not 'pdf-unannotate' in arg]
	unannotate_pdfs(args)

if __name__ == '__main__':
	main()