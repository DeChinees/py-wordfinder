// src/InputForm.js
import React from 'react';
import { Input, Button } from './styles';

function InputForm({
  includedLetters,
  setIncludedLetters,
  excludedLetters,
  setExcludedLetters,
  pattern,
  setPattern,
  language,
  setLanguage,
  wordLength,
  setWordLength,
  onSearch,
}) {
  return (
    <div>
      <Input
        type="text"
        placeholder="Included Letters"
        value={includedLetters}
        onChange={(e) => setIncludedLetters(e.target.value)}
      />
      <Input
        type="text"
        placeholder="Excluded Letters"
        value={excludedLetters}
        onChange={(e) => setExcludedLetters(e.target.value)}
      />
      <Input
        type="text"
        placeholder="Pattern (e.g., ?a?e?)"
        value={pattern}
        onChange={(e) => setPattern(e.target.value)}
      />
      <select value={language} onChange={(e) => setLanguage(e.target.value)}>
        <option value="EN">English</option>
        <option value="NL">Dutch</option>
        {/* Add other languages */}
      </select>
      <Input
        type="number"
        placeholder="Word Length"
        value={wordLength}
        onChange={(e) => setWordLength(Number(e.target.value))}
      />
      <Button onClick={onSearch}>Search</Button>
    </div>
  );
}

export default InputForm;