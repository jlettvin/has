#!/usr/bin/env python
import os,sys,re,stat

"""
has.py

A method for finding files containing multiple search items.
Copyright(c) 2013 Jonathan D. Lettvin, All Rights Reserved"

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

__module__     = "has.py"
__author__     = "Jonathan D. Lettvin"
__copyright__  = """\
Copyright(C) 2011 Jonathan D. Lettvin, All Rights Reserved"""
__credits__    = [ "Jonathan D. Lettvin" ]
__license__    = "Unknown"
__version__    = "0.0.3"
__maintainer__ = "Jonathan D. Lettvin"
__email__      = "jlettvin@gmail.com"
__contact__    = "jlettvin@gmail.com"
__status__     = "Demonstration"
__date__       = "20111110"

"""
The Has function implements a search algorithm.
Unlike grep which finds terms within one line.
Has finds files that have all the search terms requested
regardless of position within the file.

In addition, the first time it is run
it produces a "bare" command call "has" which
for posix is called "has" and for windows is called "has.cmd".
This enables the use of a shorter command name in both.
The file is generated in the same directory as has.py
and is preferably a directory on the PATH.
"""

def Has(stream, **kw):
    root = kw.get('root', '')
    expr = kw.get('expr', '')
    look = [[word, re.compile(word)] for word in expr]
    for root, dirs, files in os.walk(root):
        for filename in files:
            pathname = os.path.join(root, filename)
            absent = len(expr)
            try:
                """Allow search to include binary files."""
                with open(pathname, "r+b") as handle:
                    buffer = handle.read()
                    for word, expression in look:
                        """Bypass further search if any word is absent."""
                        if not re.search(expression, buffer):
                            break
                        """Count down absent count for present words."""
                        absent -= 1
            except KeyboardInterrupt:
                """Enable the user to quit at will."""
                raise
            except:
                """Ignore files that cannot be searched."""
                pass
            if not absent:
                stream.write(pathname+'\n')
    return stream

def makeCommand():
    """
    makeCommand() enables sharing between posix and windows.
    On windows, the file 'has.cmd' is to contain special code
    to enable windows to run it as a command rather than script.
    On posix, the file 'has' is to contain ordinary python
    to enable posix to run it as a command rather than script.
    """
    root, ext = os.path.splitext(
            os.path.basename(
                sys.modules['__main__'].__file__))
    directory = os.path.dirname(sys.argv[0])
    filename, content = '', ''

    if os.name == "Windows" or os.name == "nt":
        """Contents of 'has.cmd'"""
        filename = os.path.join(directory, root+".cmd")
        content = """\
@setlocal enableextensions & python -x %~f0 %* & goto :EOF
import has
"""
    elif os.name == "posix":
        """Contents of 'has' python script"""
        filename = os.path.join(directory, root)
        content = """\
#!/usr/bin/env python
import has"""

    if filename:
        """Generate a bare command (without '.py) if absent.'"""
        if not os.path.isfile(filename):
            print "creating command %s" % (filename)
            try:
                """Generate command script."""
                with open(filename, "w") as file:
                    print>>file, content
            except Exception as e:
                print e
                print "Failed to open and write %s (check write permission on %s)" % (
                        filename, directory)
            try:
                """Make command executable."""
                os.chmod(
                        filename,
                        stat.S_IXOTH|stat.S_IXGRP|stat.S_IXUSR|
                        stat.S_IROTH|stat.S_IRGRP|stat.S_IRUSR|
                        stat.S_IWUSR)
            except Exception as e:
                print e
                print "Failed to set executable permissions on %s" % (filename)
    return root

if __name__ == makeCommand() or __name__ == "__main__":
    import io,unittest,StringIO
    from optparse import OptionParser

    script = sys.argv[0]
    root, ext = os.path.splitext(
            os.path.basename(
                sys.modules['__main__'].__file__))
    discard, source = os.path.split(script)

    usage = """\n
Usage: python %s.py [-d directory] re [re ...]
Usage: %s [-d directory] re [re ...] (if found on the PATH)
""" % (script, root)

    class TheTest(unittest.TestCase):
        """No setUp or tearDown are necessary."""
        def test_000(self):
            root = '.'
            expr = ['unittest', 'Has', 'Exception']
            stream = StringIO.StringIO()
            result = Has(stream,root=root,expr=expr).getvalue().strip()
            discard, target = os.path.split(result)
            self.assertEqual(source, target)

    try:
        if sys.version_info < (2, 6):
            raise Exception('Must use python 2.6 or greater', usage)

        argc = len(sys.argv)
        if argc < 2:
            """When no arguments are offered, print usage and run the unit test."""
            print usage, "\nRunning unit tests"
            unittest.main()
        else:
            parser = OptionParser()
            parser.add_option("-d", "--directory", default=".")
            (options, args) = parser.parse_args()

            Has(sys.stdout, root=options.directory, expr=args)
            #Has(sys.stdout, root=sys.argv[1], expr=sys.argv[2:])

    except Exception as e:
        print e
    finally:
        pass
