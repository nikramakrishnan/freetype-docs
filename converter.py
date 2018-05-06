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



old_markup_tag = re.compile( r'''<((?:\w|-)*)>''' )

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
        self.tag_count = 0

    def convert(self, lines):
        """Perform conversion of old comment format to new commnet format
        
            lines - List containing lines of a comment block
        """
        newlines = []

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
                        self.line = re.sub(re_source_endline, '', self.line)
                        self.started = True

                        #Get indent value
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

        if self.tag_count == 0:
            # if there were no tags, return original list
            self.refresh()
            return lines
        self.refresh()
        # return the changed list
        return newlines

    def processLine(self):
        if self.format == 1:
            m = re.search(re_source_old_format.column, self.line)
            if m:
                # If the line is a documentation line
                # Replace /* with * and remove */ from the end
                self.line = re.sub(re_source_strline, ' *',self.line, 1)
                # Replace from the right to avoid touching
                # occurence of */ in comment block
                last_position = self.line.rfind("*/")
                if last_position != -1:
                    self.line = self.line[:last_position] + self.line[last_position+2:]
            
            if re_source_old_format.start.match(self.line):
                # If line matches end of old comment block
                # Replace the last line
                # We match with start because end is tailored
                # to replace it with the new format
                self.line = re.sub(re_source_old_format.end, ' */\n', self.line)
                self.ended = True

        if self.format == 2 and re_source_new_format.end.match(self.line):
            self.ended = True

        if re.search(old_markup_tag, self.line):
            # If markup tag exists, change it to new format 
            self.replaceTag()


    def refresh(self):
        self.started = False
        self.tag = None
        self.line = None
        self.ended = False
        self.indent = None
        self.format = None
        self.tag_count = 0

    def replaceTag(self):
        #print("Old line len = ",len(self.line))
        tags = re.search(old_markup_tag, self.line)
        tagname = tags.group(1)
        newtag = '@' + tagname + ":"
        self.line = self.line[:tags.start()] + newtag + self.line[tags.end():]
        self.tag_count += 1


c = Converter()

c.convert(lines)