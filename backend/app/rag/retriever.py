# backend/app/rag/retriever.py
from typing import List, Dict, Any         # 型ヒント用
import chromadb                            # Chroma 本体
from chromadb.utils import embedding_functions  # 埋め込み関数

from app import config                     # 設定（パスやモデル名など）


class RAGRetriever:
    """
    質問文から、Chroma に登録されたチャンクを類似度検索するクラス。
    """

    def __init__(self, top_k: int = 3):
        # 何件の類似チャンクを返すかの設定
        self.top_k = top_k

        # 永続化モードの Chroma クライアントを作成
        client = chromadb.PersistentClient(path=str(config.CHROMA_DIR))

        # OpenAI 埋め込み関数を用意（質問文のベクトル化に使う）
        openai_ef = embedding_functions.OpenAIEmbeddingFunction(
            api_key=config.OPENAI_API_KEY,
            model_name=config.EMBEDDING_MODEL,
        )

        # すでにインデックス作成済みのコレクションを取得
        # （なければ空のものが作られる）
        self.collection = client.get_or_create_collection(
            name=config.CHROMA_COLLECTION,
            embedding_function=openai_ef,
        )

    def retrieve(self, question: str) -> List[Dict[str, Any]]:
        """
        質問文をベクトルにして類似検索を行い、
        上位 top_k 件のチャンク情報を返す。
        """
        # Chroma に類似検索を依頼
        result = self.collection.query(
            query_texts=[question],  # 複数クエリのAPIだが、今回は1件だけ渡す
            n_results=self.top_k,    # 上位何件返すか
        )

        # Chromaの戻り値は、各キーに「リストのリスト」が入る形
        # 例: {"documents": [[ "chunk1", "chunk2", ... ]], "metadatas": [[...]]}
        docs = result.get("documents", [[]])[0]
        metadatas = result.get("metadatas", [[]])[0]
        distances = result.get("distances", [[]])[0]

        items: List[Dict[str, Any]] = []
        for content, meta, dist in zip(docs, metadatas, distances):
            # 距離が小さいほど似ているので、簡単なスコアとして 1 - 距離 を使う
            score = max(0.0, 1.0 - float(dist))
            items.append(
                {
                    "content": content,  # チャンクのテキスト
                    "metadata": meta,    # document_id / title / chunk_index など
                    "score": score,      # 0〜1 くらいのスコア
                }
            )

        return items
