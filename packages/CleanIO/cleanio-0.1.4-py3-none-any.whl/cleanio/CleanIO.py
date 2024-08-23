"""
CleanIO.py - Read or write a text file without the clutter in mainstream code.
"""

__author__ = "Travis Risner"
__project__ = "CleanIOProject"
__creation_date__ = "05/22/2022"
__version__ = "0.1.0"


from os import R_OK, access
from pathlib import Path


class CleanRead:
    """
    CleanRead - Read a text file without the clutter in mainstream code.
    """

    def __init__(self, file_path: Path | str):
        """
        Prepare to read the text file specified.

        :param file_path: filename and optional path to read
        """
        self.filename = file_path
        if isinstance(self.filename, Path):
            self.pathname = self.filename
        else:
            self.pathname = Path(self.filename)
        try:
            self.file_exists = self.pathname.exists()
        except TypeError:
            raise TypeError("file_path must be a string or a pathlike object")
        if not self.file_exists:
            raise OSError(f"File {self.filename} not found.")
        if not self.pathname.is_file():
            raise OSError(f"The name given - {self.filename} - is not a file.")
        if not access(self.pathname, R_OK):
            raise TypeError("File {self.filename} is not readable.")
        return

    def clean_read(self):
        """
        Open and manage reading a text file with a generator.

        :return:
        """
        with open(self.pathname, "rt") as fr:
            while True:
                textline = fr.readline()
                if not textline:
                    break
                text = textline.removesuffix("\n")
                yield text

        return


class CleanWrite:
    """
    CleanWriteClass - Write a text file without the clutter in mainstream code.
    """

    def __init__(self, file_path: Path | str):
        """
        Prepare to write the text file specified.

        :param file_path: filename and optional path to write
        """
        self.filename = file_path
        if isinstance(self.filename, Path):
            self.pathname = self.filename
        else:
            self.pathname = Path(self.filename)
        try:
            self.file_exists = self.pathname.exists()
        except TypeError:
            raise TypeError("file_path must be a string or a pathlike object")
        if self.file_exists:
            raise OSError(f"File {self.filename} already exists.")
        # initialize the generator
        self.write_gen = self._write()
        self.write_gen.__next__()
        return

    def clean_writeline(self, text_line: str):
        """
        Write a line to a text file.

        :param text_line: a line of text to write to the file
        :return:
        """
        line_of_text = text_line + "\n"
        self.write_gen.send(line_of_text)
        return

    def clean_close(self):
        """
        Flush the file buffers and close the file.

        :return:
        """
        self.write_gen.close()

    def _write(self):
        """
        Create and manage a generator to write text to a file.

        :return:
        """
        with open(self.pathname, "wt") as fw:
            while True:
                textline = yield
                fw.write(textline)
        return


if __name__ == "__main__":
    filename = "Selftext.txt"
    filepath: Path = Path(filename)
    filepath.unlink(missing_ok=True)
    cw = CleanWrite(filename)
    cw.clean_writeline("test line")
    cw.clean_close()
    cr = CleanRead(filename)
    for line in cr.clean_read():
        print(line)

# EOF
