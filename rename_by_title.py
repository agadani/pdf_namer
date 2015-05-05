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

ENGLISH_WORDS = {
  w.strip() for w in open('/usr/share/dict/words', 'r') if w[0].islower()}
ENGLISH_WORDS.add('parser')
ENGLISH_WORDS.add('combinator')
ENGLISH_WORDS = frozenset(ENGLISH_WORDS)

# Some words are also last names or other proper names, but
# capitalized word appearing in a title should not be misclassified as
# a proper name, so remove those.
PROPER_NAMES = {
  w.strip() for w in open('/usr/share/dict/words', 'r') if
  (w[0].isupper() and w.strip().lower() not in ENGLISH_WORDS)}
PROPER_NAMES.remove('Boolean')
PROPER_NAMES = frozenset(PROPER_NAMES)

BAD_TITLE_WORDS = (
  'usa', 'proceedings', 'letter', 'article', 'ar ticle',
  'communicated by', 'communicated_by', 'manuscript', 'public access',
  'usenix', 'perspectives', 'brevia', 'commun ', 'physical review',
  'conference', 'symantec research', 'symposium', 'vol', 'ieee', 'editor',
  'published', 'permissions', 'higher-order symb comput', 'doi',
  'university', 'no.', 'issue', 'pp.', 'society', 'technical report',
  'tech report', 'dissertation', 'thesis', 'association', 'computer science',
  'consideration', 'publication', 'faculty', 'department',
  'software engineering', 'submission', 'monday', 'tuesday', 'wednesday',
  'thursday', 'friday', 'saturday', 'sunday', 'january', 'february', 'march',
  'april', 'june', 'july', 'august', 'september', 'october', 'november',
  'december', 'journal', 'copyright', 'title', 'uptec', 'oktober',
  'examensarbete', 'siam', 'computing', 'workshop', 'date', 'document number',
  'reply to', 'programming language c', 'email', 'e-mail', 'e mail', 'submitted',
  'functional pearl', 'acta', 'springer', 'verlag', 'elsevier', 'institute',
  'lecture', 'preliminary version', 'monograph', 'supervisor', 'prof', 'dr.',
  'section', 'abstract.', 'edited', 'sciencedirect', 'computer programming',
  'arxiv', 'computational linguistics'
)


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
  # Unfortunately, the spacing isn't always consistent, so I'm going
  # to assume if more than half the words in the string are single
  # characters that it's wrongly spaced.
  if sum(len(w) == 1 for w in title.split()) > len(title.split()) / 2:
    # Use caps to guess the word boundaries.  This is likely wrong but
    # will produce something legible.
    return ' '.join(remove_whitespace.sub('', w)
                    for w in split_on_caps.findall(title))
  else:
    return title

split_words = re.compile(ur"[^\W\d]+|\d+")
copyright_notice = re.compile(ur'\(?c\)?\S*\s+\d{4}\s+(\w+\s*)+')
# journal_citation = re.compile(ur'\w[\w\s]*\s\d+(\s+\(\d+\))?:\s+\d+((\u2013|-)\d+)?,\s+\d{4}')

def bad_title(title, short_word_limit=4):
  split_title = [w for w in split_words.findall(title)
                 if not (len(w) == 1 and w.isdigit())]
  print(split_title)
  print('Bad title word: %s' %
        any(w.lower() in BAD_TITLE_WORDS for w in split_title))
  print('Too many proper names: %s' %
        (3*sum(w.capitalize() in PROPER_NAMES for w in split_title) >=
         len(split_title)))
  print('No long English words: %s' %
        all(w.lower() not in ENGLISH_WORDS or len(w) < short_word_limit or
            w == u'and' for w in split_title))
  print('Copyright notice or journal citation: %s' %
        copyright_notice.match(title)) # or journal_citation.match(title))

  # If it ends with a number, that's probably a page number, year, or
  # some similar number indicating it's not a title.
  return (len(split_title) == 0 or title.lower() == 'by' or
          split_title[-1].isdigit() or
          # If any of these words are present, it's probably not a title.
          any(w in title.lower() for w in BAD_TITLE_WORDS) or
          # If one-third or more of the words are proper names, it's
          # probably an author or institution line.
          3*sum(w.capitalize() in PROPER_NAMES for w in split_title) >=
          len(split_title) or
          # There must be at least one English word longer than some
          # number of letters in the title, not counting 'and'.
          all(w.lower() not in ENGLISH_WORDS or len(w) < short_word_limit or
              w.lower() == 'and' for w in split_title) or
          # Copyright notices aren't titles.
          copyright_notice.match(title)) # or journal_citation.match(title))

split_legible = re.compile(ur"[\w'-]+")

def guess_title(txt_name, codec):
  """Tries to guess the title given popular file formats"""

  with codecs.open(txt_name, 'r', codec) as text_file:
    for line in text_file:
      title = clean_up(line)
      print(title)
      if bad_title(title):
        continue
      break
    else:
      raise TitleError('No title found.')

    print('Good title: %s' % title)
    title = split_legible.findall(title)
    print(title)

    # The test in the original script worked out to always pass
    # provided the last string in the list of strings in the title
    # started with any alphanumeric character.  This worked
    # surprisingly well, which means it's better to err on the side of
    # including lines after the title.  These lines are usually the
    # authors, anyways, which at least is not useless information even
    # if it leads to overlong file names.  One problem here that can't
    # be solved with any simple heuristic is that titles are split
    # with blank lines in between, but blank lines are more reliably
    # the terminator for a title.

    # We think we have the beginning of a title.  If a title ends with
    # a colon or a hyphen or a word starting with a lower-case letter,
    # it's clearly split over lines.  Otherwise, if the next line
    # would be an acceptable title, include it.
    while (title[-1].endswith((':', '-')) or title[-1][0].islower() or
           len(title) < 7):
      line = clean_up(next(text_file))
      if bad_title(line, short_word_limit=2):
        break
      else:
        title += split_legible.findall(line)
        print(title)

  if sum(w.isupper() for w in title) > len(title) // 2:
    title = '_'.join(w.capitalize() for w in title)
  else:
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
