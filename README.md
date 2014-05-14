pdf_namer
=========

Renames pdfs from various sources based on their titles, and moves them to a given location.  I run this through cron to clean up my papers directory after I've spent the day downloading uninformatively named pdfs from USENIX or ACM.

Install:
You need to have Python installed. I have tested this on 2.6 +, but not Python3.
You also need Yusuke Shinyama's excellent pdfminer library, which you can
download here: http://www.unixuser.org/~euske/python/pdfminer/

To use, make certain that pmv is executable and place it somewhere in your
executable path.  You will need to either hard code or specify the location of
rename_by_title.py to the script.  That's pretty much it!

Example:

avani@gravitas:~/Downloads $ pmv --dir ~/Desktop/To_Read journal.pone.0094346.pdf

Output writing to: /Users/avani/Desktop/To_Read/

Successfully parsed journal.pone.0094346.pdf

Rename of journal.pone.0094346.pdf complete

Title:
Capturing_NaturalColour_3D_Models_of_Insects_for_Species_Discovery_and_Diagnostics
