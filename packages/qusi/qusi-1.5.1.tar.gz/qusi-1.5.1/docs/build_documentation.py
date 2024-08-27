from pathlib import Path
from sphinx.application import Sphinx

docs_directory = Path('.').absolute()
configuration_directory = docs_directory.joinpath('source')
source_directory = docs_directory.joinpath('source')
build_directory = docs_directory.joinpath('build')
doctree_directory = build_directory.joinpath('.doctrees')
builder = 'writerside'

app = Sphinx(source_directory, configuration_directory, build_directory, doctree_directory, builder,
             warningiserror=True)
app.build()
