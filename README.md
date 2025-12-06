# ドキュメント検索・要約エージェント（RAG）

指定したテキスト文書群を対象に、**関連箇所の検索＋内容に基づく要約回答**を行うシンプルな RAG（Retrieval-Augmented Generation）アプリです。

* バックエンド：FastAPI（Python）
* フロントエンド：React（Vite）
* ベクトルストア：Chroma
* LLM / Embedding：OpenAI API

---

## 1. なにができるか

* 自分で用意したテキストファイル（契約書、メモ、技術ノートなど）をアップロードしておくと、
* ブラウザから自然文で質問 →

  * 関連するチャンクをベクトル検索（Chroma）
  * その内容を踏まえて LLM が日本語で回答
* 参照された文書タイトルやスニペットも表示されるので、「どこを根拠に答えているか」が分かります。

---

## 2. アーキテクチャ概要

```text
User (Browser)
   ↓
React (Vite SPA)
   ↓  POST /api/ask (JSON: { question })
FastAPI (Python)
   ↓
Chroma (ベクトルストア) ＋ OpenAI Embedding
   ↓
LLM（OpenAI）で回答生成
   ↓
React に JSON で返却
```

---

## 3. 技術スタック

* Backend

  * Python 3.11+
  * FastAPI
  * ChromaDB
  * OpenAI API（`gpt-4.1-mini` 等）
* Frontend

  * React
  * Vite
* Infra（例）

  * Backend: Render 等
  * Frontend: Vercel 等

---

## 4. 公開版アプリの使い方（利用者向け）

※ 実際の URL に置き換えてください。

1. ブラウザで以下の URL を開く

   * フロントエンド：`https://<YOUR_FRONTEND_URL>`
2. テキストエリアに日本語で質問を入力

   * 例）「この契約書の解除条項の要点を教えてください」
3. 「送信」を押すと、

   * 回答エリアに LLM が生成した回答
   * 下部に「参照文書（タイトル・スコア・抜粋）」が表示されます。

💡 **注意：**
このアプリはあらかじめサーバー側に配置した文書のみを検索対象としています。
ユーザーがブラウザから直接ファイルをアップロードする機能はありません（v1 時点）。

---

## 5. 開発者向け：ローカルで動かす

### 5.1 リポジトリ構成（抜粋）

```text
doc-rag-agent/
├─ backend/
│  ├─ app/
│  │  ├─ main.py            # FastAPI エントリポイント (/api/ask)
│  │  ├─ config.py          # 設定（モデル名・パスなど）
│  │  └─ rag/
│  │     ├─ document_loader.py
│  │     ├─ index_builder.py
│  │     ├─ retriever.py
│  │     └─ llm_client.py
│  ├─ documents/            # 検索対象のテキストファイル (.txt など)
│  ├─ requirements.txt
│  └─ .env                  # OpenAI API キーなど（Git 管理外）
└─ frontend/
   ├─ index.html
   ├─ package.json
   ├─ vite.config.js
   └─ src/
      ├─ main.jsx
      ├─ App.jsx
      ├─ App.css
      └─ index.css
```

### 5.2 バックエンドセットアップ

```bash
cd backend

# 仮想環境の作成（任意）
python -m venv .venv
source .venv/bin/activate  # Windows は .venv\Scripts\activate

pip install -r requirements.txt
```

`.env` を作成して OpenAI キーなどを設定：

```bash
# backend/.env
OPENAI_API_KEY="sk-xxxxxxxxxxxxxxxxxxxxx"
OPENAI_EMBEDDING_MODEL="text-embedding-3-small"
OPENAI_LLM_MODEL="gpt-4.1-mini"
CHROMA_DIR="./chroma_db"
CHROMA_COLLECTION="documents"
DOCUMENTS_DIR="./documents"
```

### 5.3 インデックス構築

`backend/documents/` 配下に `.txt` などのファイルを置いた上で：

```bash
cd backend
python -m app.rag.build_index
```

成功すると：

```text
インデックス作成完了: XX チャンクを登録しました。
```

と表示されます。

### 5.4 バックエンド起動

```bash
cd backend
uvicorn app.main:app --reload
```

---

### 5.5 フロントエンドセットアップ

```bash
cd frontend
npm install
```

**環境変数の設定（重要）**

`frontend/.env` ファイルを作成して、バックエンドAPIのURLを設定します：

```bash
# frontend/.env
VITE_API_URL=http://localhost:8000/api/ask
```

**注意：**
- `.env` ファイルはGitにコミットされません（`.gitignore`で除外されています）
- デプロイ環境（Vercel等）では、環境変数として `VITE_API_URL` を設定してください
- ローカル開発時は上記のデフォルト値（`http://localhost:8000/api/ask`）が使用されます

ローカル開発用サーバーを起動：

```bash
npm run dev
```

---

## 6. デプロイ（概要）

* Backend

  * Render 等で「Python / FastAPI」サービスとしてデプロイ
  * Start command 例：`uvicorn app.main:app --host 0.0.0.0 --port $PORT`
  * 環境変数に OpenAI API キーやパス関連を設定

* Frontend

  * Vercel 等に GitHub 連携でデプロイ
  * ビルドコマンド：`npm run build`
  * **環境変数の設定（重要）**：
    * Vercelのダッシュボードで環境変数を追加：
      * 変数名：`VITE_API_URL`
      * 値：`https://your-backend-url.onrender.com/api/ask`
    * これにより、コードにURLをハードコードせずにデプロイできます

---

## 7. 制約・注意点

* 現時点では **ユーザーアップロード機能なし**（サーバー側で事前に文書を配置）
* OpenAI API を使用するため、利用量に応じて費用が発生します
* 契約書などセンシティブな文書を扱う場合は、
  アクセス制御・ネットワーク構成・ログ管理など別途セキュリティ設計が必要です

---

## 8. ライセンス

（必要に応じて追記：例：MIT License など）
