#
#  sources.py
#
#    Convert source code comments to multi-line blocks (library file).
#
#  Copyright 2002-2018 by
#  David Turner.
#
#  This file is part of the FreeType project, and may only be used,
#  modified, and distributed under the terms of the FreeType project
#  license, LICENSE.TXT.  By continuing to use, modify, or distribute
#  this file you indicate that you have read the license and
#  understand and accept it fully.

#
# This library file contains definitions of classes needed to decompose C
# source code files into a series of multi-line `blocks'.  There are two
# kinds of blocks.
#
#   - Normal blocks, which contain source code or ordinary comments.
#
#   - Documentation blocks, which have restricted formatting, and whose text
#     always start with a documentation markup tag like `<Function>',
#     `<Type>', etc.
#
# The routines to process the content of documentation blocks are contained
# in file `content.py'; the classes and methods found here only deal with
# text parsing and basic documentation block extraction.
#


import fileinput, re, string, converter, markdown


################################################################
##
##  SOURCE BLOCK FORMAT CLASS
##
##  A simple class containing compiled regular expressions to detect
##  potential documentation format block comments within C source code.
##
##  The `column' pattern must contain a group to `unbox' the content of
##  documentation comment blocks.
##
##  Later on, paragraphs are converted to long lines, which simplifies the
##  regular expressions that act upon the text.
##
class  SourceBlockFormat:

    def  __init__( self, id, start, column, end ):
        """Create a block pattern, used to recognize special documentation
           blocks."""
        self.id     = id
        self.start  = re.compile( start, re.VERBOSE )
        self.column = re.compile( column, re.VERBOSE )
        self.end    = re.compile( end, re.VERBOSE )


#
# Format 1 documentation comment blocks.
#
#    /************************************/ (at least 2 asterisks)
#    /*                                  */
#    /*                                  */
#    /*                                  */
#    /************************************/ (at least 2 asterisks)
#
start = r'''
  \s*      # any number of whitespace
  /\*{2,}/ # followed by '/' and at least two asterisks then '/'
  \s*$     # probably followed by whitespace
'''

column = r'''
  \s*      # any number of whitespace
  /\*{1}   # followed by '/' and precisely one asterisk
  ([^*].*) # followed by anything (group 1)
  \*{1}/   # followed by one asterisk and a '/'
  \s*$     # probably followed by whitespace
'''

re_source_block_format1 = SourceBlockFormat( 1, start, column, start )


#
# Format 2 documentation comment blocks.
#
#    /************************************ (at least 2 asterisks)
#     *
#     *                                    (1 asterisk)
#     *
#     */                                   (1 or more asterisks)
#
start = r'''
  \s*     # any number of whitespace
  /\*{2,} # followed by '/' and at least two asterisks
  \s*$    # probably followed by whitespace
'''

column = r'''
  \s*           # any number of whitespace
  \*{1}(?![*/]) # followed by precisely one asterisk not followed by `/'
  (.*)          # then anything (group1)
'''

end = r'''
  \s*  # any number of whitespace
  \*+/ # followed by at least one asterisk, then '/'
'''

re_source_block_format2 = SourceBlockFormat( 2, start, column, end )


#
# The list of supported documentation block formats.  We could add new ones
# quite easily.
#
re_source_block_formats = [re_source_block_format1, re_source_block_format2]

################################################################
##
##  SOURCE BLOCK CLASS
##
##  There are two important fields in a `SourceBlock' object.
##
##    self.lines
##      A list of text lines for the corresponding block.
##
##    self.content
##      For documentation comment blocks only, this is the block content
##      that has been `unboxed' from its decoration.  This is `None' for all
##      other blocks (i.e., sources or ordinary comments with no starting
##      markup tag)
##
line_num = 1
class SourceBlock:

    def __init__( self, filename, lineno, lines ):
        global line_num
        self.filename  = filename
        self.lineno    = lineno
        self.lines     = lines[:]
        self.content   = []
        # for i in lines:
        #     print(line_num, i, end='')
        #     line_num += 1


################################################################
##
##  SOURCE PROCESSOR CLASS
##
##  The `SourceProcessor' is in charge of reading a C source file and
##  decomposing it into a series of different `SourceBlock' objects.
##
##  A SourceBlock object consists of the following data.
##
##    - A documentation comment block using one of the layouts above.  Its
##      exact format will be discussed later.
##
##    - Normal sources lines, including comments.
##
##
class  SourceProcessor:

    def  __init__( self, type = 1 ):
        """Initialize a source processor."""
        self.blocks   = []
        self.filename = None
        self.format   = None
        self.lines    = []
        if type == 1:
            self.converter = converter.Converter()
        elif type == 2:
            self.converter = markdown.Markify()
        self.modline = None
    def  reset( self ):
        """Reset a block processor and clean up all its blocks."""
        self.blocks = []
        self.format = None

    def  parse_file( self, filename ):
        """Parse a C source file and add its blocks to the processor's
           list."""
        self.reset()

        self.filename = filename

        fileinput.close()
        self.format = None
        self.lineno = 0
        self.lines  = []
        self.endlineno = 0
        for line in fileinput.input( filename ):
            # strip trailing newlines, important on Windows machines!
            # if line[-1] == '\012':
            #     line = line[0:-1]
            #     print(line)
            # DEBUG
            # print("self.format =", self.format ,line, end ='')
            if self.format == None:
                self.process_normal_line( line )
            else:
                if self.format.end.match( line ):
                    # A normal block end.  Add it to `lines' and create a
                    # new block
                    self.lines.append( line )
                    # DEBUG
                    #print(self.lines)
                    self.endlineno = fileinput.filelineno()
                    # CALL TO REPLACE COMMENT FORMAT
                    self.convert_comment()
                    self.add_block_lines()
                elif self.format.column.match( line ):
                    # A normal column line.  Add it to `lines'.
                    self.lines.append( line )
                else:
                    # An unexpected block end.  Create a new block, but
                    # don't process the line.
                    # DEBUG
                    #print(self.lines)
                    self.endlineno = fileinput.filelineno()
                    # CALL TO REPLACE COMMENT FORMAT
                    self.convert_comment()
                    self.add_block_lines()

                    # we need to process the line again
                    self.process_normal_line( line )

        # record the last lines
        self.add_block_lines()
        return self.blocks

        

    def  process_normal_line( self, line ):
        """Process a normal line and check whether it is the start of a new
           block."""
        for f in re_source_block_formats:
            if f.start.match( line ):
                self.add_block_lines()
                self.format = f
                self.lineno = fileinput.filelineno()

        self.lines.append( line )

    def  add_block_lines( self ):
        """Add the current accumulated lines and create a new block."""
        if self.lines != []:
            block = SourceBlock( self.filename,
                                 self.lineno,
                                 self.lines )

            self.blocks.append( block )
            self.format = None
            self.lines  = []

    def  convert_comment( self ):
        """Get converted comment block and write back to file"""
        if self.lines != []:
            self.lines = self.converter.convert(self.lines)
            #print(''.join(self.lines))

    # debugging only, not used in normal operations
    def  dump( self ):
        """Print all blocks in a processor."""
        for b in self.blocks:
            b.dump()

# eof
