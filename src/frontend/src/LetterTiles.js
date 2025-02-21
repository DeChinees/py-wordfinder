// src/LetterTiles.js
import React from 'react';
import { Tile } from './styles';

function LetterTiles({ letters, included, pattern }) {
  const getTileColor = (letter) => {
    if (pattern) {
      return letter === '?' ? 'lightgray' : 'green'; // Pattern tiles
    }
    return included ? 'green' : 'yellow'; // Included/excluded tiles
  };

  return (
    <div>
      {Array.isArray(letters) ? letters.map((letter, index) => (
        <Tile key={index} color={getTileColor(letter)}>
          {letter}
        </Tile>
      )) : letters.split('').map((letter, index) => (
        <Tile key={index} color={getTileColor(letter)}>
          {letter}
        </Tile>
      ))}
    </div>
  );
}

export default LetterTiles;