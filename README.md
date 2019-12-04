A simple implementation of the getontracks (http://www.getontracks.org/) API to be used with Mutt MUA to efficiently create new todo.
The following macro pipes the entire message to the script for processing. At the moment only the subject is used as description to the new todo.

macro pager ,mt "| /path_to_script/mutt2getontracks.py -t example.com/tracks"
