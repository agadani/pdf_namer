from __future__ import print_function

import codecs
import os
import re
import sys
import unicodedata

from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.pdfpage import PDFPage
from pdfminer.converter import TextConverter
from pdfminer.layout import LAParams

ENGLISH = {w.strip() for w in open('/usr/share/dict/words', 'r')}

BAD_TITLE_WORDS = {
  ' usa', 'proceedings of', 'letter', 'article', 'ar ticle',
  'communicated by', 'communicated_by', 'anuscript', 'public access',
  'usenix', 'perspectives', 'brevia', 'commun ', 'physical review',
  'conference', 'symantec research', 'symposium', 'vol', 'ieee', 'editor',
  'published', 'permissions', 'higher-order symb comput', 'doi',
  'university', 'no.', 'issue', 'pp.', 'society', 'report', 'dissertation',
  'thesis', 'association', 'computer science', 'consideration',
  'publication', 'faculty', 'department', 'software engineering',
  'submission', 'monday', 'tuesday', 'wednesday', 'thursday', 'friday',
  'saturday', 'sunday', 'january', 'february', 'march', 'april', 'june',
  'july', 'august', 'september', 'october', 'november', 'december', 'journal',
  'copyright', 'title', 'uptec', 'oktober', 'examensarbete', 'siam', 
  'computing', 'workshop', 'date', 'document number', 'reply to',
  'programming language c', 'email', 'e-mail', 'e mail', 'submitted',
  'introduction', 'functional pearl'
}


class TitleError(ValueError):
  '''Raised when a valid title isn't found.'''


def pdf_miner(pdf_file, tmp_file):
  rsrcmgr = PDFResourceManager()
  device = TextConverter(rsrcmgr, tmp_file, codec='utf-8', laparams=LAParams())
  interpreter = PDFPageInterpreter(rsrcmgr, device)
  for page in PDFPage.get_pages(pdf_file, maxpages=2):
      interpreter.process_page(page)

# Using the PyPi regex package, it would be possible to use the
# Unicode capital character class rather than [A-Z] and the Unicode
# Dash property class rather than the literal en-dash in these
# regexes.
remove_bad_chars = re.compile(ur"[^\w\s\-'.:+]")
split_on_caps = re.compile(ur'[A-Z][^A-Z]*')
remove_whitespace = re.compile(ur'\s+')

def clean_up(title):
  title = remove_bad_chars.sub('', title.strip())
  # Some titles end up with bad spacing l i k e t h i s.
  if sum(len(w) == 1 for w in title.split()) > len(title.split()) // 2:
    # Use caps to guess the word boundaries
    return ' '.join(remove_whitespace.sub('', w)
                    for w in split_on_caps.findall(title))
  else:
    return title

split = re.compile(ur"[\w']+")
copyright_notice = re.compile(ur'\(?c\)?\S*\s+\d{4}\s+(\w+\s*)+')
journal_citation = re.compile(ur'\w[\w\s]*\s\d+(\s+\(\d+\))?:\s+\d+((\u2013|-)\d+)?,\s+\d{4}')

def bad_title(title):
  # print(split.findall(title))
  return (title == '' or len(title) == 1 or
          any(x in title for x in BAD_TITLE_WORDS) or
          all(w not in ENGLISH or len(w) < 4 for w in split.findall(title)) or
          copyright_notice.match(title) or journal_citation.match(title))

def guess_title(txt_name, codec):
  """Tries to guess the title given popular file formats"""

  with codecs.open(txt_name, 'r', codec) as text_file:
    for line in text_file:
      title = clean_up(line)
      print(title)
      if bad_title(title.lower()):
        continue
      break
    else:
      raise TitleError('No title found.')

    print('Good title %s' % title)
    title = split.findall(title)
    print(title)

    # We think we have the beginning of a title.  Let's join titles
    # that are obviously split over two lines.
    while (title[-1][-1] == ':' or title[-1][0].islower()):
      line = clean_up(text_file.readline())
      if not bad_title(line.lower()):
        title += split.findall(line)
        print(title)

  title = '_'.join(title)
  # Reencode the title into ASCII after normalizing the Unicode.
  return unicodedata.normalize('NFKD', title).encode('ascii','ignore')

def title_rename(title, fn, extension=''):
  os.rename(fn, title + extension)
  print('Rename of %s complete' % fn)
  print('Title: %s%s' % (title, extension))
  return title + extension

if __name__ == '__main__':
  fn = sys.argv[1]
  with codecs.open(fn, 'r', 'utf-8') as text_file:
    title = guess_title(text_file, 'utf-8')
  if len(sys.argv) > 2:
    if sys.argv[2] == '-r':
      title_rename(title, fn)
