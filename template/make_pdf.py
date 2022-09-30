import pdfkit,os
def GeneratePDF(name_doc,path):
	path_dir = path
	if not os.path.exists(path_dir):
		os.makedirs(path_dir)
	pdfkit.from_file('template/pdfs/'+name_doc+'.html', path_dir+'/'+name_doc+'.pdf')