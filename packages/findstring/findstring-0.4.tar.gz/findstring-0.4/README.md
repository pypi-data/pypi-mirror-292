# findstring

This program, `findstring`, allows you to search for a specific string within files in a directory, including support for searching within PDF and DOCX files. It works similarly to the `grep -rI` command but adds the ability to read and search through PDF and DOCX files.

## Usage

```bash
findstring [OPTIONS] search_string
```

## Options

- `search_string`: The string to search for in the files.

### Optional Arguments

- `-b`, `--binary`:  
  Scan binary files as well. If this option is used, the tool will attempt to read binary files and search for the specified string.

- `-d`, `--directory`:  
  Root directory to start searching from. If not specified, the current directory (`.`) is used by default.

- `-l`, `--max_length`:  
  Maximum number of characters to be shown as a result. The default is 0, which means no limit is set.

- `-t`, `--text`:  
  Show the matched lines containing the search string in the output.

- `-v`, `--verbose`:  
  Enable verbose output. The program will provide more detailed information about its operation, including which directories and files are being checked.

## Features

- **PDF Support**:  
  The program can search within PDF files using the `pdfminer` library. It extracts text from the PDF and searches for the specified string.

- **DOCX Support**:  
  DOCX files are also supported, with text extraction handled by the `docx` library.

- **Binary File Scanning**:  
  When the `--binary` flag is enabled, the program will attempt to read binary files and search for the specified string. This is done by decoding the binary content into ASCII.

- **Context Display**:  
  When the `--text` option is enabled, the tool will display the lines containing the search string, with maximum numbers of characters specified by the `--max_length` option. When `--max_length` is specified, `--text` is also enabled.

## Examples

### Search for a string in the current directory

```bash
findstring "example_string"
```

### Search for a string in a specific directory

```bash
findstring -d /path/to/directory "example_string"
```

### Search in binary files

```bash
findstring -b "example_string"
```

### Show matched lines and search with verbose output

```bash
findstring -tv "example_string"
```

### Limit the length of the output text to 50 characters

```bash
findstring -l 50 "example_string"
```

### Highlighting Search Results

The program is configured to highlight matching search results in bold red text by default. This highlighting is controlled by the `GREP_COLORS` environment variable, specifically using the `mt=` option.

If you wish to change the color or style of the highlighted text, you can modify the `mt=` setting in the `GREP_COLORS` environment variable. The `mt=` value is a color code that specifies the style and color used for matching text.

For example:
- **Bold Red (default):** `mt=1;31`
- **Bold Green:** `mt=1;32`
- **Underline Blue:** `mt=4;34`

To apply a custom color, you can set the `GREP_COLORS` environment variable in your shell as follows:

```bash
export GREP_COLORS='mt=1;32'
```

This example would change the highlighted text to bold green.

The program automatically detects if the output is directed to a terminal (TTY). If not, it will print the plain text without any colorization.

## Error Handling

The program will attempt to handle errors such as unreadable files gracefully. If an error occurs while reading a file, the program will skip the file and continue processing the rest, optionally displaying an error message if verbose mode is enabled.
