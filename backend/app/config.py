# backend/app/config.py
from pathlib import Path  # ファイルパスを扱うための標準ライブラリ
import os                 # 環境変数を読むための標準ライブラリ
from dotenv import load_dotenv  # .env ファイルを読み込むためのライブラリ

# .env ファイル（同じディレクトリか上位にある）を読み込む
load_dotenv()

# このファイル（config.py）のフルパスから、backend/ の一つ上のディレクトリを求める
# __file__ → config.py のパス
# .parent → app/
# .parent → backend/
BASE_DIR = Path(__file__).resolve().parent.parent

# 文書ファイルを置くディレクトリのパス（backend/documents）
DOCUMENTS_DIR = BASE_DIR / "documents"

# Chroma のベクトルストアを保存するディレクトリ（backend/chroma_db）
CHROMA_DIR = BASE_DIR / "chroma_db"

# Chroma コレクションの名前（「このプロジェクトのベクトル集合」を識別するキー）
CHROMA_COLLECTION = "documents"

# OpenAI の API キーを環境変数から取得
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# APIキーが設定されていない場合は、起動時に落として気づけるようにする
if not OPENAI_API_KEY:
    raise RuntimeError("OPENAI_API_KEY が .env などで設定されていません。")

# 利用する埋め込みモデル名
EMBEDDING_MODEL = "text-embedding-3-small"

# 利用するチャットモデル名
CHAT_MODEL = "gpt-4.1-mini"
