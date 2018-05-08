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
This module is currently under development. To convert files:
```bash
python docconverter.py file1 [file2 ...]
```

Using the following options:
- -h : print usage information
- -o : set output directory, as in '-o mydir'

**Note**: If `-o` parameter is not specified, output will flush to terminal.

For example, if you want to convert all header files and flush to ./include_mod:
```bash
python docconverter.py -o ./include_mod ./include/*.h ./include/freetype/*.h ./include/freetype/internal/*.h ./include/freetype/internal/services/*.h ./include/freetype/config/*.h
```

**Note**: Output directory `./include_mod` should exist. Any directories inside will be created automatically.

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
