import argparse
import os
import re
from docx import Document
from pdfminer.high_level import extract_text

GIGA = 2**30
MEMORY_SIZE = GIGA  # Upper limit of size for loading memory


def entry():
    parser = argparse.ArgumentParser(
        description="Search for a string in files recursively.\nSee https://pypi.org/project/findstring")
    parser.add_argument(
        "search_string",
        help="string to search for in files")
    parser.add_argument(
        '-b',
        '--binary',
        action='store_true',
        help='scan binary files')
    parser.add_argument(
        "-d",
        "--directory",
        nargs="?",
        default=".",
        help="root directory to start searching from (default is current directory)")
    parser.add_argument(
        "-l",
        "--max_length",
        type=int,
        nargs="?",
        default=0,
        help="maximum numbers of characters shown as a result (default is 0 = no limit)")
    parser.add_argument(
        '-t',
        '--text',
        action='store_true',
        help='show matched lines')
    parser.add_argument('-v', '--verbose', action='store_true', help='verbose')

    args = parser.parse_args()

    find_files_with_string(
        args.directory,
        args.search_string,
        max_length=args.max_length,
        verbose=args.verbose,
        show_text=args.text,
        binary=args.binary)

    if args.verbose:
        show('')


def search_string_in_pdf(file_path, search_string,
                         max_length=0, show_text=False, verbose=False):
    if verbose:
        show(file_path)
    try:
        text = extract_text(file_path)
    except Exception as e:
        if verbose:
            print(f"Error reading {file_path}: {e}")
        return
    grep(
        file_path,
        text,
        search_string,
        max_length=max_length,
        show_text=show_text)


def search_string_in_docx(file_path, search_string,
                          max_length=0, show_text=False, verbose=False):
    if verbose:
        show(file_path)
    try:
        doc = Document(file_path)
    except Exception as e:
        if verbose:
            print(f"Error reading {file_path}: {e}")
        return
    for paragraph in doc.paragraphs:
        grep(
            file_path,
            paragraph.text,
            search_string,
            max_length=max_length,
            show_text=show_text)


def find_files_with_string(
        root_dir, search_string, memory_size=MEMORY_SIZE, max_length=0, verbose=False, show_text=False, binary=False):
    if verbose:
        print('Checking directory...\r', end='')
        dirs = os.walk(root_dir)
        len_dirs = sum(1 for _ in dirs)
        count = 0
    for dirpath, _, filenames in os.walk(root_dir):
        if verbose:
            count += 1
            show(f'{count}/{len_dirs}: {dirpath}')
        for filename in filenames:
            file_path = os.path.join(dirpath, filename)
            if filename.lower().endswith('.pdf'):
                search_string_in_pdf(
                    file_path, search_string, max_length=max_length, show_text=show_text, verbose=verbose)
            elif filename.lower().endswith('.docx'):
                search_string_in_docx(
                    file_path, search_string, max_length=max_length, show_text=show_text, verbose=verbose)
            else:
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        while True:
                            text = f.read(memory_size)
                            if not text:
                                break
                            grep(
                                file_path,
                                text,
                                search_string,
                                max_length=max_length,
                                show_text=show_text)
                except Exception:
                    if not binary:
                        continue
                    try:
                        with open(file_path, 'rb') as f:
                            while True:
                                bin = f.read(memory_size)
                                if not bin:
                                    break
                                text = bin.decode('ascii', errors='ignore')
                                grep(
                                    file_path, text, search_string, binary=True)
                    except Exception as e:
                        if verbose:
                            print(f"Error reading {file_path}: {e}")
                        continue


def show(text):
    chars = 79
    showtext = text
    if len(text.encode('utf-8')) > chars:
        showtext = text.encode(
            'utf-8')[:chars - 3].decode('utf-8', 'ignore') + '...'
    print(f'{" "*chars}\r{showtext}\r', end='')


def grep(file_path, text, search_string,
         max_length=0, show_text=False, binary=False):
    if binary:
        if search_string in text:
            print(f'Binary file {file_path} matches.')
        return
    for line in text.splitlines():
        if search_string in line:
            if show_text:
                find_contexts(
                    file_path,
                    line,
                    search_string,
                    max_length=max_length)
            else:
                print(file_path)


def find_contexts(file_path, line, search_string, max_length=0):
    if max_length == 0 or (len(line) <= max_length and len(
            line) < len(search_string) + 10):
        print(f'{file_path}:{line}')
        return
    context_size = (max_length - len(search_string)) // 2
    pattern = re.escape(search_string)
    matches = re.finditer(pattern, line)

    for match in matches:
        start = match.start()
        end = match.end()
        context_start = max(0, start - context_size)
        context_end = min(len(line), end + context_size)
        context = line[context_start:context_end]
        print(f'{file_path}:{context}')
