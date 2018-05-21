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

import re
#
# Two regular expressions to detect italic and emphasis markup, respectively.
#
# Note that the markup is limited to words consisting of letters, digits,
# the characters `_' and `-', or an apostrophe (but not as the first
# character).
#
re_italic = re.compile( r"_((?:\w|-)(?:\w|'|-)*)_" )     #  _italic_
re_bold   = re.compile( r"\*((?:\w|-)(?:\w|'|-)*)\*" )   #  *emphasis*

def emphasis( content ):
    content = check_emp( content, 1 )
    content = check_emp( content, 2 )
    return content


def check_emp( content, type = 1 ):
    if type == 1:
        re_emp = re_bold
        pp_chr = '**'
    elif type == 2:
        re_emp = re_italic
        pp_chr = '_'

    n = re_emp.search( content )
    if n:
        # if we find a emphasis
        emp_started = False
        emphasis = []
        rest = []
        words = content.split(' ')

        for word in words:
            bold_match = re_emp.match( word )

            if bold_match:
                # if the word is emphasis
                if not emp_started:
                    # if emphasis block is not started yet
                    emp_started = True

                text = bold_match.group(1)
                emphasis.append( text )

            elif not bold_match and emp_started:
                # if the emphasis block ends
                if word == '':
                    # if we have multiple spaces continue the block
                    emphasis.append( word )
                    continue
                boldtext = pp_chr + ' '.join( emphasis ) + pp_chr
                rest.append( boldtext )  # append the emphasis block to rest
                rest.append( word )  # append the current word to rest
                emp_started = False # emphasis block is no longer active
                emphasis = []

            else:
                # elif not bold_match and not emp_started
                rest.append( word )
        # Flush emphasis into rest
        if emphasis != []:
            boldtext = pp_chr + ' '.join( emphasis ) + pp_chr
            rest.append( boldtext )

        content = ' '.join( rest )
        #content = re.sub(re_bold, r'**\g<1>**',content)
        print(content)
    return content