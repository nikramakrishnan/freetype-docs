/***************************************************************************/
/*                                                                         */
/*  sfnt.h                                                                 */
/*                                                                         */
/*    High-level `sfnt' driver interface (specification).                  */
/*                                                                         */
/*  Copyright 1996-2018 by                                                 */
/*  David Turner, Robert Wilhelm, and Werner Lemberg.                      */
/*                                                                         */
/*  This file is part of the FreeType project, and may only be used,       */
/*  modified, and distributed under the terms of the FreeType project      */
/*  license, LICENSE.TXT.  By continuing to use, modify, or distribute     */
/*  this file you indicate that you have read the license and              */
/*  understand and accept it fully.                                        */
/*                                                                         */
/***************************************************************************/


#ifndef SFNT_H_
#define SFNT_H_


#include <ft2build.h>
#include FT_INTERNAL_DRIVER_H
#include FT_INTERNAL_TRUETYPE_TYPES_H


FT_BEGIN_HEADER


  /*************************************************************************/
  /*                                                                       */
  /* <FuncType>                                                            */
  /*    TT_Init_Face_Func                                                  */
  /*                                                                       */
  /* <Description>                                                         */
  /*    First part of the SFNT face object initialization.  This finds     */
  /*    the face in a SFNT file or collection, and load its format tag in  */
  /*    face->format_tag.                                                  */
  /*                                                                       */
  /* <Input>                                                               */
  /*    stream     :: The input stream.                                    */
  /*                                                                       */
  /*    face       :: A handle to the target face object.                  */
  /*                                                                       */
  /*    face_index :: The index of the TrueType font, if we are opening a  */
  /*                  collection, in bits 0-15.  The numbered instance     */
  /*                  index~+~1 of a GX (sub)font, if applicable, in bits  */
  /*                  16-30.                                               */
  /*                                                                       */
  /*    num_params :: The number of additional parameters.                 */
  /*                                                                       */
  /*    params     :: Optional additional parameters.                      */
  /*                                                                       */
  /* <Return>                                                              */
  /*    FreeType error code.  0 means success.                             */
  /*                                                                       */
  /* <Note>                                                                */
  /*    The stream cursor must be at the font file's origin.               */
  /*                                                                       */
  /*    This function recognizes fonts embedded in a `TrueType             */
  /*    collection'.                                                       */
  /*                                                                       */
  /*    Once the format tag has been validated by the font driver, it      */
  /*    should then call the TT_Load_Face_Func() callback to read the rest */
  /*    of the SFNT tables in the object.                                  */
  /*                                                                       */
  typedef FT_Error
  (*TT_Init_Face_Func)( FT_Stream      stream,
                        TT_Face        face,
                        FT_Int         face_index,
                        FT_Int         num_params,
                        FT_Parameter*  params );


  /*************************************************************************/
  /*                                                                       */
  /* <FuncType>                                                            */
  /*    TT_Load_Face_Func                                                  */
  /*                                                                       */
  /* <Description>                                                         */
  /*    Second part of the SFNT face object initialization.  This loads    */
  /*    the common SFNT tables (head, OS/2, maxp, metrics, etc.) in the    */
  /*    face object.                                                       */
  /*                                                                       */
  /* <Input>                                                               */
  /*    stream     :: The input stream.                                    */
  /*                                                                       */
  /*    face       :: A handle to the target face object.                  */
  /*                                                                       */
  /*    face_index :: The index of the TrueType font, if we are opening a  */
  /*                  collection, in bits 0-15.  The numbered instance     */
  /*                  index~+~1 of a GX (sub)font, if applicable, in bits  */
  /*                  16-30.                                               */
  /*                                                                       */
  /*    num_params :: The number of additional parameters.                 */
  /*                                                                       */
  /*    params     :: Optional additional parameters.                      */
  /*                                                                       */
  /* <Return>                                                              */
  /*    FreeType error code.  0 means success.                             */
  /*                                                                       */
  /* <Note>                                                                */
  /*    This function must be called after TT_Init_Face_Func().            */
  /*                                                                       */
  typedef FT_Error
  (*TT_Load_Face_Func)( FT_Stream      stream,
                        TT_Face        face,
                        FT_Int         face_index,
                        FT_Int         num_params,
                        FT_Parameter*  params );


  /*************************************************************************/
  /*                                                                       */
  /* <FuncType>                                                            */
  /*    TT_Done_Face_Func                                                  */
  /*                                                                       */
  /* <Description>                                                         */
  /*    A callback used to delete the common SFNT data from a face.        */
  /*                                                                       */
  /* <Input>                                                               */
  /*    face :: A handle to the target face object.                        */
  /*                                                                       */
  /* <Note>                                                                */
  /*    This function does NOT destroy the face object.                    */
  /*                                                                       */
  typedef void
  (*TT_Done_Face_Func)( TT_Face  face );


  /*************************************************************************/
  /*                                                                       */
  /* <FuncType>                                                            */
  /*    TT_Load_Any_Func                                                   */
  /*                                                                       */
  /* <Description>                                                         */
  /*    Load any font table into client memory.                            */
  /*                                                                       */
  /* <Input>                                                               */
  /*    face   :: The face object to look for.                             */
  /*                                                                       */
  /*    tag    :: The tag of table to load.  Use the value 0 if you want   */
  /*              to access the whole font file, else set this parameter   */
  /*              to a valid TrueType table tag that you can forge with    */
  /*              the MAKE_TT_TAG macro.                                   */
  /*                                                                       */
  /*    offset :: The starting offset in the table (or the file if         */
  /*              tag == 0).                                               */
  /*                                                                       */
  /*    length :: The address of the decision variable:                    */
  /*                                                                       */
  /*                If length == NULL:                                     */
  /*                  Loads the whole table.  Returns an error if          */
  /*                  `offset' == 0!                                       */
  /*                                                                       */
  /*                If *length == 0:                                       */
  /*                  Exits immediately; returning the length of the given */
  /*                  table or of the font file, depending on the value of */
  /*                  `tag'.                                               */
  /*                                                                       */
  /*                If *length != 0:                                       */
  /*                  Loads the next `length' bytes of table or font,      */
  /*                  starting at offset `offset' (in table or font too).  */
  /*                                                                       */
  /* <Output>                                                              */
  /*    buffer :: The address of target buffer.                            */
  /*                                                                       */
  /* <Return>                                                              */
  /*    TrueType error code.  0 means success.                             */
  /*                                                                       */
  typedef FT_Error
  (*TT_Load_Any_Func)( TT_Face    face,
                       FT_ULong   tag,
                       FT_Long    offset,
                       FT_Byte   *buffer,
                       FT_ULong*  length );


  /*************************************************************************/
  /*                                                                       */
  /* <FuncType>                                                            */
  /*    TT_Find_SBit_Image_Func                                            */
  /*                                                                       */
  /* <Description>                                                         */
  /*    Check whether an embedded bitmap (an `sbit') exists for a given    */
  /*    glyph, at a given strike.                                          */
  /*                                                                       */
  /* <Input>                                                               */
  /*    face          :: The target face object.                           */
  /*                                                                       */
  /*    glyph_index   :: The glyph index.                                  */
  /*                                                                       */
  /*    strike_index  :: The current strike index.                         */
  /*                                                                       */
  /* <Output>                                                              */
  /*    arange        :: The SBit range containing the glyph index.        */
  /*                                                                       */
  /*    astrike       :: The SBit strike containing the glyph index.       */
  /*                                                                       */
  /*    aglyph_offset :: The offset of the glyph data in `EBDT' table.     */
  /*                                                                       */
  /* <Return>                                                              */
  /*    FreeType error code.  0 means success.  Returns                    */
  /*    SFNT_Err_Invalid_Argument if no sbit exists for the requested      */
  /*    glyph.                                                             */
  /*                                                                       */
  typedef FT_Error
  (*TT_Find_SBit_Image_Func)( TT_Face          face,
                              FT_UInt          glyph_index,
                              FT_ULong         strike_index,
                              TT_SBit_Range   *arange,
                              TT_SBit_Strike  *astrike,
                              FT_ULong        *aglyph_offset );


  /*************************************************************************/
  /*                                                                       */
  /* <FuncType>                                                            */
  /*    TT_Load_SBit_Metrics_Func                                          */
  /*                                                                       */
  /* <Description>                                                         */
  /*    Get the big metrics for a given embedded bitmap.                   */
  /*                                                                       */
  /* <Input>                                                               */
  /*    stream      :: The input stream.                                   */
  /*                                                                       */
  /*    range       :: The SBit range containing the glyph.                */
  /*                                                                       */
  /* <Output>                                                              */
  /*    big_metrics :: A big SBit metrics structure for the glyph.         */
  /*                                                                       */
  /* <Return>                                                              */
  /*    FreeType error code.  0 means success.                             */
  /*                                                                       */
  /* <Note>                                                                */
  /*    The stream cursor must be positioned at the glyph's offset within  */
  /*    the `EBDT' table before the call.                                  */
  /*                                                                       */
  /*    If the image format uses variable metrics, the stream cursor is    */
  /*    positioned just after the metrics header in the `EBDT' table on    */
  /*    function exit.                                                     */
  /*                                                                       */
  typedef FT_Error
  (*TT_Load_SBit_Metrics_Func)( FT_Stream        stream,
                                TT_SBit_Range    range,
                                TT_SBit_Metrics  metrics );


  /*************************************************************************/
  /*                                                                       */
  /* <FuncType>                                                            */
  /*    TT_Load_SBit_Image_Func                                            */
  /*                                                                       */
  /* <Description>                                                         */
  /*    Load a given glyph sbit image from the font resource.  This also   */
  /*    returns its metrics.                                               */
  /*                                                                       */
  /* <Input>                                                               */
  /*    face ::                                                            */
  /*      The target face object.                                          */
  /*                                                                       */
  /*    strike_index ::                                                    */
  /*      The strike index.                                                */
  /*                                                                       */
  /*    glyph_index ::                                                     */
  /*      The current glyph index.                                         */
  /*                                                                       */
  /*    load_flags ::                                                      */
  /*      The current load flags.                                          */
  /*                                                                       */
  /*    stream ::                                                          */
  /*      The input stream.                                                */
  /*                                                                       */
  /* <Output>                                                              */
  /*    amap ::                                                            */
  /*      The target pixmap.                                               */
  /*                                                                       */
  /*    ametrics ::                                                        */
  /*      A big sbit metrics structure for the glyph image.                */
  /*                                                                       */
  /* <Return>                                                              */
  /*    FreeType error code.  0 means success.  Returns an error if no     */
  /*    glyph sbit exists for the index.                                   */
  /*                                                                       */
  /*  <Note>                                                               */
  /*    The `map.buffer' field is always freed before the glyph is loaded. */
  /*                                                                       */
  typedef FT_Error
  (*TT_Load_SBit_Image_Func)( TT_Face              face,
                              FT_ULong             strike_index,
                              FT_UInt              glyph_index,
                              FT_UInt              load_flags,
                              FT_Stream            stream,
                              FT_Bitmap           *amap,
                              TT_SBit_MetricsRec  *ametrics );


  /*************************************************************************/
  /*                                                                       */
  /* <FuncType>                                                            */
  /*    TT_Set_SBit_Strike_Func                                            */
  /*                                                                       */
  /* <Description>                                                         */
  /*    Select an sbit strike for a given size request.                    */
  /*                                                                       */
  /* <Input>                                                               */
  /*    face          :: The target face object.                           */
  /*                                                                       */
  /*    req           :: The size request.                                 */
  /*                                                                       */
  /* <Output>                                                              */
  /*    astrike_index :: The index of the sbit strike.                     */
  /*                                                                       */
  /* <Return>                                                              */
  /*    FreeType error code.  0 means success.  Returns an error if no     */
  /*    sbit strike exists for the selected ppem values.                   */
  /*                                                                       */
  typedef FT_Error
  (*TT_Set_SBit_Strike_Func)( TT_Face          face,
                              FT_Size_Request  req,
                              FT_ULong*        astrike_index );


  /*************************************************************************/
  /*                                                                       */
  /* <FuncType>                                                            */
  /*    TT_Load_Strike_Metrics_Func                                        */
  /*                                                                       */
  /* <Description>                                                         */
  /*    Load the metrics of a given strike.                                */
  /*                                                                       */
  /* <Input>                                                               */
  /*    face          :: The target face object.                           */
  /*                                                                       */
  /*    strike_index  :: The strike index.                                 */
  /*                                                                       */
  /* <Output>                                                              */
  /*    metrics       :: the metrics of the strike.                        */
  /*                                                                       */
  /* <Return>                                                              */
  /*    FreeType error code.  0 means success.  Returns an error if no     */
  /*    such sbit strike exists.                                           */
  /*                                                                       */
  typedef FT_Error
  (*TT_Load_Strike_Metrics_Func)( TT_Face           face,
                                  FT_ULong          strike_index,
                                  FT_Size_Metrics*  metrics );


  /*************************************************************************/
  /*                                                                       */
  /* <FuncType>                                                            */
  /*    TT_Get_PS_Name_Func                                                */
  /*                                                                       */
  /* <Description>                                                         */
  /*    Get the PostScript glyph name of a glyph.                          */
  /*                                                                       */
  /* <Input>                                                               */
  /*    idx  :: The glyph index.                                           */
  /*                                                                       */
  /*    PSname :: The address of a string pointer.  Will be NULL in case   */
  /*              of error, otherwise it is a pointer to the glyph name.   */
  /*                                                                       */
  /*              You must not modify the returned string!                 */
  /*                                                                       */
  /* <Output>                                                              */
  /*    FreeType error code.  0 means success.                             */
  /*                                                                       */
  typedef FT_Error
  (*TT_Get_PS_Name_Func)( TT_Face      face,
                          FT_UInt      idx,
                          FT_String**  PSname );


  /*************************************************************************/
  /*                                                                       */
  /* <FuncType>                                                            */
  /*    TT_Load_Metrics_Func                                               */
  /*                                                                       */
  /* <Description>                                                         */
  /*    Load a metrics table, which is a table with a horizontal and a     */
  /*    vertical version.                                                  */
  /*                                                                       */
  /* <Input>                                                               */
  /*    face     :: A handle to the target face object.                    */
  /*                                                                       */
  /*    stream   :: The input stream.                                      */
  /*                                                                       */
  /*    vertical :: A boolean flag.  If set, load the vertical one.        */
  /*                                                                       */
  /* <Return>                                                              */
  /*    FreeType error code.  0 means success.                             */
  /*                                                                       */
  typedef FT_Error
  (*TT_Load_Metrics_Func)( TT_Face    face,
                           FT_Stream  stream,
                           FT_Bool    vertical );


  /*************************************************************************/
  /*                                                                       */
  /* <FuncType>                                                            */
  /*    TT_Get_Metrics_Func                                                */
  /*                                                                       */
  /* <Description>                                                         */
  /*    Load the horizontal or vertical header in a face object.           */
  /*                                                                       */
  /* <Input>                                                               */
  /*    face     :: A handle to the target face object.                    */
  /*                                                                       */
  /*    vertical :: A boolean flag.  If set, load vertical metrics.        */
  /*                                                                       */
  /*    gindex   :: The glyph index.                                       */
  /*                                                                       */
  /* <Output>                                                              */
  /*    abearing :: The horizontal (or vertical) bearing.  Set to zero in  */
  /*                case of error.                                         */
  /*                                                                       */
  /*    aadvance :: The horizontal (or vertical) advance.  Set to zero in  */
  /*                case of error.                                         */
  /*                                                                       */
  typedef void
  (*TT_Get_Metrics_Func)( TT_Face     face,
                          FT_Bool     vertical,
                          FT_UInt     gindex,
                          FT_Short*   abearing,
                          FT_UShort*  aadvance );


  /*************************************************************************/
  /*                                                                       */
  /* <FuncType>                                                            */
  /*    TT_Load_Colr_Layer_Func                                            */
  /*                                                                       */
  /* <Description>                                                         */
  /*    Load the color layer data given a glyph index.                     */
  /*                                                                       */
  /* <Input>                                                               */
  /*    face       :: The target face object.                              */
  /*                                                                       */
  /*    idx        :: The glyph index.                                     */
  /*                                                                       */
  /* <Output>                                                              */
  /*    layers     :: The layer info with color index and glyph index.     */
  /*                  Deallocate with `FT_FREE'.                           */
  /*                                                                       */
  /*    num_layers :: Number of layers.                                    */
  /*                                                                       */
  /* <Return>                                                              */
  /*    FreeType error code.  0 means success.  Returns an error if no     */
  /*    color layer information exists for `idx'.                          */
  /*                                                                       */
  typedef FT_Error
  (*TT_Load_Colr_Layer_Func)( TT_Face          face,
                              FT_Int           idx,
                              FT_Glyph_Layer  *layers,
                              FT_UShort*       num_layers );


  /*************************************************************************/
  /*                                                                       */
  /* <FuncType>                                                            */
  /*    TT_Blend_Colr_Func                                                 */
  /*                                                                       */
  /* <Description>                                                         */
  /*    Blend the bitmap in `new_glyph' into `base_glyph' using the color  */
  /*    specified by `color_index'.                                        */
  /*                                                                       */
  /*    XXX: Handle foregound color                                        */
  /*                                                                       */
  /* <Input>                                                               */
  /*    face        :: The target face object.                             */
  /*                                                                       */
  /*    color_index :: Color index from the COLR table.                    */
  /*                                                                       */
  /*    base_glyph  :: Slot for bitmap to be merged into.  The underlying  */
  /*                   bitmap may get reallocated.                         */
  /*                                                                       */
  /*    new_glyph   :: Slot to be incooperated into `base_glyph'.          */
  /*                                                                       */
  /* <Return>                                                              */
  /*    FreeType error code.  0 means success.  Returns an error if        */
  /*    color_index is invalid or reallocation fails.                      */
  /*                                                                       */
  typedef FT_Error
  (*TT_Blend_Colr_Func)( TT_Face       face,
                         FT_Int        color_index,
                         FT_GlyphSlot  base_glyph,
                         FT_GlyphSlot  new_glyph );


  /*************************************************************************/
  /*                                                                       */
  /* <FuncType>                                                            */
  /*    TT_Get_Name_Func                                                   */
  /*                                                                       */
  /* <Description>                                                         */
  /*    From the `name' table, return a given ENGLISH name record in       */
  /*    ASCII.                                                             */
  /*                                                                       */
  /* <Input>                                                               */
  /*    face     :: A handle to the source face object.                    */
  /*                                                                       */
  /*    nameid   :: The name id of the name record to return.              */
  /*                                                                       */
  /* <InOut>                                                               */
  /*    name     :: The address of an allocated string pointer.  NULL if   */
  /*                no name is present.                                    */
  /*                                                                       */
  /* <Return>                                                              */
  /*    FreeType error code.  0 means success.                             */
  /*                                                                       */
  typedef FT_Error
  (*TT_Get_Name_Func)( TT_Face      face,
                       FT_UShort    nameid,
                       FT_String**  name );


  /*************************************************************************/
  /*                                                                       */
  /* <FuncType>                                                            */
  /*    TT_Get_Name_ID_Func                                                */
  /*                                                                       */
  /* <Description>                                                         */
  /*    Search whether an ENGLISH version for a given name ID is in the    */
  /*    `name' table.                                                      */
  /*                                                                       */
  /* <Input>                                                               */
  /*    face     :: A handle to the source face object.                    */
  /*                                                                       */
  /*    nameid   :: The name id of the name record to return.              */
  /*                                                                       */
  /* <Out>                                                                 */
  /*    win      :: If non-negative, an index into the `name' table with   */
  /*                the corresponding (3,1) or (3,0) Windows entry.        */
  /*                                                                       */
  /*    apple    :: If non-negative, an index into the `name' table with   */
  /*                the corresponding (1,0) Apple entry.                   */
  /*                                                                       */
  /* <Return>                                                              */
  /*    1 if there is either a win or apple entry (or both), 0 otheriwse.  */
  /*                                                                       */
  typedef FT_Bool
  (*TT_Get_Name_ID_Func)( TT_Face    face,
                          FT_UShort  nameid,
                          FT_Int    *win,
                          FT_Int    *apple );


  /*************************************************************************/
  /*                                                                       */
  /* <FuncType>                                                            */
  /*    TT_Load_Table_Func                                                 */
  /*                                                                       */
  /* <Description>                                                         */
  /*    Load a given TrueType table.                                       */
  /*                                                                       */
  /* <Input>                                                               */
  /*    face   :: A handle to the target face object.                      */
  /*                                                                       */
  /*    stream :: The input stream.                                        */
  /*                                                                       */
  /* <Return>                                                              */
  /*    FreeType error code.  0 means success.                             */
  /*                                                                       */
  /* <Note>                                                                */
  /*    The function uses `face->goto_table' to seek the stream to the     */
  /*    start of the table, except while loading the font directory.       */
  /*                                                                       */
  typedef FT_Error
  (*TT_Load_Table_Func)( TT_Face    face,
                         FT_Stream  stream );


  /*************************************************************************/
  /*                                                                       */
  /* <FuncType>                                                            */
  /*    TT_Free_Table_Func                                                 */
  /*                                                                       */
  /* <Description>                                                         */
  /*    Free a given TrueType table.                                       */
  /*                                                                       */
  /* <Input>                                                               */
  /*    face :: A handle to the target face object.                        */
  /*                                                                       */
  typedef void
  (*TT_Free_Table_Func)( TT_Face  face );


  /*
   * @functype:
   *    TT_Face_GetKerningFunc
   *
   * @description:
   *    Return the horizontal kerning value between two glyphs.
   *
   * @input:
   *    face        :: A handle to the source face object.
   *    left_glyph  :: The left glyph index.
   *    right_glyph :: The right glyph index.
   *
   * @return:
   *    The kerning value in font units.
   */
  typedef FT_Int
  (*TT_Face_GetKerningFunc)( TT_Face  face,
                             FT_UInt  left_glyph,
                             FT_UInt  right_glyph );


  /*************************************************************************/
  /*                                                                       */
  /* <Struct>                                                              */
  /*    SFNT_Interface                                                     */
  /*                                                                       */
  /* <Description>                                                         */
  /*    This structure holds pointers to the functions used to load and    */
  /*    free the basic tables that are required in a `sfnt' font file.     */
  /*                                                                       */
  /* <Fields>                                                              */
  /*    Check the various xxx_Func() descriptions for details.             */
  /*                                                                       */
  typedef struct  SFNT_Interface_
  {
    TT_Loader_GotoTableFunc      goto_table;

    TT_Init_Face_Func            init_face;
    TT_Load_Face_Func            load_face;
    TT_Done_Face_Func            done_face;
    FT_Module_Requester          get_interface;

    TT_Load_Any_Func             load_any;

    /* these functions are called by `load_face' but they can also  */
    /* be called from external modules, if there is a need to do so */
    TT_Load_Table_Func           load_head;
    TT_Load_Metrics_Func         load_hhea;
    TT_Load_Table_Func           load_cmap;
    TT_Load_Table_Func           load_maxp;
    TT_Load_Table_Func           load_os2;
    TT_Load_Table_Func           load_post;

    TT_Load_Table_Func           load_name;
    TT_Free_Table_Func           free_name;

    /* this field was called `load_kerning' up to version 2.1.10 */
    TT_Load_Table_Func           load_kern;

    TT_Load_Table_Func           load_gasp;
    TT_Load_Table_Func           load_pclt;

    /* see `ttload.h'; this field was called `load_bitmap_header' up to */
    /* version 2.1.10                                                   */
    TT_Load_Table_Func           load_bhed;

    TT_Load_SBit_Image_Func      load_sbit_image;

    /* see `ttpost.h' */
    TT_Get_PS_Name_Func          get_psname;
    TT_Free_Table_Func           free_psnames;

    /* starting here, the structure differs from version 2.1.7 */

    /* this field was introduced in version 2.1.8, named `get_psname' */
    TT_Face_GetKerningFunc       get_kerning;

    /* new elements introduced after version 2.1.10 */

    /* load the font directory, i.e., the offset table and */
    /* the table directory                                 */
    TT_Load_Table_Func           load_font_dir;
    TT_Load_Metrics_Func         load_hmtx;

    TT_Load_Table_Func           load_eblc;
    TT_Free_Table_Func           free_eblc;

    TT_Set_SBit_Strike_Func      set_sbit_strike;
    TT_Load_Strike_Metrics_Func  load_strike_metrics;

    TT_Load_Table_Func           load_colr;
    TT_Free_Table_Func           free_colr;
    TT_Load_Colr_Layer_Func      load_colr_layer;
    TT_Blend_Colr_Func           colr_blend;

    TT_Get_Metrics_Func          get_metrics;

    TT_Get_Name_Func             get_name;
    TT_Get_Name_ID_Func          get_name_id;

  } SFNT_Interface;


  /* transitional */
  typedef SFNT_Interface*   SFNT_Service;


#define FT_DEFINE_SFNT_INTERFACE(        \
          class_,                        \
          goto_table_,                   \
          init_face_,                    \
          load_face_,                    \
          done_face_,                    \
          get_interface_,                \
          load_any_,                     \
          load_head_,                    \
          load_hhea_,                    \
          load_cmap_,                    \
          load_maxp_,                    \
          load_os2_,                     \
          load_post_,                    \
          load_name_,                    \
          free_name_,                    \
          load_kern_,                    \
          load_gasp_,                    \
          load_pclt_,                    \
          load_bhed_,                    \
          load_sbit_image_,              \
          get_psname_,                   \
          free_psnames_,                 \
          get_kerning_,                  \
          load_font_dir_,                \
          load_hmtx_,                    \
          load_eblc_,                    \
          free_eblc_,                    \
          set_sbit_strike_,              \
          load_strike_metrics_,          \
          load_colr_,                    \
          free_colr_,                    \
          load_colr_layer_,              \
          colr_blend_,                   \
          get_metrics_,                  \
          get_name_,                     \
          get_name_id_ )                 \
  static const SFNT_Interface  class_ =  \
  {                                      \
    goto_table_,                         \
    init_face_,                          \
    load_face_,                          \
    done_face_,                          \
    get_interface_,                      \
    load_any_,                           \
    load_head_,                          \
    load_hhea_,                          \
    load_cmap_,                          \
    load_maxp_,                          \
    load_os2_,                           \
    load_post_,                          \
    load_name_,                          \
    free_name_,                          \
    load_kern_,                          \
    load_gasp_,                          \
    load_pclt_,                          \
    load_bhed_,                          \
    load_sbit_image_,                    \
    get_psname_,                         \
    free_psnames_,                       \
    get_kerning_,                        \
    load_font_dir_,                      \
    load_hmtx_,                          \
    load_eblc_,                          \
    free_eblc_,                          \
    set_sbit_strike_,                    \
    load_strike_metrics_,                \
    load_colr_,                          \
    free_colr_,                          \
    load_colr_layer_,                    \
    colr_blend_,                         \
    get_metrics_,                        \
    get_name_,                           \
    get_name_id_                         \
  };


FT_END_HEADER

#endif /* SFNT_H_ */


/* END */
