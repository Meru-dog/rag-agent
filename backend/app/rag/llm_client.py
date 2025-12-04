# backend/app/rag/llm_client.py
from typing import List, Dict, Any  # 型ヒント
from openai import OpenAI          # 新しい OpenAI Python クライアント

from app import config             # 設定（APIキーやモデル名）


# OpenAI クライアントのインスタンスを1つ作って使い回す
client = OpenAI(api_key=config.OPENAI_API_KEY)


def build_context_text(chunks: List[Dict[str, Any]]) -> str:
    """
    RAG で取得したチャンクのリストを、
    そのまま LLM に渡す「コンテキスト用テキスト」に整形する。
    """
    parts = []
    for item in chunks:
        meta = item["metadata"]
        content = item["content"]
        title = meta.get("document_title", "無題ドキュメント")
        idx = meta.get("chunk_index", 0)
        # タイトルとチャンク番号をコメント的に付けてから本文を並べる
        parts.append(f"# {title} (chunk {idx})\n{content}")

    # チャンクごとに空行を挟んで連結
    return "\n\n".join(parts)


def generate_answer(question: str, retrieved_chunks: List[Dict[str, Any]]) -> str:
    """
    質問文と、retrieve で取得したチャンクをもとに、
    OpenAI のチャットモデルに回答を生成させる。
    """
    # LLMに渡すコンテキストテキストを構築
    context_text = build_context_text(retrieved_chunks)

    # システムプロンプト：アシスタントのキャラや方針を指定
    system_prompt = (
        "あなたはユーザーの手元のドキュメントをもとに答えるアシスタントです。\n"
        "以下のコンテキスト（文書抜粋）だけを根拠にして、日本語で丁寧に回答してください。\n"
        "コンテキストに書かれていない情報については、推測で答えず、"
        "『手元の文書には該当の記載がありません』と明示してください。"
    )

    # ユーザープロンプト：質問 + コンテキストをまとめて渡す
    user_prompt = (
        f"質問:\n{question}\n\n"
        f"コンテキスト:\n{context_text}"
    )

    # OpenAI のチャット補完APIを呼び出す
    response = client.chat.completions.create(
        model=config.CHAT_MODEL,
        messages=[
            {"role": "system", "content": system_prompt},  # システムメッセージ
            {"role": "user", "content": user_prompt},      # ユーザーメッセージ
        ],
    )

    # 一番最初の候補のメッセージ本文を取り出す
    answer = response.choices[0].message.content
    # None の可能性に備えて空文字と比較
    return answer or ""
