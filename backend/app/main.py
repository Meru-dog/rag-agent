# backend/app/main.py
from typing import List                         # 型ヒント
from fastapi import FastAPI                     # FastAPI 本体
from fastapi.middleware.cors import CORSMiddleware  # CORS 対応用
from pydantic import BaseModel                  # リクエスト/レスポンスの型定義

from app.rag.retriever import RAGRetriever      # 類似検索クラス
from app.rag.llm_client import generate_answer  # 回答生成関数
from .rag.index_builder import build_index



# FastAPI アプリケーションのインスタンスを作成
app = FastAPI()

# フロントエンド（Vite dev server）のオリジンを許可する
origins = [
    "http://localhost:5173",  # 開発中のフロントエンドURL
    "https://rag-agent-delta.vercel.app/" # 本番URL
]

# CORS（クロスオリジン）設定：フロントからのAPIアクセスを許可
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,       # 許可するオリジン
    allow_credentials=True,
    allow_methods=["*"],         # どのHTTPメソッドも許可
    allow_headers=["*"],         # すべてのヘッダーを許可
)


# --- Pydantic モデル定義（リクエスト・レスポンスの型）

class AskRequest(BaseModel):
    # フロントから送られてくる JSON の形：{"question": "...."}
    question: str


class Reference(BaseModel):
    # 参照文書をフロントに返すときの1件分の形
    document_id: str
    document_title: str
    snippet: str
    score: float


class AskResponse(BaseModel):
    # /api/ask のレスポンス全体の形
    answer: str
    references: List[Reference]


# グローバル変数として retriever を用意（起動時に初期化）
retriever: RAGRetriever | None = None


@app.on_event("startup")
def on_startup():
    """
    サーバー起動時に一度だけ実行される処理。
    ここで RAGRetriever を初期化しておく。
    """
    global retriever
    retriever = RAGRetriever(top_k=3)
    print("RAGRetriever 初期化完了")


@app.on_event("startup")
def startup_event():
    build_index()

@app.get("/health")
def health_check():
    """
    動作確認用のシンプルなエンドポイント。
    ブラウザで /health にアクセスすると {"status": "ok"} が返る。
    """
    return {"status": "ok"}


@app.post("/api/ask", response_model=AskResponse)
def ask(request: AskRequest):
    """
    質問を受け取って、RAGで文書検索 → LLMで回答生成を行うメインAPI。
    """
    # retriever がまだ初期化されていない場合はエラー
    if retriever is None:
        raise RuntimeError("Retriever が初期化されていません。")

    # 1. 類似チャンクを検索
    retrieved = retriever.retrieve(request.question)

    # 1件もヒットしなかった場合のフォールバック
    if not retrieved:
        answer = (
            "手元の文書からは、質問に関連する情報を見つけることができませんでした。"
        )
        return AskResponse(answer=answer, references=[])

    # 2. LLM に回答を生成させる
    answer = generate_answer(request.question, retrieved)

    # 3. フロントに返すための参照文書情報を整形
    refs: List[Reference] = []
    for item in retrieved:
        meta = item["metadata"]
        refs.append(
            Reference(
                document_id=str(meta.get("document_id", "")),
                document_title=str(meta.get("document_title", "")),
                snippet=item["content"][:300],  # チャンク先頭の300文字だけ返す
                score=float(item["score"]),
            )
        )

    # 最終的なレスポンスを返す
    return AskResponse(answer=answer, references=refs)
