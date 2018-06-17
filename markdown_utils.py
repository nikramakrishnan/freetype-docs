#
#  markdown_utils.py
#
#    Auxiliary functions for the `markdown' tool.
#
#  Copyright 2018 by
#  Nikhil Ramakrishnan.
#
#  This file is part of the FreeType project, and may only be used,
#  modified, and distributed under the terms of the FreeType project
#  license, LICENSE.TXT.  By continuing to use, modify, or distribute
#  this file you indicate that you have read the license and
#  understand and accept it fully.
'''
Contains utility functions for conversion of comment lines/blocks
to markdown.

Typical usage:
    import markdown_utils as mdutils
    mdutils.do_stuff( content )

'''
from __future__ import print_function
import re

# Variables to store field data
inside_field = False
field_indent = 0
cur_lines = []

newlinechar = "\n"

# Variables for code conversion
mode  = 0
mode_none = 0
mode_code = 1
in_code_bock = False
margin = -1
new_delimiter = "```"

#
# Two regular expressions to detect italic and emphasis markup, respectively.
#
# Note that the markup is limited to words consisting of letters, digits,
# the characters `_' and `-', or an apostrophe (but not as the first
# character).
#
# We capture anything after the italics to retain that
# This is *not* dangerous becuase we split the line while processing
re_italic = re.compile( r"_((?:\w|-)(?:\w|'|-)*)_(.*)" )     #  _italic_
re_bold   = re.compile( r"\*((?:\w|-)(?:\w|'|-)*)\*(.*)" )   #  *emphasis*

#
# A regular expression to detect field definitions.
#
# Examples:
#
#   foo     ::
#   foo.bar ::
#
re_field = re.compile( r"""
                         \s*
                           (
                             \w*
                           |
                             \w (\w | \.)* \w
                           )
                         (\s*) ::
                       """, re.VERBOSE )

#
# Regular expressions to detect code sequences.  `Code sequences' are simply
# code fragments embedded in '{' and '}', as demonstrated in the following
# example.
#
#   {
#     x = y + z;
#     if ( zookoo == 2 )
#     {
#       foobar();
#     }
#   }
#
# Note that the indentation of the first opening brace and the last closing
# brace must be exactly the same.  The code sequence itself should have a
# larger indentation than the surrounding braces.
#
re_code_start = re.compile( r"(\s*){\s*$" )
re_code_end   = re.compile( r"(\s*)}\s*$" )

#
# Regular expression to try and recognize code snippets within quotes.
# It looks for a '_' or '.' in the text and categorizes it as an inline
# code block. Manual cleanup may be required
#
re_inline_code   = re.compile( r"(^|\W)`((?:\w| |\.|\*)+(?:(?:\->)|[_.+=])+[\s\w\->_+.=]+)'(\W|$)" )

# Try to find camelCase variable nemes
re_inline_code_2 = re.compile( r"(^|\W)`([a-z|\d]+[A-Z]+(?:[a-z|A-Z|\d]+)?)'(\W|$)" )

re_other_quote = re.compile( r"(^|\W)`(.*?)'(\W|$)" )

# Find new markup tags
new_markup_tag = re.compile( r'''(\s*)@((?:\w|-)*):''' )  # @xxxx: format


def table( precontent, content ):
    '''Convert field entries to lighter syntax'''
    # Get indent value
    indent = len(re.match(r'(\s*)', content).group(1))
    content = convert_table( precontent, content, indent )
    return content

def emphasis( content ):
    '''Convert emphasis (bold and italics) to markdown syntax'''
    content = check_emp( content, 1 )
    content = check_emp( content, 2 )
    return content

def code_block( precontent, content ):
    '''Change code block start and ends
    
    Note that content must be supplied with comment prefixes
    '''
    content, to_add = convert_code_block( precontent, content )
    return content, to_add

def quotes( content ):
    '''Convert inline code snippet quotes to the markdown supported `foo`'''
    line = convert_quotes( content )
    return line

def markup_tags( content ):
    '''Convert markup tags from `@Foo:` to `@foo:`'''
    line = convert_markup_tags( content )
    return line

def convert_table( precontent, content, indent ):
    '''Table converter internal function'''
    global inside_field
    global field_indent
    global newlinechar
    # if nothing changes, we return original string
    new_content = content

    m = re_field.match( content )
    if m:
        # if we find a field definition
        inside_field = True
        # check space between field name and ::
        field_len = len( m.group( 0 ) )
        field_pre = content[:field_len-2]   # The part bofore ::
        field_pre = field_pre.rstrip() + " ::" # fix spaces and add ::

        # Now put the description to the next line
        field_desc = content[field_len:].strip()
        if( len(field_desc) != 0 ):
            field_desc = newlinechar + precontent + " " * (indent + 2) + field_desc
        
        new_content = field_pre + field_desc
        
        # Set field indent
        field_indent = indent
    
    elif inside_field:
        # if we are already inside a field
        if len( content.strip() ) > 0:
            new_content = " " * (field_indent + 2) + content.strip()
    # DEBUG
    # print(new_content)
    return new_content

def end_table( ):
    '''Explicitly signal end of a table field markup'''
    global inside_field
    inside_field = False


def check_emp( content, type = 1 ):
    '''Emphasis converter internal function'''
    if type == 1:
        re_emp = re_bold
        pp_chr = '**'
    elif type == 2:
        re_emp = re_italic
        pp_chr = '_'
    changed = False
    n = re_emp.search( content )
    if n:
        # if we find a emphasis
        emp_started = False
        emphasis = []
        rest = []
        words = content.split(' ')

        for word in words:
            emp_match = re_emp.match( word )

            if emp_match:
                # if the word is emphasis
                if not emp_started:
                    # if emphasis block is not started yet
                    emp_started = True

                text = emp_match.group(1)
                # capture anything attached to match text
                attach = emp_match.group(2).strip()

                # add text to emphasis
                emphasis.append( text )

            elif not emp_match and emp_started:
                # if the emphasis block ends
                if word == '':
                    # if we have multiple spaces continue the block
                    emphasis.append( word )
                    continue
                if len( emphasis ) >= 1:
                    changed = True
                emptext = pp_chr + ' '.join( emphasis ) + pp_chr
                
                # NOTE This is not good, and is not a permanent fix
                # It adds `attach' to end of block instead of
                # with the word it came from
                # NOTE In the specific case of the FreeType header files,
                # fixing this is not required as there is no use case
                # where `attach' is not at the end of block
                if len(attach) > 0:
                    # add to text if there is anything
                    emptext += attach
                    attach = ""
                
                rest.append( emptext )  # append the emphasis block to rest
                rest.append( word )  # append the current word to rest
                emp_started = False # emphasis block is no longer active
                emphasis = []

            else:
                # elif not emp_match and not emp_started
                rest.append( word )

        # Flush last block of emphasis into rest
        if emphasis != []:
            emptext = pp_chr + ' '.join( emphasis ) + pp_chr
            if len(attach) > 0:
                # add to text if there is anything
                emptext += attach
                attach = ""
            rest.append( emptext )

        content = ' '.join( rest )
        # DEBUG
        # if changed:
        #     print(content)
    return content

def convert_code_block( precontent, line ):
    '''Code block converter internal function'''
    
    global mode, mode_none, mode_code, in_code_bock, margin
    global new_delimiter, cur_lines, newlinechar

    # are we parsing a code sequence?
    if mode == mode_code:
        m = re_code_end.match( line )
        if m and len( m.group( 1 ) ) <= margin:
            # that's it, we finished the code sequence
            #code = DocCode( 0, cur_lines )
            #self.items.append( code )
            new_end = precontent + " " * margin + new_delimiter # endline will be added later
            cur_lines += new_end
            ret_lines = cur_lines
            margin    = -1
            cur_lines = ""
            mode      = mode_none
            return ret_lines, 1
        else:
            # otherwise continue the code sequence
            cur_lines += ( precontent + line + newlinechar)
            return None, 2
    else:
        # start of code sequence?
        m = re_code_start.match( line )
        if m:
            # clear current lines
            cur_lines = ""

            # switch to code extraction mode
            margin = len( m.group( 1 ) )
            mode   = mode_code

            # replace current line and add to block
            new_start = " " * margin + new_delimiter + newlinechar
            cur_lines += (new_start)
            return None, 2
        else:
            return None, 0

def convert_quotes( content ):
    '''Quotes converter internal function'''
    # We check if inline code may be present, and add a
    # random sentinel to it, so that it can be replaced
    # later.
    line = re.sub( re_inline_code,
                   r'\g<1>/quot/\g<2>/quot/\g<3>',
                   content )
    line = re.sub( re_inline_code_2,
                   r'\g<1>/quot/\g<2>/quot/\g<3>',
                   line )
    line = re.sub( re_other_quote,
                   r"\1'\2'\3",
                   line )
    # Replace all ` with ' because quotes accross multiple
    # lines cannot be inline code sequences
    line = line.replace( "`", "'" )
    # Replace the /quot/ sentinel with the actual symbol
    line = line.replace( "/quot/", "`" )

    return line

def convert_markup_tags( content ):
    '''Markup tags case internal function'''
    tag = content
    m = new_markup_tag.match( content )
    if m:
        spaces = m.group( 1 )
        text = m.group( 2 )
        text = text.lower()
        tag  = spaces + "@" + text + ":"
    return tag

# eof
