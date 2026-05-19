# nhm-deepagents

[簡体字中国語](/docs/README.zh.md)\|[英語](/docs/README.en.md)\|[日本語](/docs/README.ja.md)\|[繁体中文](/docs/README.zh-TW.md)

最新の LLM フレームワークを使用して Deep Agent を構築および実行する Python プロジェクト。

## 🌟プロジェクト概要

`nhm-deepagents`は、ディープ エージェントに焦点を当てたプロフェッショナルな Python プロジェクトです。最新の Python 機能 (3.14 以降) と強力なツールを活用して、AI エージェントの研究とアプリケーションに高品質の開発エクスペリエンスを提供します。

プロジェクトには現在、使用できる心理学の専門家エージェントが含まれています。`deepagents`このフレームワークはユーザー入力を分析し、推奨事項を提供します。

## 🛠️ テクノロジースタック

-   **言語**:[パイソン](https://www.python.org/)>= 3.14
-   **包管理器**:[紫外線](https://github.com/astral-sh/uv)
-   **エージェントフレームワーク**:[ディープエージェント](https://github.com/zongxuheng/deepagents)(LangGraph/LangChainに基づく)
-   **LLMプロバイダー**:[であること](https://ollama.com/)（合格`langchain-ollama`)
-   **配置管理**:[ダイナコンフ](https://www.dynaconf.com/)
-   **コードの品質**:`black`,`isort`,`pre-commit`

## 📋 環境要件

-   **Python 3.14+**
-   **紫外線**: 高速な Python パッケージ インストーラーおよびパーサー。
-   **であること**: 実行中でアクセス可能である必要があります。
-   **LLMモデル**: デフォルトで使用されるモデルは`qwen3.5:9b`。次のコマンドを使用して取得できます。
    ```bash
    ollama pull qwen3.5:9b
    ```

## 🚀 クイックスタート

### インストール

1.  **インストール`uv`**:
    フォローしてください[UV公式倉庫](https://github.com/astral-sh/uv)の指示に従ってください。

2.  **リポジトリのクローンを作成する**:
    ```bash
    git clone <repository-url>
    cd nhm-deepagents
    ```

3.  **依存関係を同期し、仮想環境を作成する**:
    ```bash
    uv sync
    ```

4.  **プリコミットフックをインストールする**:
    ```bash
    uv run pre-commit install
    ```

### アプリケーションを実行する

メイン エントリ ポイントを実行します。

```bash
uv run python src/main.py
```

## ⚙️ 配置

このプロジェクトでは、**ダイナコンフ**構成管理を実行します。設定は次のように定義されています`src/tomorrow/settings.py`、環境変数または`.env`ファイルが上書きされます。

### 環境変数

環境変数にはデフォルトで接頭辞が付けられます`TOMORROW_`始まり。

| 変数                         | 説明する                      | デフォルト値                   |
| -------------------------- | ------------------------- | ------------------------ |
| `TOMORROW_OLLAMA_BASE_URL` | Ollama サービスのベース アドレス      | `http://localhost:11434` |
| `TOMORROW_DEFAULT_MODEL`   | デフォルトで使用される LLM モデル       | `qwen3.5:9b`             |
| `TOMORROW_APP`             | アプリケーション名 (環境変数の接頭辞として使用) | `tomorrow`               |
| `TOMORROW_SETTINGS_MODULE` | モジュールパスを設定する              | `tomorrow.settings`      |

## 📜 脚本

一般的に使用される開発スクリプト:

-   **フォーマットコード**:
    ```bash
    uv run black .
    uv run isort .
    ```

-   **コミット前フックを手動で実行する**:
    ```bash
    uv run pre-commit run --all-files
    ```

## 📂 プロジェクトの構造

-   `src/main.py`: アプリケーションのメイン エントリ ポイント。環境をセットアップし、エージェントを呼び出します。
-   `src/tomorrow/`: コアパッケージディレクトリ。
    -   `core/agent.py`: ディープエージェントとその命令を定義します。
    -   `settings.py`: デフォルトの設定値。
    -   `utils/conf.py`: Dynaconf 初期化ロジック。
    -   `utils/functional.py`: 機能的有用性 (例:`SimpleLazyObject`）。
-   `docs/`: 多言語ドキュメント。
-   `pyproject.toml`: プロジェクトのメタデータ、依存関係、およびツール構成。
-   `uv.lock`: 依存関係のバージョンをロックします。
-   `LICENSE`: Apache ライセンス 2.0。

## 🧪 テスト

-   TODO: 使用`pytest`単体テストと結合テストを実施します。
-   TODO: 自動テスト用の CI プロセスを追加します。

テストの実行 (実装後):

```bash
uv run pytest
```

## 📄ライセンス

このプロジェクトでは、**Apache ライセンス 2.0**ライセンス。詳しくはこちらをご覧ください[ライセンス](LICENSE)書類。
