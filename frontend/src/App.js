// src/App.js
import React, { useEffect, useState } from 'react';
import api from './api';

function App() {
  const [message, setMessage] = useState('');

  useEffect(() => {
    api.get('/')
      .then(response => {
        setMessage(response.data.message);
      })
      .catch(error => {
        console.error('There was an error fetching the data!', error);
      });
  }, []);

  return (
    <div className="App">
      <h1>{message}</h1>
    </div>
  );
}

export default App;
