
import os


def push_file(filename):
    """
    Push a file to a backup location
    if the backup exists push that one eg

    push_file('hello.txt')

    hello.txt will get moved to hello.txt.bak

    if hello.txt.bak exists it will get moved to
    hello.txt.bak.bak
    """
    if not os.path.exists(filename):
        return
    push_file(filename + '.bak')
    os.rename(filename, filename + '.bak')


def pull_file(filename):
    """
    The opposite operation of push_file
    """
    if os.path.exists(filename):
        os.unlink(filename)

    if os.path.exists(filename + '.bak'):
        os.rename(filename + '.bak', filename)
        pull_file(filename + '.bak')
