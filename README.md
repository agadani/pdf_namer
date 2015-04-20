pdf_namer
=========

Renames PDFs and PS files from various sources based on their titles,
and moves them to a given location.  I run this through cron to clean
up my papers directory after I've spent the day downloading
uninformatively named PDFs from USENIX or ACM.

Install
-------

You need to have Python installed.  Compatible with 2.6+ but not
Python 3.  For parsing PDFs, you need either pdftotext, which is a
command-line script distributed as part of Poppler at
http://poppler.freedesktop.org/ or packaged as poppler-utils in most
Linux distros, or Yusuke Shinyama's excellent pdfminer library, which
you can download at https://euske.github.io/pdfminer/ or from PyPi.
(The Debian version is now too old.)  For parsing PS files, you need
pstotext, a command line script from
http://pages.cs.wisc.edu/~ghost/doc/pstotext.htm or distributed by
most distros.

To use, make certain that pmv is executable and place it somewhere in
your executable path.  You will need to either hard code or specify
the location of rename_by_title.py to the script.  That's pretty much
it!

Example
------

avani@gravitas:~/Downloads $ pmv --dir ~/Desktop/To_Read journal.pone.0094346.pdf

Output writing to: /Users/avani/Desktop/To_Read/

Successfully parsed journal.pone.0094346.pdf

Rename of journal.pone.0094346.pdf complete

Title:
Capturing_NaturalColour_3D_Models_of_Insects_for_Species_Discovery_and_Diagnostics
