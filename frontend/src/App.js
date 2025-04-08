import React from 'react';
import './App.css';
import PredictionForm from './components/PredictionForm';

function App() {
  return (
    <div className="App">
      <header className="App-header">
        <h1 className="app-title">🏏 CricSage: Cricket Predictor</h1>
        <PredictionForm />
        <footer className="app-footer">
        </footer>
      </header>
    </div>
  );
}

export default App;