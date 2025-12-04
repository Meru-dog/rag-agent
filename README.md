# ドキュメント検索・要約エージェント（Backend）

FastAPI + Chroma + OpenAI を使った、シンプルな RAG バックエンドです。
`documents/` 配下のテキスト文書をインデックスし、質問に関連する箇所を検索して回答を生成します。

---

## 1. 構成概要

* フレームワーク: FastAPI
* ベクトルストア: Chroma (PersistentClient)
* LLM / Embedding: OpenAI API
* 主な機能:

  * `documents/` から文書を読み込む
  * 文書をチャンク化して Chroma に登録する
  * 質問に対して類似チャンクを検索する
  * 検索結果をコンテキストにして LLM で回答を生成する
  * `/api/ask` で回答と参照文書を返す

---

## 2. ディレクトリ構造

```text
backend/
├─ app/
│  ├─ main.py            # FastAPI エントリポイント（/api/ask, /health）
│  ├─ config.py          # 設定（パス、モデル名、APIキー読み込み）
│  └─ rag/
│     ├─ document_loader.py  # documents/ から文書を読み込む
│     ├─ index_builder.py    # 文書 → チャンク → Chroma へ登録
│     ├─ retriever.py        # 質問 → 類似チャンクを取得
│     └─ llm_client.py       # 類似チャンクを元に LLM で回答生成
│
├─ documents/             # 検索対象文書（.txt / .md）
│  ├─ sample1.txt
│  └─ ...
│
├─ scripts/
│  └─ build_index.py      # インデックス作成スクリプト
│
├─ chroma_db/             # Chroma の永続化データ（生成される）
├─ requirements.txt
├─ .env                   # OPENAI_API_KEY など（Git 管理外）
└─ README.md              # このファイル
```

---

## 3. セットアップ

### 3.1 依存ライブラリインストール

```bash
cd backend

python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

pip install -r requirements.txt
```

### 3.2 環境変数 (.env)

`backend/.env` に OpenAI の API キーを設定します。

```env
OPENAI_API_KEY=sk-xxxxxxx...
```

---

## 4. 文書の準備とインデックス作成

### 4.1 文書の配置

`backend/documents/` フォルダに `.txt` や `.md` ファイルを配置します。

例:

```text
backend/documents/
├─ contract_memo.txt
└─ rag_notes.md
```

### 4.2 インデックス作成

以下のコマンドで、文書のチャンク化と Chroma への登録を行います。

```bash
cd backend
source .venv/bin/activate

python scripts/build_index.py
```

実行が成功すると、コンソールに次のようなメッセージが表示されます。

```text
インデックス作成完了: XX チャンクを登録しました。
```

`backend/chroma_db/` 配下に Chroma のデータが生成されます。

---

## 5. サーバー起動と動作確認

### 5.1 FastAPI サーバー起動

```bash
cd backend
source .venv/bin/activate

uvicorn app.main:app --reload --port 8000
```

### 5.2 ヘルスチェック

ブラウザで以下にアクセスします。

* `http://localhost:8000/health`

`{"status": "ok"}` が返れば起動成功です。

### 5.3 Swagger UI から `/api/ask` をテスト

* `http://localhost:8000/docs` にアクセス
* `POST /api/ask` を選択
* 「Try it out」→ `question` に質問を入力 → 「Execute」

質問に基づいた回答と、参照文書の一覧が JSON で返ってきます。

---

## 6. エンドポイント概要

### 6.1 `GET /health`

* 用途: サーバーの生存確認
* レスポンス例:

  ```json
  { "status": "ok" }
  ```

### 6.2 `POST /api/ask`

* 用途: RAG による質問応答
* リクエスト:

  ```json
  {
    "question": "このプロジェクトの概要を教えてください。"
  }
  ```
* レスポンス例（イメージ）:

  ```json
  {
    "answer": "（ここに回答本文）",
    "references": [
      {
        "document_id": "rag_notes",
        "document_title": "rag_notes",
        "snippet": "ここにチャンクの先頭300文字が入る…",
        "score": 0.87
      }
    ]
  }
  ```

---

## 7. 今後の拡張アイデア（メモ）

* 文書アップロードAPIの追加
* 文書種別（法務 / 技術など）のメタデータ付与
* 検索結果の評価用テストケース作成
* ツール（Web検索、法令データAPI など）を使うエージェントへの拡張
