#
#  docmaker.py
#
#    Convert source code markup to HTML documentation.
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
Collection of methods to convert heavy comment blocks 
in the FreeType library to light comment blocks.

Typical usage:
    import converter
    converter = Converter()
    converter.convert(lines)
"""
import re
try:
    from StringIO import StringIO
except ImportError:
    from io import StringIO

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
  \s*           # any number of whitespace
  \*{1}(?![*/]) # followed by precisely one asterisk not followed by `/'
  (.*)          # then anything (group1)
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

class Converter:

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

    def convert(self, lines):
        """Perform conversion of old comment format to new commnet format
        
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
                    self.format = 1

                    if not self.started:
                        # If we're not already in a block
                        # This is to differentiate between the first
                        # and last line of the block
                        self.line = re.sub(re_source_endline, '**', self.line)
                        self.started = True

                        # Get indent value
                        self.indent = len(re.match(r'(\s*)', self.line).group(1))

                        # Check if line ends at column 77 (78 accounts for newline)
                        if len(self.line) != 78:
                            # if not left justify with * and add endline char
                            self.line[:-1].ljust(77,'*') + self.newlinechar
                            

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
        
        if self.format == 1 and not self.ended:
            # if comment block ends abruptly, close it
            endline = ' '*self.indent + ' */\n'

            if re_source_sep.match(newlines[-1]):
                #If previous line is blank, replace it
                newlines[-1] = endline
            else:
                # Otherwise add the comment end block
                newlines.append(endline)
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
        if self.format == 1:
            if re_source_old_format.start.match(self.line) and not self.column_started:
                # if the start line occurrs again this is a special
                # comment block and should be retained
                self.return_new = False

            m = re.search(re_source_old_format.column, self.line)
            if m:
                #Set the column_started flag
                self.column_started = True
                # If the line is a documentation line
                # Replace /* with * and remove */ from the end
                self.line = re.sub(re_source_strline, ' *',self.line, 1)
                # Replace from the right to avoid touching
                # occurence of */ in comment block
                last_position = self.line.rfind("*/")
                if last_position != -1:
                    self.line = self.line[:last_position] + self.line[last_position+2:]
                # Strip spaces from end of line and add the newline character
                self.line = self.line.rstrip() + self.newlinechar
                
                if self.inside_markup:
                    # Start fixing indents if we are inside a markup tag
                    if not re.search(old_markup_tag, self.line) and not re.search(new_markup_tag, self.line):
                        # Check indentation of lines other than ones with markup tags
                        line_groups = re.search(re_source_new_format.column, self.line)
                        line_content = line_groups.group(1)
                        if line_content:
                            # If there is stuff in the line
                            content_indent = len(re.match(r'(\s*)', self.line).group(1))
                            if content_indent > 2:
                                # If the indentation is more than 2, we reduce it by 1
                                space_index = self.line.find(' ', self.indent+2)  # search only after initial indent
                                self.line = self.line[:space_index] + self.line[space_index+1:]

                            
            
            if re_source_old_format.start.match(self.line):
                # If line matches end of old comment block
                # Replace the last line
                # We match with start because end is tailored
                # to replace it with the new format
                self.line = re.sub(re_source_old_format.end, ' */\n', self.line)
                self.ended = True
                self.inside_markup = False

        if self.format == 2 and re_source_new_format.end.match(self.line):
            self.ended = True
            self.inside_markup = False

        if re.search(old_markup_tag, self.line):
            # If markup tag exists, change it to new format 
            self.inside_markup = True
            self.replaceTag()
             


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

    def replaceTag(self):
        #print("Old line len = ",len(self.line))
        tags = re.search(old_markup_tag, self.line)
        tagname = tags.group(1)
        newtag = '@' + tagname + ":"
        self.line = self.line[:tags.start()] + newtag + self.line[tags.end():]

if __name__ == "__main__":
    s = r'''
    /*************************************************************************/
    /*                                                                       */
    /* <Section>                                                             */
    /*    gzip                                                               */
    /*                                                                       */
    /* <Title>                                                               */
    /*    GZIP Streams                                                       */
    /*                                                                       */
    /* <Abstract>                                                            */
    /*    Using gzip-compressed font files.                                  */
    /*                                                                       */
    /* <Description>                                                         */
    /*    This section contains the declaration of Gzip-specific functions.  */
    /*                                                                       */
    /*************************************************************************/
    '''
    lines = []
    s =  StringIO(s)
    for line in s:
        lines.append(line)
    c = Converter()

    newlines = c.convert(lines)

    print(''.join(newlines))
    