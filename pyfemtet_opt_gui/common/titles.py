# noinspection PyUnresolvedReferences
from PySide6 import QtWidgets, QtCore, QtGui

# noinspection PyUnresolvedReferences
from PySide6.QtCore import *

# noinspection PyUnresolvedReferences
from PySide6.QtGui import *

# noinspection PyUnresolvedReferences
from PySide6.QtWidgets import *

import os
import enum


__all__ = [
    'PageSubTitles', 'TitledWizardPage',
]


class PageSubTitles(enum.StrEnum):
    initial = ''  # スタートページ。使わない。
    analysis_model = '解析モデル'
    var = 'パラメータ'
    obj = '目的関数'
    cns = '変数拘束式'
    cfg = '実行設定'
    confirm = '確認'  # 使わない？


def get_html_title(sub_title: PageSubTitles):
    return f'現在の項目: {[s for s in PageSubTitles].index(sub_title)}/{len(PageSubTitles) - 1}'


def get_html_subtitle(sub_title: PageSubTitles):

    # settings
    out = ''
    default_color = QApplication.palette().color(QPalette.ColorRole.WindowText)
    enhanced_color = QApplication.palette().color(QPalette.ColorRole.Highlight)

    # get base html
    base_html_path = os.path.join(
        os.path.dirname(__file__),
        'subtitle.html'
    )
    with open(base_html_path, 'r') as f:
        content = f.read()

    # get template region
    header, _, footer = content.split('<!-- SPLITTER -->\n')
    out += header

    # create table element
    for page_name_ in PageSubTitles:

        header_ = "<td align=center valign=top style='padding:0mm 5.4pt 0mm 5.4pt'>"
        footer_ = "</td>"

        # color
        if sub_title == page_name_:
            hex = enhanced_color.name(QColor.NameFormat.HexRgb)
        else:
            hex = default_color.name(QColor.NameFormat.HexRgb)
        page_name__ = page_name_.replace('\n', '<br>')
        html = f"<span style='color:{hex}'>{page_name__}</span>"

        # b, i
        if sub_title == page_name_:
            html = "<b><i>" + html + "</i></b>"

        out += header_
        out += html
        out += footer_

    out += footer

    return out


class TitledWizardPage(QWizardPage):

    @property
    def page_name(self):
        raise NotImplementedError

    def __init__(self, parent=None, _dummy_data=None):
        super().__init__(parent)
        self._dummy_data = _dummy_data

        self.setTitle(get_html_title(self.page_name))
        self.setSubTitle(get_html_subtitle(self.page_name))


if __name__ == '__main__':
    get_html_title(PageSubTitles.var)
