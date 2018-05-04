import re, StringIO
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
s = StringIO.StringIO(s)
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
class  SourceBlockFormat:

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

re_source_old_format = SourceBlockFormat( 1, start, column, end )

old_markup_tag = re.compile( r'''<((?:\w|-)*)>''' )

#
# A regular expression that stops collection of comments for the current
# block.
#
re_source_sep = re.compile( r'\s*/\*\s*\*/' )   #  /* */

re_source_strline = re.compile(r'\/\*')    # /*
re_source_endline = re.compile(r'\*\/\h*')    # */

class Converter:

    def __init__(self):
        self.started = False
        self.tag = None
        self.line = None
        self.ended = False
        self.indent = None

    def convert(self, lines):
        newlines = []

        for line in lines:
            self.line = line
            if re_source_old_format.start.match(self.line):
                # If line matches start or end of a comment block
                if not self.started:
                    # If we're not already in a block
                    # This is to differentiate between the first
                    # and last line of the block
                    self.line = re.sub(re_source_endline, '', self.line)
                    self.started = True

                    #Get indent value
                    self.indent = len(re.match(r'(\s*)', self.line).group(1))

                else:
                    # Replace the last line
                    self.line = re.sub(re_source_old_format.end, ' */\n', self.line)
                    self.ended = True
            else:
                # If it is a normal line
                self.processLine()

            # Push the changed line to list
            newlines.append(self.line)
            
        if not self.ended:
            endline = ' */\n'
            newlines.append(endline)

        print(''.join(newlines))

    def processLine(self):
        m = re.search(re_source_old_format.column, self.line)
        if m:
            # If the line is a documentation line
            # Replace /* with * and remove */ from the end
            self.line = re.sub(re_source_strline, ' *',self.line, 1)
            self.line = re.sub(re_source_endline, '', self.line, 1)

        if re.search(old_markup_tag, self.line):
            # If markup tag exists, change it to new format 
            self.replaceTag()

    def replaceTag(self):
        #print("Old line len = ",len(self.line))
        tags = re.search(old_markup_tag, self.line)
        tagname = tags.group(1)
        newtag = '@' + tagname + ":"
        self.line = self.line[:tags.start()] + newtag + self.line[tags.end():]


c = Converter()

c.convert(lines)