#  EPUB Files in the root of the folder will each be treated as books
# Terry Goodkind / Sword of Truth / Vol 1 - 1994 - Wizards First Rule / book.epub
#   author           series                 title                         file

import logging
import os
import shutil
from pathlib import Path

import epub_meta
from ebooklib import epub

from epub_parse.epub import ParseEPUB

logger = logging.getLogger(__name__)

logger.setLevel(logging.INFO)

# ISBNLIBRARY PYTHON


class EpubSorter:
    """
    example:
    sorter = EpubSorter(r"D:\\books", r"D:\\output_book", parsers=["ebooklib", "epub_meta", "lector"], copy_file=False)
    """

    def __init__(
        self,
        books_path,
        output_books_path,
        parsers: list = ["ebooklib", "epub_meta", "lector"],
        copy_file: bool = False,
    ):
        self.books_path = books_path
        self.output_books_path = output_books_path

        self.copy_files = copy_file

        self.parsers = parsers
        self.good_parse = []

        self.file_list = []
        self.file_count = 0

        # GET EPUB FILE LIST
        # MAKE SURE ALL FILES ARE EPUBS
        self.get_epub_files()

        logger.info(f"Found {self.file_count} epub files in {self.books_path}")

    def get_epub_files(self):
        """
        Get all epub files in a directory
        """
        for root, subfolders, filenames in os.walk(self.books_path):
            for bookname in filenames:
                _, ext = os.path.splitext(bookname)
                if (
                    ext in (".epub")
                    and ext not in (".Ds_Store")
                    and not bookname.startswith("._")
                ):
                    full_path = os.path.join(root, bookname)
                    self.file_list.append(full_path)
                    self.file_count += 1

    def start_book_sorter(self):
        """
        takes every file in file_list and gets the epub metadata and creates
        a new path for it based on author and book title
        Terry Goodkind / Wizards First Rule / book.epub
           author           title              file

        """
        print("(+) staring to move files")
        for file in self.file_list:
            metadata = self.get_metadata(file)
            new_path = self.create_new_book_path(metadata, file)

            if not new_path:
                print("BAD PARSE SKIPPING FILE: ", file)

            if self.copy_files:
                self.copy_book_to_path(file, new_path)

            else:
                self.move_book(file, new_path)

        print("(+) done moving files")

    def move_book(self, old_path, new_path):
        """
        Moves book to new Dir
        """
        shutil.move(old_path, new_path)

    def copy_book_to_path(self, old_path, new_path):
        """
        copies book to new path
        """
        shutil.copy(old_path, new_path)

    def create_new_book_path(self, metadata, file):

        if "ebooklib" in self.good_parse:
            data = metadata["ebooklib"]
            title = data["title"]
            author = data["authors"][0]

            if "," in author:
                author_split = author.split(",")

                first = author_split[1]
                # DEAL WITH SPACE AFTER COMMA
                if first[0] == " ":
                    first = first[1:]

                author = first + " " + author_split[0]

            return self.make_dir(author, title, file)

        elif "epub_meta" in self.good_parse:
            data = metadata["epub_meta"]
            title = data["title"]
            author = data["authors"][0]

            return self.make_dir(title, author, file)

        elif "lector" in self.good_parse:
            data = metadata["lector"]

            title = data["title"]
            author = data["authors"]

            return self.make_dir(author, title, file)

        else:
            return False

        # AUTHOR NAME
        # BOOK TITLE
        # BOOK FILE

    def make_dir(self, author, title, file):
        new_path_base = os.path.join(self.output_books_path, author + os.sep + title)

        # file paths with ":" are not valid windows file paths
        # this replaces those with empty space
        new_path_base = self.fix_colons_in_path(new_path_base)

        base_file = os.path.basename(file)

        if not os.path.exists(new_path_base):
            os.makedirs(new_path_base)

        full_path = new_path_base + os.sep + base_file

        return full_path

    def get_metadata(self, filepath):
        """
        Gets metadata from epub files with 3 possible parsers ebooklib, epub_meta, lector
        """

        full_metadata = {}

        # Read using ebooklib
        if "ebooklib" in self.parsers:
            try:
                metadata_1 = epub.read_epub(filepath)

                # try to get metadata
                title = metadata_1.get_metadata("DC", "title")[0][0]
                creator = metadata_1.get_metadata("DC", "creator")[0]
                id = metadata_1.get_metadata("DC", "identifier")
                source = metadata_1.get_metadata("DC", "source")
                description1 = metadata_1.get_metadata("DC", "description")

                full_metadata["ebooklib"] = {
                    "title": title,
                    "authors": creator,
                    "ids": id,
                    "source": source,
                    "description": description1,
                }

                self.good_parse.append("ebooklib")

            except Exception as e:
                logging.info(f"ebooklib: Error reading epub file: {filepath} ")

        if "epub_meta" in self.parsers:
            # Read using epub_meta
            try:
                metadata_2 = epub_meta.get_epub_metadata(filepath)

                title2 = metadata_2.get("title")
                authors2 = metadata_2.get("authors")
                id2 = metadata_2.get("identifiers")
                description2 = metadata_2.get("description")

                full_metadata["epub_meta"] = {
                    "title": title2,
                    "authors": authors2,
                    "ids": id2,
                    "source": None,
                    "description": description2,
                }

                self.good_parse.append("epub_meta")
            except Exception as e:
                logging.info(f"epub_meta: Error reading epub file: {filepath} {e}")

        if "lector" in self.parsers:

            try:

                metadata_3 = ParseEPUB(filepath)
                metadata_3.read_book()
                data = metadata_3.generate_metadata()

                full_metadata["lector"] = {
                    "title": data.title,
                    "authors": data.title,
                    "ids": data.ids,
                }

                self.good_parse.append("lector")
            except Exception as e:
                logging.info(f"lector: Error reading epub file: {filepath} {e}")

        return full_metadata

    def fix_colons_in_path(self, original_name):

        dirnames = Path(original_name).parts

        new_path = dirnames[0]

        for dir in dirnames[1:]:
            if ":" in dir:
                dir = dir.replace(":", "")

            new_path = os.path.join(new_path, dir)

        return new_path


# if __name__ == "__main__":
#     l = EpubSorter(r"/home/Downloads",r"/home/Downloads/sorted")

#     l.start_book_sorter()
