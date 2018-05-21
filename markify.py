#!/usr/bin/env python
#
#  markify.py
#
#    Entry point to convert comment blocks to markdown.
#    This follows the Feature Draft at
#    https://github.com/nikramakrishnan/freetype-docs/wiki/Feature-Draft-of-the-FreeType-Markdown-Documentation
#
#  Copyright 2018 by
#  Nikhil Ramakrishnan.
#
#  This file is part of the FreeType project, and may only be used,
#  modified, and distributed under the terms of the FreeType project
#  license, LICENSE.TXT.  By continuing to use, modify, or distribute
#  this file you indicate that you have read the license and
#  understand and accept it fully.

from sources   import *
from utils     import *

import utils

import sys, glob, getopt


def  usage():
    print( "Markify Usage information\n" )
    print( "  markify file1 [file2 ...]\n" )
    print( "using the following options:\n" )
    print( "  -h : print this page" )
    print( "  -o : set output directory, as in '-o mydir'" )
    print( "" )
    print( "  --output : same as -o, as in '--output=mydir'" )

def  main( argv ):
    """Main program loop."""

    global output_dir

    try:
        opts, args = getopt.getopt( sys.argv[1:],
                                    "ho:",
                                    ["help", "output="] )
    except getopt.GetoptError:
        usage()
        sys.exit( 2 )

    if args == []:
        usage()
        sys.exit( 1 )

    # process options
    output_dir     = None

    for opt in opts:
        if opt[0] in ( "-h", "--help" ):
            usage()
            sys.exit( 0 )

        if opt[0] in ( "-o", "--output" ):
            utils.output_dir = opt[1]
            utils.flush_to_file = True

    check_output()

    # create context and processor
    source_processor  = SourceProcessor(type = 2)

    # retrieve the list of files to process
    file_list = make_file_list( args )
    for filename in file_list:
        blocks = source_processor.parse_file( filename )
        write_to_file( blocks, filename )
# if called from the command line
if __name__ == '__main__':
    main( sys.argv )

# eof
