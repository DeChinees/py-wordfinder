// src/Results.js
import React from 'react';

function Results({ results }) {
  return (
    <div>
      <h2>Results</h2>
      <ul>
        {results.map((word, index) => (
          <li key={index}>{word}</li>
        ))}
      </ul>
    </div>
  );
}

export default Results;