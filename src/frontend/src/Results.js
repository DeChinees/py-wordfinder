// src/Results.js
import React from 'react';
import { chunkArray } from './utils';

function Results({ results }) {
  const columns = chunkArray(results, 10);

  return (
    <div style={{ display: 'flex', flexDirection: 'row' }}>
      {columns.map((column, columnIndex) => (
        <div key={columnIndex} style={{ margin: '0 10px' }}>
          <ul>
            {column.map((word, wordIndex) => (
              <li key={wordIndex}>{word}</li>
            ))}
          </ul>
        </div>
      ))}
    </div>
  );
}

export default Results;