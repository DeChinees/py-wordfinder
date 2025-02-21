// src/App.js
import React, { useState } from 'react';
import axios from 'axios';
import InputForm from './InputForm';
import LetterTiles from './LetterTiles';
import Results from './Results';
import { Tile } from './styles';

function App() {
  const [includedLetters, setIncludedLetters] = useState('');
  const [excludedLetters, setExcludedLetters] = useState('');
  const [pattern, setPattern] = useState('?????'); // Default 5-letter pattern
  const [language, setLanguage] = useState('EN');
  const [wordLength, setWordLength] = useState(5);
  const [results, setResults] = useState([]);

  const handleSearch = async () => {
    try {
      const response = await axios.post('http://127.0.0.1:8000', {
        included: includedLetters,
        excluded: excludedLetters,
        pattern: pattern,
        language: language,
        length: wordLength,
      });
      setResults(response.data);
    } catch (error) {
      console.error('Error fetching data:', error);
    }
  };

  return (
    <div>
      <h1>Word Helper</h1>
      <p>Enter your criteria to find possible words.</p>

      <InputForm
        includedLetters={includedLetters}
        setIncludedLetters={setIncludedLetters}
        excludedLetters={excludedLetters}
        setExcludedLetters={setExcludedLetters}
        pattern={pattern}
        setPattern={setPattern}
        language={language}
        setLanguage={setLanguage}
        wordLength={wordLength}
        setWordLength={setWordLength}
        onSearch={handleSearch}
      />

      <div>
        <h2>Included Letters</h2>
        <LetterTiles letters={includedLetters} included={true} />
      </div>

      <div>
        <h2>Excluded Letters</h2>
        <LetterTiles letters={excludedLetters} included={false} />
      </div>

      <div>
        <h2>Pattern</h2>
        <LetterTiles letters={pattern.split('')} pattern={true} />
      </div>

      <Results results={results} />
    </div>
  );
}

export default App;