import webbrowser as _webbrowser
import tempfile as _tempfile
import time as _time
from pathlib import Path as _Path

from IPython import display as _display


def display(content: str, ipython: bool = False, as_md: bool = False):
    if ipython:
        renderer = _display.Markdown if as_md else _display.HTML
        _display.display(renderer(content))
        return
    with _tempfile.NamedTemporaryFile('w', delete=False, suffix='.html') as temp_file:
        temp_file.write(content)
        temp_file.flush()
        temp_filepath = temp_file.name
    _webbrowser.open(f'file://{temp_filepath}')
    _time.sleep(5)
    _Path(temp_filepath).unlink()
    return
