import React, { useState } from 'react';
import './App.css';

function App() {
  const [inputText, setInputText] = useState('');
  const [responseText, setResponseText] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSend = async () => {
    setLoading(true);
    try {
      const res = await fetch('http://127.0.0.1:8000/query', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ query: inputText }),
      });

      const data = await res.json();
      setResponseText(data.result || 'No response field in JSON');
    } catch (error) {
      setResponseText(`Error: ${error.message}`);
    } finally {
      setLoading(false);
    }
  };
  return (
    <div style={{ maxWidth: '600px', margin: '2rem auto', fontFamily: 'Arial, sans-serif' }}>
      <h2>Query Interface</h2>
      <textarea
        rows="4"
        style={{ width: '100%', padding: '0.5rem', marginBottom: '1rem' }}
        placeholder="Enter your query here..."
        value={inputText}
        onChange={(e) => setInputText(e.target.value)}
      />
      <button
        onClick={handleSend}
        disabled={loading || !inputText.trim()}
        style={{ padding: '0.5rem 1rem' }}
      >
        {loading ? 'Sending...' : 'Send'}
      </button>

      {responseText && (
        <div style={{ marginTop: '2rem', padding: '1rem', border: '1px solid #ccc' }}>
          <strong>Response:</strong>
          <p>{responseText}</p>
        </div>
      )}
    </div>
  );
}

export default App;
