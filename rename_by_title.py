import codecs
import os
import re
import string
import sys
import unicodedata
from pdfminer.pdfparser import PDFDocument, PDFParser
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter, process_pdf
from pdfminer.pdfdevice import PDFDevice
from pdfminer.converter import TextConverter
from pdfminer.cmapdb import CMapDB
from pdfminer.layout import LAParams

def parse_first_page(pdf_file, tmp_file):
  rsrcmgr = PDFResourceManager(caching=True)
  device = TextConverter(rsrcmgr, tmp_file, codec='utf-8', laparams=LAParams())
  process_pdf(rsrcmgr,device,pdf_file,pagenos=set(),maxpages=2,password='',caching=True,check_extractable=True)

def clean_up_and_lower(title_string):
  '''Remove fancy characters that break things'''
  badchars = ('_','.','!','?')
  for i in badchars:
    title_string = title_string.replace(i,'')
  return title_string.lower()


def guess_title(pdf_text):
  """Tries to guess the title given popular file formats"""
  singles = list(string.ascii_lowercase)
  for x in ['a','i','m','n','e']:
    singles.remove(x)
  # print singles
  bad_title_first_words=[' USA','Proceedings of','LETTER','Journal of','ARTICLE','ar ticle','Communicated by','Communicated_by','anuscript','Public Access',' S ','USENIX','PERSPECTIVES','Brevia','COMMUN ','PHYSICAL REVIEW','Conference','Symantec Research','Symposium','Vol','IEEE','Editor','Published','Permissions','email','doi','Higher-Order Symb Comput','University','no.','Issue','pp.','Society','Report','Dissertation','Thesis','Editor','Association','Computer Science','consideration','publication','faculty','Department','Software Engineering','submission','Monday','Tuesday','Wednesday','Thursday','Friday','Saturday','Sunday','January','February','March','April','June','July','August','September','October','November','December']

  copyright_notice = re.compile(ur'\(?c\)?\S*\s+\d{4}\s+(\w+\s*)+')
  # Using the PyPi regex package, it would be possible to use the
  # Unicode Dash property class rather than the literal en-dash.
  journal_citation = re.compile(ur'\w[\w\s]*\s\d+(\s+\(\d+\))?:\s+\d+((\u2013|-)\d+)?,\s+\d{4}')

  lower_bad_title = [x.lower() for x in bad_title_first_words]

  for line in pdf_text:
    title = clean_up_and_lower(line.strip())
    print title
    print title.split()
    if title.isdigit() or title == '' or len(title.split()) == 1 or any(x in title for x in lower_bad_title) or any(y in title.split() for y in singles) or copyright_notice.match(title) or journal_citation.match(title):
      continue
    break
  else:
    raise ValueError('No title found.')

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
    if next.isdigit() or next == '' or len(next) == 1 or any(x in next for x in bad_title_first_words):
      break
    else:
      rest += (' '+next) 
      t = next.split()

  title = '_'.join((title+rest.lower()).split())
  # Reencode the title into ASCII after normalizing the Unicode.
  return unicodedata.normalize('NFKD', title).encode('ascii','ignore')

def sanitize(title):
  # Remove weird characters that are bad for whilename
  for i in title:
    if not i.isalnum() and i != '_' and i != '-':
      title = title.replace(i,'')
  print title
  return title

def title_rename(title,fn):
  title=sanitize(title)
  os.rename(fn,title+'.pdf')
  print 'Rename of',fn,'complete'
  print 'Title:',title
  return title+'.pdf'

if __name__ == '__main__':
  fn = sys.argv[1]
  with codecs.open(fn,'r','utf-8') as pdf_text:
    title = guess_title(pdf_text)
  if len(sys.argv)>2:
    if sys.argv[2] == '-r':
      title_rename(title,fn)
