********************
CleanIO Project
********************

CleanIO is a simple project illustrating how to use the yield statement to
make reading and writing text files simple and to remove the clutter and
boilerplate from your mainstream code.

Usage
********

Read a Text File
==================

To read a text file.

    1.  Add an import statement

        ``from CleanIO import CleanRead``

    2.  Create an instance of the ``CleanRead`` class and pass it the desired filename or path

        ``cr = CleanRead(<<file name or path>>)``

    3.  Accept each line of the file from the generator (e.g. with a ``for`` statement) from the ``clean_read`` method

        ``for line in cr.clean_read():``

    4.  When the generator finishes, it will return a ``StopIteration`` exception (which the for statement will handle automatically

The file is opened, read, and closed automatically with no extra boilerplate
needed.

Write a Text File
=====================

To write a text file:

    1.  Add an import statement.

        ``from CleanIO import CleanWrite``

    2.  Create an instance of the ``CleanWrite`` class and pass it the desired filename or path.

        ``cw = CleanWrite(<<file name or path>>)``

    3.  Send each line of the file to the generator via the ``clean_writeline`` method

        ``cw.clean_writeline(<<line>>)``

    4.  When done, notify the generator

        ``cw.clean_close()``

The file is opened, written, and closed automatically with no extra
boilerplate needed.

Comments
=============

-   Read or write as many files as you need.
-   This has not been tested with async calls.
-   This code has been formatted with the ``blue`` library.

Structure
********************
CleanIO consists of two classes, one for reading a text file and one for
writing a text file.

Each class uses the ``yield`` statement for maintaining the position of the
file and its place in the method.  Other "boilerplate" code, such as the
open, starting the generator, and closing is handled automatically in the
class.

Possible Future Enhancements
===============================

There are several possible enhancement to this module that come to mind.

Currently this module is designed to read and write text files.  It
could be enhanced to also read and write binary files.

Currently the CleanWrite class assumes it will be getting one line at a
time (without the newline or '\\n' at the end).  It could be enhanced to
output partial lines or multiple lines at a time if the user desires to put
the line endings on themselves.
