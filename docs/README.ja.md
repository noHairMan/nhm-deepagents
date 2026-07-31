# 開発ガイド

[簡体字中国語](/docs/DEVELOPMENT.zh.md)\|[英語](/docs/DEVELOPMENT.en.md)\|[日本語](/docs/DEVELOPMENT.ja.md)\|[繁体中文](/docs/DEVELOPMENT.zh-TW.md)

このドキュメントはプロジェクト開発者および貢献者を対象としており、開発環境、コード構造、品質検査およびテスト方法を紹介します。プロジェクトの背景、インストール、操作、および構成手順については、を参照してください。[お読みください](README.zh.md)。

## 🛠️ テクノロジースタック

-   **言語**:[パイソン](https://www.python.org/)>= 3.14
-   **包管理器**:[紫外線](https://github.com/astral-sh/uv)
-   **APIフレームワーク**:[速い](https://fastapi.tiangolo.com/)
-   **ウェブサーバー**:[ユビコーン](https://www.uvicorn.org/)
-   **エージェントフレームワーク**:[ディープエージェント](https://github.com/zongxuheng/deepagents)(LangGraph/LangChainに基づく)
-   **LLMプロバイダー**:[であること](https://ollama.com/)、[ハグ顔](https://huggingface.co/)そして[人間的](https://www.anthropic.com/)
-   **コードの実行**:[langchain-quickjs](https://github.com/langchain-ai/langchainjs)QuickJSミドルウェア提供
-   **端末のインタラクション**:`asyncclick`、`prompt-toolkit`そして`Rich`
-   **配置管理**:[ピダンティックな設定](https://docs.pydantic.dev/latest/usage/settings/)
-   **コードの品質**:[ラフ](https://github.com/astral-sh/ruff)、`pre-commit`および必須の型ヒント
-   **テストと適用範囲**:`pytest`、`coverage`

## ⚙️CI/CD

このプロジェクトには、以下を含む GitHub Actions ワークフローが統合されています。

-   **テストと適用範囲**: テストを自動的に実行し、コード カバレッジをチェックします。
-   **文書翻訳**： 自動的に`README.zh.md`そして`DEVELOPMENT.zh.md`英語、日本語、繁体字中国語に翻訳されます。
-   **コード仕様**：自動実行`ruff`コード スタイルの一貫性を確保するためにチェックしてフォーマットします。
-   **CIプロセスの最適化**: 関連するコードまたは構成変更に基づいてビルドをトリガーし、不要なビルド タスクを削減します。

## 📜 開発スクリプト

依存関係を同期し、仮想環境を作成します。

```bash
uv sync
```

コードを確認してフォーマットします。

```bash
uv run ruff check . --fix
uv run ruff format .
```

手動で実行する`pre-commit`フック:

```bash
uv run pre-commit run --all-files
```

## 📂 プロジェクトの構造

-   `src/main.py`: Rainy API サービスのメイン エントリ ポイント。
-   `src/fragile/`: 対話型セッション、スラッシュ コマンド、表示および入力処理を含む非同期コマンド ライン クライアント。
-   `src/tomorrow/`: 核心智能体，实现 graph、模型、后端、检查点、存储和生命周期管理。
-   `src/rainy/`: アプリケーションのライフサイクル、チャットインターフェイス、ヘルスチェック、ミドルウェアを実装するための API サービス。
-   `tests/`: テストディレクトリ、構造、および`src`保持一致。
-   `docs/`: 多言語ドキュメント。
-   `pyproject.toml`: プロジェクトのメタデータ、依存関係、およびツール構成。
-   `langgraph.json`:`langgraph-cli`グラフと環境構成。
-   `uv.lock`: 依存関係のバージョンをロックします。

## 🧪 テスト

プロジェクト利用`pytest`テストを実施し、到達するためにテストカバレッジを要求する**100%**。

各モジュールのテストを実行します。

```bash
PYTHONPATH=src TOMORROW_APP=tomorrow uv run pytest tests/tomorrow
PYTHONPATH=src RAINY_APP=rainy uv run pytest tests/rainy
PYTHONPATH=src FRAGILE_APP=fragile uv run pytest tests/fragile
```

完全なカバレッジ テストを実行します。

```bash
PYTHONPATH=src \
TOMORROW_APP=tomorrow \
RAINY_APP=rainy \
FRAGILE_APP=fragile \
uv run coverage run --rcfile=pyproject.toml -m pytest -q && uv run coverage report --rcfile=pyproject.toml
```

テスト文書は次のとおりである必要があります。`src/`モジュールパスは編成され、次のように使用されます。`Test`先頭のテスト クラスはテスト メソッドをラップします。
