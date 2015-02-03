import sys
import os
import string
from pdfminer.pdfparser import PDFDocument, PDFParser
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter, process_pdf
from pdfminer.pdfdevice import PDFDevice
from pdfminer.converter import TextConverter
from pdfminer.cmapdb import CMapDB
from pdfminer.layout import LAParams

def parse_first_page(pdf_file):
  rsrcmgr = PDFResourceManager(caching=True)
  outfp = open('temp_title','w')
  device = TextConverter(rsrcmgr, outfp, codec='utf-8', laparams=LAParams())
  pdf = open(pdf_file,'r')
  process_pdf(rsrcmgr,device,pdf,pagenos=set(),maxpages=2,password='',caching=True,check_extractable=True)
  outfp.close()
  print 'Successfully parsed',pdf_file

def clean_up_and_lower(title_string):
  '''Remove fancy characters that break things'''
  badchars = ('_','.','-','!','?')
  for i in badchars:
    title_string = title_string.replace(i,'')
  return title_string.lower()


def guess_title():
  """Tries to guess the title given popular file formats"""
  pdf_text = open('temp_title','r')
  title = clean_up_and_lower(pdf_text.readline().strip())
  
  singles = list(string.ascii_lowercase)
  for x in ['a','i','m','n','e']:
    singles.remove(x)
  print singles
  bad_title_first_words=[' USA','Proceedings of','LETTER','Journal of','ARTICLE','ar ticle','Communicated by','Communicated_by','anuscript','Public Access',' S ','USENIX','PERSPECTIVES','Brevia','COMMUN ','PHYSICAL REVIEW','Conference','Symantec Research','Symposium','Vol.','IEEE','Editors','Published by','Published in','Permissions','email','doi:'] 

  lower_bad_title = [x.lower() for x in bad_title_first_words]

  while title.isdigit() or title == '' or len(title.split()) == 1 or any([x in
    title for x in lower_bad_title]) or any([y in title.split() for y in singles] ):
    title = clean_up_and_lower(pdf_text.readline().strip())
    print title
    print title.split()
  print 'Good title',title
  print title.split()
  t = title.split()
  print len(t)
  while len(t) == 1:
    print title
    ri = raw_input('Would you like to skip this? y/n')
    if ri == 'y':
      title = pdf_text.readline().strip()
      t = title.split()
      print title
      
  # We think we have the beginning of a title
  rest = ''
  # Let's join titles that are obviously split over two lines.. 
  while (not t[-1][0].isupper() and not t[-1][0].isdigit()) or (t[-1][-1] == ':'): 
    next = pdf_text.readline().strip()
    if next.isdigit() or next == '' or len(next) == 1 or any([x in next for x in bad_title_first_words]):
      break
    else:
      rest += (' '+next) 
      t = next.split()

  return '_'.join((title+rest).split())

def sanitize(title):
  # Remove wierd characters that are bad for whilename
  for i in title:
    if not i.isalnum() and i !='_':
      title = title.replace(i,'')
  print title
  return title

def get_title(fn):
  parse_first_page(fn)
  title= guess_title()
  return title

def title_rename(title,fn):
  title=sanitize(title)
  os.rename(fn,title+'.pdf')
  print 'Rename of',fn,'complete'
  os.remove('temp_title')
  print 'Title:',title
  return title+'.pdf'

if __name__ == '__main__':
  fn = sys.argv[1]
  title = get_title(fn)
  if len(sys.argv)>2:
    if sys.argv[2] == '-r':
      title_rename(title,fn)
