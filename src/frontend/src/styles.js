// src/styles.js
import styled from 'styled-components';

export const Tile = styled.div`
  width: 40px;
  height: 40px;
  display: inline-flex;
  justify-content: center;
  align-items: center;
  font-size: 1.5em;
  margin: 4px;
  color: white;
  background-color: ${props => props.color};
`;

export const Input = styled.input`
  padding: 8px;
  margin: 4px;
  border: 1px solid #ccc;
  border-radius: 4px;
`;

export const Button = styled.button`
  padding: 8px 16px;
  margin: 4px;
  background-color: #007bff;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
`;

// Add more styled components as needed