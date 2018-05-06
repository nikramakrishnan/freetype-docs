# freetype-docs
Documentation unification for FreeType

# Introduction
The purpose of this module is to convert the 'heavy' comment documentation format to a 'lighter' version.

## Example
### Old 'heavy' format
```c
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
```

### New 'light' format
```c
/************************************************************************
*
* @Section:
*    gzip
*
* @Title:
*    GZIP Streams
*
* @Abstract:
*    Using gzip-compressed font files.
*
* @Description:
*    This section contains the declaration of Gzip-specific functions.
*
*/
```

# Usage
This module is currently under development, and output is only shown on Terminal. To convert files:
```bash
python docconverter.py file1 [file2 ...]
```

For example, if you want to convert include/freetype/freetype.h:
```bash
python docconverter.py include/freetype/freetype.h
```

# Development
This is in initial stages, and there may be many changes left.

What it does:
  - Converts 'heavy' comments to 'light' comments
  - Preserves (does not change) 'special' comment blocks like [include/freetype/freetype.h#L384](include/freetype/freetype.h#L384)
  - Shows output on the terminal with line numbers
  
What it doesn't do:
  - Write output to file

# License
This module is a part of FreeType Google Summer of Code 2018. All files and code are licensed under the FreeType License.
