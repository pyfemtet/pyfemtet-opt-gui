
インストール方法
================


必要な環境
----------
- Python 3.11 ~ 3.13
- Femtet 2023.1 以降（2024.0 以降を推奨）
- Solidworks（Solidworks連携機能を利用する場合のみ必要）


インストール手順
----------------
1. Python のインストール

   - Python 公式サイト（ `https://www.python.org/downloads/ <https://www.python.org/downloads/>`_ ）から適合するバージョンをインストールしてください。
   - `pyfemtet のインストールガイド <https://pyfemtet.readthedocs.io/ja/stable/pages/installation_pages/install_python.html>`_ にも参考情報を記載しています。

2. 必要なパッケージのインストール

   - 自動インストール: `pyfemtet` ドキュメントの `インストールガイド <https://pyfemtet.readthedocs.io/ja/stable/pages/installation_pages/install_pyfemtet.html>`_ 参照
   - またはコマンドプロンプトで以下のコマンドを実行:

     .. code-block:: powershell

        py -m pip install pyfemtet pyfemtet-opt-gui -U --no-warn-script-location

3. Femtet や Solidworks のインストール・ライセンス認証（必要に応じて）


インストールの結果確認
----------------------
1. コマンドプロンプトを開いてください。
2. 以下のコマンドを入力してください。インストールが成功していれば、パッケージ情報が表示されます。

   .. code-block:: powershell

      py -m pip show pyfemtet-opt-gui


