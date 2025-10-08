[https://www.sphinx-doc.org/ja/master/usage/advanced/intl.html]

### Make .pot and .po

uv run sphinx-build -b gettext .\source .\build\gettext
uv run sphinx-intl update -p .\build\gettext --language=en --line-width=-1


### Build .mo

uv run sphinx-intl build --language en


### Rebuild docs

uv run sphinx-build -b html .\source .\build\html -D language=en
