import sys
import io
from stable_world.output import error_output
from stable_world import errors
from stable_world import __version__ as version
from mock import patch

from stable_world.py_helpers import PY3

if PY3:
    StringIO = io.StringIO
else:
    StringIO = io.BytesIO


@patch('stable_world.output.error_output.open')
@patch('click.utils._default_text_stderr')
def test_write_error(default_text_stderr, sw_open):
    stderr_io = default_text_stderr.return_value = StringIO()
    logfile_io = sw_open.return_value = StringIO()
    logfile_io.close = lambda: None

    try:
        raise IOError()
    except IOError:
        exctype, value, traceback = sys.exc_info()
        error_output.write_error_log(exctype, value, traceback)

    sw_open.assert_called_once()

    log = logfile_io.getvalue()

    assert version in log
    assert 'Traceback (most recent call last):' in log
    assert 'IOError' in log

    assert 'Wrote full traceback to' in stderr_io.getvalue()


@patch('click.utils._default_text_stderr')
@patch('stable_world.output.error_output.write_error_log')
def test_brief_excepthook(write_error_log, default_text_stderr):

    stderr_io = default_text_stderr.return_value = StringIO()
    try:
        raise errors.UserError('custom user error')
    except errors.UserError:
        exctype, value, traceback = sys.exc_info()
        error_output.brief_excepthook(exctype, value, traceback)

    assert 'UserError: custom user error' in stderr_io.getvalue()
    write_error_log.assert_not_called()
