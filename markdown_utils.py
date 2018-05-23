#
#  markdown_utils.py
#
#    Auxiliary functions for the `markdown' tool.
#
#  Copyright 2018 by
#  Nikhil Ramakrishnan.
#
#  Modified for use of docconverter
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
import re

# Variables to store field data
inside_field = False
field_indent = 0

#
# Two regular expressions to detect italic and emphasis markup, respectively.
#
# Note that the markup is limited to words consisting of letters, digits,
# the characters `_' and `-', or an apostrophe (but not as the first
# character).
#
# We capture anything after the italics to retain that
# This is *not* dangerous becuase we split the line while fixing
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


def convert_table( precontent, content, indent ):
    '''Table converter internal function'''
    global inside_field
    global field_indent
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
            field_desc = "\n" + precontent + " " * (indent + 2) + field_desc
        
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
                # TODO fix this. It adds `attach' to end of block instead of
                #      with the word it came from
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
            rest.append( emptext )

        content = ' '.join( rest )
        # DEBUG
        # if changed:
        #     print(content)
    return content