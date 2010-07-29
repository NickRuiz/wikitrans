from django.db.transaction import commit_on_success
from django.core.management.base import BaseCommand
from django.core.management.color import no_style
from django.utils.encoding import smart_str

from wt_articles.models import SourceSentence, SourceArticle

import sys
import os
import csv
import re
from optparse import make_option
from datetime import datetime

try:
    set
except NameError:
    from sets import Set as set   # Python 2.3 fallback

def unicode_csv_reader(unicode_csv_data, dialect=csv.excel, **kwargs):
    # Borrowed from Python v.2.6.5 Documentation >> ... >> 13.1 csv
    # csv.py doesn't do Unicode; encode temporarily as UTF-8:
    csv_reader = csv.reader(unicode_csv_data,
                            dialect=dialect, **kwargs)
    for row in csv_reader:
        # decode UTF-8 back to Unicode, cell by cell:
        yield [unicode(cell, 'utf-8') for cell in row]

def run():
    from django.db.models import get_apps
    from django.core import serializers
    from django.db import connection, transaction
    from django.conf import settings
    
    csv_file = '/Users/bahn/Desktop/wikitrans-system/result data sets/Farsi-Batch_191447_result.csv'
    #csv_file = '/Users/bahn/Desktop/wikitrans-system/result data sets/Hindi-Batch_188107_result.csv'
    
    error = False
    if not os.path.exists(csv_file):
        print 'file does not exist'
        sys.exit(0)

    return parse_source_file(csv_file)

@commit_on_success
def parse_source_file(source_file):
    f = open(source_file, 'r')
    csv_reader = unicode_csv_reader(f)
    headers = csv_reader.next()
    header_map = {}
    for i,h in enumerate(headers):
        header_map[h] = i

    l = ["Approve", "Reject", "AssignmentStatus", "ApprovalTime", "AssignmentId", "HITId", "HITTypeId"]
    #===========================================================================
    # status = set()
    #===========================================================================
    for i,line in enumerate(csv_reader):
        for header in sorted(headers):
            index = header_map[header]
            if index < len(line):
                print header, ":", line[index]
            else:
                print header, ": not found"
        break

         #======================================================================
         # for header in l:
         #   index = header_map[header]
         #   if index < len(line):
         #       print header, ":", line[index]
         #   else:
         #       print header, ": not found"
         # if i > 20:
         #   break
         # else:
         #   print "========================================"
         #======================================================================

        #=======================================================================
        # status.add(line[header_map["AssignmentStatus"]])
        #=======================================================================
    #===========================================================================
    # print status
    #===========================================================================
    
run()
