# Freetype-docs Examples
## Docconverter
## Old 'heavy' format
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

## New 'light' format
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

## Markify
## Old format
```c
  /************************************************************************
   * (...)
   * @Fields:
   *   tag     :: Must be `ttc ' to indicate a TrueType collection.
   *
   *   version :: The version number.
   *
   *   count   :: The number of faces in the collection.  The
   *              specification says this should be an unsigned long, but
   *              we use a signed long since we need the value -1 for
   *              specific purposes.
   * (...)
```

## New 'light' format
```c
  /************************************************************************
   * (...)
   * @Fields:
   *   tag ::
   *     Must be `ttc ' to indicate a TrueType collection.
   *
   *   version ::
   *     The version number.
   *
   *   count ::
   *     The number of faces in the collection.  The
   *     specification says this should be an unsigned long, but
   *     we use a signed long since we need the value -1 for
   *     specific purposes.
   * (...)
```
