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
    converter.markify( lines )
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
        """Create a block pattern, used to recognize documentation
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
        

class Markify:

    def __init__(self):
        self.started = False
        self.line = None
        self.ended = False
        self.indent = None
        self.format = None
        self.return_new = True
        self.column_started = False
        self.inside_markup = False
        self.precontent = None
        self.content = None
        self.in_code = False
        mdutils.end_table()



    def convert(self, lines):
        """Perform conversion of comment blocks to markdown
        
            lines - List containing lines of a comment block
        """
        newlines = []
        # grab the newline character
        self.newlinechar = lines[0][-1]
        # set newlinechar in mdutils
        mdutils.newlinechar = self.newlinechar

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

        tag_search = re.search(new_markup_tag, self.line)
        if tag_search:
            # If markup tag exists, start a content block 
            self.inside_markup = True
            mdutils.end_table()

        if self.format == 2 and self.inside_markup:
            m = re.search(re_source_new_format.column, self.line)
            if m:
                # Get the beginning and push rest through markdown checks
                self.precontent = m.group(1)
                self.content = m.group(2)
                self.content = self.content.rstrip()
                # Set the column_started flag
                self.column_started = True

                #########################################
                # Italics and Bold
                #########################################
                # handle markup for italic and bold
                if not self.in_code:
                    # If not in a code block
                    self.content = mdutils.emphasis( self.content )
                    self.line = self.precontent + self.content + self.newlinechar

                #########################################
                # Field entries
                #########################################
                # handle markup for field entries
                if not self.in_code:
                    # If not in a code block
                    self.content = mdutils.table( self.precontent, self.content )
                    self.line = self.precontent + self.content + self.newlinechar

                #########################################
                # Quotes
                #########################################
                # handle markup for quotes
                if not self.in_code:
                    # If not in a code block
                    self.content = mdutils.quotes( self.content )
                    self.line = self.precontent + self.content + self.newlinechar

                #########################################
                # Markup Tags case
                #########################################
                # lowercase markup tags
                if not self.in_code:
                    # If not in a code block
                    self.content = mdutils.markup_tags( self.content )
                    self.line = self.precontent + self.content + self.newlinechar

                #########################################
                # Code Blocks
                #########################################
                # handle markup for code blocks
                self.content, to_add = mdutils.code_block( self.precontent, self.content )
                if to_add == 1:
                    # Code block ended, we can add the line
                    self.line = self.precontent + self.content + self.newlinechar
                    self.in_code = False
                elif to_add == 2:
                    # We are in a code block, so don't add anything
                    self.line = ""
                    self.in_code = True
                # Otherwise self.line remains untouched

        if self.format == 2 and re_source_new_format.end.match(self.line):
            self.ended = True
            self.inside_markup = False

    def refresh(self):
        self.started = False
        self.line = None
        self.ended = False
        self.indent = None
        self.format = None
        self.return_new = True
        self.column_started = False
        self.inside_markup = False
        self.precontent = None
        self.content = None
        self.markup_status = 0
        self.in_code = False
        mdutils.end_table()

if __name__ == "__main__":
    s = r'''
  /**************************************************************************
   *
   * @Struct:
   *   FT_FaceRec
   *
   * @Description:
   *   FreeType root face class structure.  A face object models a
   *   typeface in a font file.
   *   Hello *this* *is*: _Something'_ _special_
   *
   * @Fields:
   *   num_faces           :: The number of faces in the font file.  Some
   *                          font formats can have multiple faces in
   *                          a single font file.
   *
   *   face_index          :: This field holds two different values.
   *                          Bits 0-15 are the index of the face in the
   *                          font file (starting with value~0).  They
   *                          are set to~0 if there is only one face in
   *                          the font file.
   *
   *                          [Since 2.6.1] Bits 16-30 are relevant to GX
   *                          and OpenType variation fonts only, holding
   *                          the named instance index for the current
   *                          face index (starting with value~1; value~0
   *                          indicates font access without a named
   *                          instance).  For non-variation fonts, bits
   *                          16-30 are ignored.  If we have the third
   *                          named instance of face~4, say, `face_index'
   *                          is set to 0x00030004.
   *
   *                          Bit 31 is always zero (this is,
   *                          `face_index' is always a positive value).
   *
   *                          [Since 2.9] Changing the design coordinates
   *                          with @FT_Set_Var_Design_Coordinates or
   *                          @FT_Set_Var_Blend_Coordinates does not
   *                          influence the named instance index value
   *                          (only @FT_Set_Named_Instance does that).
   *
   *   face_flags          :: A set of bit flags that give important
   *                          information about the face; see
   *                          @FT_FACE_FLAG_XXX for the details.
   *
   *   style_flags         :: The lower 16~bits contain a set of bit
   *                          flags indicating the style of the face; see
   *                          @FT_STYLE_FLAG_XXX for the details.
   *
   *                          [Since 2.6.1] Bits 16-30 hold the number
   *                          of named instances available for the
   *                          current face if we have a GX or OpenType
   *                          variation (sub)font.  Bit 31 is always zero
   *                          (this is, `style_flags' is always a
   *                          positive value).  Note that a variation
   *                          font has always at least one named
   *                          instance, namely the default instance.
   *
   *   num_glyphs          :: The number of glyphs in the face.  If the
   *                          face is scalable and has sbits (see
   *                          `num_fixed_sizes'), it is set to the number
   *                          of outline glyphs.
   *
   *                          For CID-keyed fonts (not in an SFNT
   *                          wrapper) this value gives the highest CID
   *                          used in the font.
   *
   *   family_name         :: The face's family name.  This is an ASCII
   *                          string, usually in English, that describes
   *                          the typeface's family (like `Times New
   *                          Roman', `Bodoni', `Garamond', etc).  This
   *                          is a least common denominator used to list
   *                          fonts.  Some formats (TrueType & OpenType)
   *                          provide localized and Unicode versions of
   *                          this string.  Applications should use the
   *                          format specific interface to access them.
   *                          Can be NULL (e.g., in fonts embedded in a
   *                          PDF file).
   *
   *                          In case the font doesn't provide a specific
   *                          family name entry, FreeType tries to
   *                          synthesize one, deriving it from other name
   *                          entries.
   *
   *   style_name          :: The face's style name.  This is an ASCII
   *                          string, usually in English, that describes
   *                          the typeface's style (like `Italic',
   *                          `Bold', `Condensed', etc).  Not all font
   *                          formats provide a style name, so this field
   *                          is optional, and can be set to NULL.  As
   *                          for `family_name', some formats provide
   *                          localized and Unicode versions of this
   *                          string.  Applications should use the format
   *                          specific interface to access them.
   *
   *   num_fixed_sizes     :: The number of bitmap strikes in the face.
   *                          Even if the face is scalable, there might
   *                          still be bitmap strikes, which are called
   *                          `sbits' in that case.
   *
   *   available_sizes     :: An array of @FT_Bitmap_Size for all bitmap
   *                          strikes in the face.  It is set to NULL if
   *                          there is no bitmap strike.
   *
   *                          Note that FreeType tries to sanitize the
   *                          strike data since they are sometimes sloppy
   *                          or incorrect, but this can easily fail.
   *
   *   num_charmaps        :: The number of charmaps in the face.
   *
   *   charmaps            :: An array of the charmaps of the face.
   *
   *   generic             :: A field reserved for client uses.  See the
   *                          @FT_Generic type description.
   *
   *   bbox                :: The font bounding box.  Coordinates are
   *                          expressed in font units (see
   *                          `units_per_EM').  The box is large enough
   *                          to contain any glyph from the font.  Thus,
   *                          `bbox.yMax' can be seen as the `maximum
   *                          ascender', and `bbox.yMin' as the `minimum
   *                          descender'.  Only relevant for scalable
   *                          formats.
   *
   *                          Note that the bounding box might be off by
   *                          (at least) one pixel for hinted fonts.  See
   *                          @FT_Size_Metrics for further discussion.
   *
   *   units_per_EM        :: The number of font units per EM square for
   *                          this face.  This is typically 2048 for
   *                          TrueType fonts, and 1000 for Type~1 fonts.
   *                          Only relevant for scalable formats.
   *
   *   ascender            :: The typographic ascender of the face,
   *                          expressed in font units.  For font formats
   *                          not having this information, it is set to
   *                          `bbox.yMax'.  Only relevant for scalable
   *                          formats.
   *
   *   descender           :: The typographic descender of the face,
   *                          expressed in font units.  For font formats
   *                          not having this information, it is set to
   *                          `bbox.yMin'.  Note that this field is
   *                          negative for values below the baseline.
   *                          Only relevant for scalable formats.
   *
   *   height              :: This value is the vertical distance
   *                          between two consecutive baselines,
   *                          expressed in font units.  It is always
   *                          positive.  Only relevant for scalable
   *                          formats.
   *
   *                          If you want the global glyph height, use
   *                          `ascender - descender'.
   *
   *   max_advance_width   :: The maximum advance width, in font units,
   *                          for all glyphs in this face.  This can be
   *                          used to make word wrapping computations
   *                          faster.  Only relevant for scalable
   *                          formats.
   *
   *   max_advance_height  :: The maximum advance height, in font units,
   *                          for all glyphs in this face.  This is only
   *                          relevant for vertical layouts, and is set
   *                          to `height' for fonts that do not provide
   *                          vertical metrics.  Only relevant for
   *                          scalable formats.
   *
   *   underline_position  :: The position, in font units, of the
   *                          underline line for this face.  It is the
   *                          center of the underlining stem.  Only
   *                          relevant for scalable formats.
   *
   *   underline_thickness :: The thickness, in font units, of the
   *                          underline for this face.  Only relevant for
   *                          scalable formats.
   *
   *   glyph               :: The face's associated glyph slot(s).
   *
   *   size                :: The current active size for this face.
   *
   *   charmap             :: The current active charmap for this face.
   *
   * @Note:
   *   Fields may be changed after a call to @FT_Attach_File or
   *   @FT_Attach_Stream.
   *
   *   For an OpenType variation font, the values of the following fields
   *   can change after a call to @FT_Set_Var_Design_Coordinates (and
   *   friends) if the font contains an `MVAR' table: `ascender',
   *   `descender', `height', `underline_position', and
   *   `underline_thickness'.
   *
   *   Especially for TrueType fonts see also the documentation for
   *   @FT_Size_Metrics.
   */
    '''
    lines = []
    s =  StringIO(s)
    for line in s:
        lines.append(line)
    c = Markify()

    newlines = c.convert(lines)

    print(''.join(newlines))

# eof
