# icalendar documentation build configuration file
import datetime
import os
from importlib.metadata import version

on_rtd = os.environ.get('READTHEDOCS', None) == 'True'

try:
    import sphinx_rtd_theme
    html_theme = 'sphinx_rtd_theme'
    html_theme_path = [sphinx_rtd_theme.get_html_theme_path()]
except ImportError:
    html_theme = 'default'
    if not on_rtd:
        print('-' * 74)
        print('Warning: sphinx-rtd-theme not installed, building with default '
              'theme.')
        print('-' * 74)

extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.coverage',
    'sphinx.ext.viewcode'
]
source_suffix = '.rst'
master_doc = 'index'

project = 'SMS'
this_year = datetime.date.today().year
copyright = f"{this_year}, Andreas Ruppen"
if on_rtd:
    version = '1.1.7'    # noqa: F811
else:
    version = version("seriesManagementSystem")
release = version

exclude_patterns = ['_build', 'lib', 'bin', 'include', 'local']
pygments_style = 'sphinx'

htmlhelp_basename = 'seriesManagementSystem'

man_pages = [
    ('index', 'adnitc', 'adnitc doc',
     ['Andreas Ruppen'], 1)
]
