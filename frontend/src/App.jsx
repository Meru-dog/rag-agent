// frontend/src/App.jsx
import { useState } from "react";
import "./App.css";

function App() {
  const [question, setQuestion] = useState("");
  const [answer, setAnswer] = useState("");
  const [references, setReferences] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState("");

  const handleSubmit = async (e) => {
    e.preventDefault();

    if (!question.trim()) {
      setError("質問を入力してください。");
      return;
    }

    setIsLoading(true);
    setError("");
    setAnswer("");
    setReferences([]);

    try {
      const res = await fetch("http://localhost:8000/api/ask", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ question }),
      });

      if (!res.ok) {
        throw new Error(`サーバーエラー: ${res.status}`);
      }

      const data = await res.json();
      setAnswer(data.answer ?? "");
      setReferences(data.references ?? []);
    } catch (err) {
      console.error(err);
      setError("回答の取得に失敗しました。サーバーが起動しているか確認してください。");
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="app">
      <h1 className="app-title">ドキュメント検索・要約エージェント</h1>

      <form className="question-form" onSubmit={handleSubmit}>
        <label className="question-label">
          質問を入力してください：
          <textarea
            className="question-input"
            value={question}
            onChange={(e) => setQuestion(e.target.value)}
            rows={4}
            placeholder="例：このプロジェクトの概要を教えて など"
          />
        </label>

        <button
          className="submit-button"
          type="submit"
          disabled={isLoading || !question.trim()}
        >
          {isLoading ? "問い合わせ中..." : "送信"}
        </button>
      </form>

      {error && <div className="error-message">{error}</div>}

      <div className="answer-section">
        <h2>回答</h2>
        {isLoading && <p>回答を生成しています...</p>}
        {!isLoading && answer && (
          <pre className="answer-text">{answer}</pre>
        )}
        {!isLoading && !answer && !error && (
          <p className="placeholder-text">まだ質問が送信されていません。</p>
        )}
      </div>

      <div className="references-section">
        <h2>参照文書</h2>
        {references.length === 0 && <p>参照文書はありません。</p>}
        {references.map((ref) => (
          <div key={ref.document_id} className="reference-card">
            <div className="reference-title">{ref.document_title}</div>
            <div className="reference-score">
              関連度スコア: {ref.score?.toFixed(2)}
            </div>
            <div className="reference-snippet">{ref.snippet}</div>
          </div>
        ))}
      </div>
    </div>
  );
}

export default App;
