#
#  utils.py
#
#    Auxiliary functions for the `docmaker' tool (library file).
#
#  Copyright 2002-2018 by
#  David Turner.
#
#  Modified for use of docconverter
#  This file is part of the FreeType project, and may only be used,
#  modified, and distributed under the terms of the FreeType project
#  license, LICENSE.TXT.  By continuing to use, modify, or distribute
#  this file you indicate that you have read the license and
#  understand and accept it fully.

from __future__ import print_function
import string, sys, os, glob, itertools, ntpath


# current output directory
#
output_dir = None

# Decides whether to flush to file or terminal
#
flush_to_file = False


# Divert standard output to a given project documentation file.  Use
# `output_dir' to determine the filename location if necessary and save the
# old stdout handle in a tuple that is returned by this function.
#
def  open_output( filename ):
    global output_dir

    if output_dir and output_dir != "":
        filename = output_dir + os.sep + filename

    old_stdout = sys.stdout
    new_file   = open( filename, "w" )
    sys.stdout = new_file

    return ( new_file, old_stdout )


# Close the output that was returned by `open_output'.
#
def  close_output( output ):
    output[0].close()
    sys.stdout = output[1]


# Check output directory.
#
def  check_output():
    global output_dir
    if output_dir:
        if output_dir != "":
            if not os.path.isdir( output_dir ):
                sys.stderr.write( "argument"
                                  + " '" + output_dir + "' "
                                  + "is not a valid directory\n" )
                sys.exit( 2 )
        else:
            output_dir = None


def  file_exists( pathname ):
    """Check that a given file exists."""
    result = 1
    try:
        file = open( pathname, "r" )
        file.close()
    except:
        result = None
        sys.stderr.write( pathname + " couldn't be accessed\n" )

    return result


def  make_file_list( args = None ):
    """Build a list of input files from command-line arguments."""
    file_list = []
    # sys.stderr.write( repr( sys.argv[1 :] ) + '\n' )

    if not args:
        args = sys.argv[1:]

    for pathname in args:
        if pathname.find('*') >= 0:
            newpath = glob.glob( pathname )
            newpath.sort()  # sort files -- this is important because
                            # of the order of files
        else:
            newpath = [pathname]

        file_list.extend( newpath )

    if len( file_list ) == 0:
        file_list = None
    else:
        # now filter the file list to remove non-existing ones
        file_list = filter( file_exists, file_list )

    return file_list

def create_dirs( filename ):
    """Create directory for a file name if does not exist"""
    global output_dir
    dirname = output_dir + os.sep + os.path.dirname( filename )
    if dirname and not os.path.isdir( dirname ):
        os.makedirs( dirname )
        print("created directory",dirname)

def get_filename( filename ):
    """
    Get the new relative path for a file.
    For example, if the current file is 
    `./include/freetype/freetype.h`,
    this function will return `freetype/freetype.h`
    """
    global output_dir
    filename_norm = os.path.normpath(filename)
    filename_split = filename_norm.split( os.sep )
    new_path_split = filename_split[1:]
    return (os.path.sep).join(new_path_split)


def write_to_file( blocks, filename ):
    """Write list of blocks to file `filename`"""
    line_num = 1
    output = None

    if flush_to_file:
        filename = get_filename( filename )
        create_dirs( filename )
        output = open_output( filename )

    for block in blocks:
        lines = block.lines

        for i in lines:
            # print(line_num, '\t', i, end='', sep='')
            print(i, end='', sep='')
            line_num += 1
    
    if output:
        close_output( output )
# eof
