[https://www.sphinx-doc.org/ja/master/usage/advanced/intl.html]

### Make .pot

uv run .\make.bat gettext


### Make .po

uv run sphinx-intl update -p .\build\gettext -l ja


### Build .mo

uv run sphinx-intl build --language ja


### Rebuild docs

uv run sphinx-build -b html .\source .\build\html -D language=ja
