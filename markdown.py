#
#  markdown.py
#
#    Collection of methods to convert text in comment blocks
#    to Markdown
#
#  Copyright 2018 by
#  Nikhil Ramakrishnan.
#
#  This file is part of the FreeType project, and may only be used,
#  modified, and distributed under the terms of the FreeType project
#  license, LICENSE.TXT.  By continuing to use, modify, or distribute
#  this file you indicate that you have read the license and
#  understand and accept it fully.
"""
Collection of methods to convert text in comment blocks
to Markdown as per the Feature Draft at
https://github.com/nikramakrishnan/freetype-docs/wiki/Feature-Draft-of-the-FreeType-Markdown-Documentation

Typical usage:
    import markdown
    converter = markdown.Markify()
    converter.markify(lines)
"""
from __future__ import print_function
import re
try:
    from StringIO import StringIO
except ImportError:
    from io import StringIO

import markdown_utils as mdutils


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
class  DocBlockFormat:

    def  __init__( self, id, start, column, end ):
        """Create a block pattern, used to recognize special documentation
           blocks."""
        self.id     = id
        self.start  = re.compile( start, re.VERBOSE )
        self.column = re.compile( column, re.VERBOSE )
        self.end    = re.compile( end, re.VERBOSE )

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
# This is defined separately to preserve the spaces in
# last line of documentation
end = r'''
  /\*{2,}/ # followed by '/' and at least two asterisks then '/'
  \s*$     # probably followed by whitespace
'''

re_source_old_format = DocBlockFormat( 1, start, column, end )

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
  (\s*           # any number of whitespace
  \*{1})(?![*/]) # followed by precisely one asterisk (group1) not followed by `/'
  (.*)          # then anything (group2)
'''

end = r'''
  \s*  # any number of whitespace
  \*+/ # followed by at least one asterisk, then '/'
'''

re_source_new_format = DocBlockFormat( 2, start, column, end )



old_markup_tag = re.compile( r'''<((?:\w|-)*)>''' )  # <xxxx> format
new_markup_tag = re.compile( r'''\s*@((?:\w|-)*):''' )  # @xxxx: format

#
# A regular expression that stops collection of comments for the current
# block.
#
re_source_sep = re.compile( r'\s*\*\s*' )   #  /* */

re_source_strline = re.compile(r'\/\*')    # /*
re_source_endline = re.compile(r'\*\/')    # */

class Markify:

    def __init__(self):
        self.started = False
        self.tag = None
        self.line = None
        self.ended = False
        self.indent = None
        self.format = None
        self.return_new = True
        self.column_started = False
        self.inside_markup = False
        self.precontent = None
        self.content = None

    def convert(self, lines):
        """Perform conversion of comment blocks to markdown
        
            lines - List containing lines of a comment block
        """
        newlines = []
        # grab the newline character
        self.newlinechar = lines[0][-1]

        for line in lines:
            self.line = line

            if self.format == None:
                # If no format or old comment block format
                if re_source_old_format.start.match(self.line):
                    # If line matches start or end of old comment block
                    self.return_new = False

                    if not self.started:
                        self.indent = len(re.match(r'(\s*)', self.line).group(1))

                elif self.format == None and re_source_new_format.start.match(self.line):
                    # If line matches start of new comment block
                    self.format = 2
                    #Get indent value
                    self.indent = len(re.match(r'(\s*)', self.line).group(1))
                else:
                    pass
            
            else:
                # If it is a normal line
                self.processLine()

            # Push the changed line to list
            newlines.append(self.line)

        # DEBUG
        #print(''.join(newlines))

        if not self.return_new:
            # if it is a special block, return original list
            self.refresh()
            return lines
        # return the changed list
        self.refresh()
        return newlines

    def processLine(self):
        '''Process line and convert to markdown'''
        if self.format == 2 and self.inside_markup:
            m = re.search(re_source_new_format.column, self.line)
            if m:
                # Get the beginning and push rest through markdown checks
                self.precontent = m.group(1)
                self.content = m.group(2)
                #Set the column_started flag
                self.column_started = True

                # handle markup for italic and bold
                self.content = mdutils.emphasis( self.content )

                # more functions bla bla bla




                            
            
            if re_source_old_format.start.match(self.line):
                self.ended = True
                self.inside_markup = False

        if self.format == 2 and re_source_new_format.end.match(self.line):
            self.ended = True
            self.inside_markup = False

        tag_search = re.search(new_markup_tag, self.line)
        if tag_search:
            # If markup tag exists, start a content block 
            self.inside_markup = True
            # content = TagContent()
            # content.tag = tag_search.group(1)

    def refresh(self):
        self.started = False
        self.tag = None
        self.line = None
        self.ended = False
        self.indent = None
        self.format = None
        self.return_new = True
        self.column_started = False
        self.inside_markup = False
        self.precontent = None
        self.content = None

if __name__ == "__main__":
    s = r'''
  /**************************************************************************
   *
   * @Function:
   *   FT_Outline_Get_BBox
   *
   * @Description:
   *   Compute the exact bounding box of an outline.  This is slower
   *   than computing the control box.  However, it uses an *advanced*
   *   algorithm that returns _very_ quickly when the two boxes
   *   coincide.  Otherwise, the outline Bezier arcs are traversed to
   *   extract their extrema.
   *   Also *here* *is* *a* test *line* *with* weird _stuff_
   *   *More* tricky  stuff    *is*      *coming* *your* *way* byatch
   *
   * @Input:
   *   outline :: A pointer to the source outline.
   *
   * @Output:
   *   abbox   :: The outline's exact bounding box.
   *
   * @Return:
   *   FreeType error code.  0~means success.
   *   _Native_ _ClearType_ _Mode_ hello _lol_ ok
   *
   * @Note:
   *   If the font is tricky and the glyph has been loaded with
   *   @FT_LOAD_NO_SCALE, the resulting BBox is meaningless.  To get
   *   reasonable values for the BBox it is necessary to load the glyph
   *   at a large ppem value (so that the hinting instructions can
   *   properly shift and scale the subglyphs), then extracting the BBox,
   *   which can be eventually converted back to font units.
   */
    '''
    lines = []
    s =  StringIO(s)
    for line in s:
        lines.append(line)
    c = Markify()

    newlines = c.convert(lines)

    #print(''.join(newlines))
    