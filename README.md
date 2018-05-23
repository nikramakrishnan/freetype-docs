# freetype-docs
Documentation unification and Markdown conversion for FreeType

# Introduction
The purpose of this module is to:
* convert the 'heavy' comment documentation format to a 'lighter' version.
* convert comment blocks to FreeType flavored Markdown ([feature draft])

See [EXAMPLES.md](EXAMPLES.md) for examples.

[feature draft]: https://github.com/nikramakrishnan/freetype-docs/wiki/Feature-Draft-of-the-FreeType-Markdown-Documentation

# Usage
This module is currently under development. 

* To change comment formatting:
```bash
python docconverter.py file1 [file2 ...]
```

* To convert to markdown syntax:
```bash
python markify.py file1 [file2 ...]
```

Using the following options:
- -h : print usage information
- -o : set output directory, as in '-o mydir'

**Info**: If `-o` parameter is not specified, output will flush to terminal.

**Note**: Markify will only accept the 'light' comment format. 
It is recommended to run `docconverter` before `markify`.

**Important**: Emphasis (bold and italics) conversion is currently disabled.
This has been done to support the current docmaker.

# Examples
* Change comment formatting  
To change comment formatting of all header files and flush to `./include_mod`:
```bash
python docconverter.py -o ./include_mod ./include/*.h ./include/freetype/*.h ./include/freetype/internal/*.h ./include/freetype/internal/services/*.h ./include/freetype/config/*.h
```

* Convert to markdown  
To convert markdown in all header files and flush to `./include_mark`:
```bash
python markify.py -o ./include_mark ./include_mod/*.h ./include_mod/freetype/*.h ./include_mod/freetype/internal/*.h ./include_mod/freetype/internal/services/*.h ./include_mod/freetype/config/*.h
```

**Note**: Output directory `./include_mod` and `./include_mark` should exist. Any directories inside will be created automatically.

# Development
This is in initial stages, and there may be many changes left.

What it does:
  - Converts 'heavy' comments to 'light' comments
  - Preserves (does not change) 'special' comment blocks like [include/freetype/freetype.h#L384](include/freetype/freetype.h#L384)
  - Shows output on the terminal
  - Converts field entries to new format
  - Converts bold and italics to markdown syntax (**currently disabled**)
  - Write output to file
  
What it doesn't do:
  - Teleport to Andromeda

# License
This module is a part of FreeType Google Summer of Code 2018. All files and code are licensed under the FreeType License.
