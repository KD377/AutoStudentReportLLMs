import React from 'react';
import 'bootstrap/dist/css/bootstrap.min.css'; // Upewnij się, że Bootstrap CSS jest zaimportowany
import FileUpload from './components/FileUpload';
import RateAndCriteria from './components/RateAndCriteria';

function App() {
  return (
    <div className="container mt-5">
      <h1 className="mb-3">Automatic student report system</h1>
      <FileUpload />
      <RateAndCriteria topicId="1" />
    </div>
  );
}

export default App;
