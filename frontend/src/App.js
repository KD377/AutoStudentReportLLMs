import React from 'react';
import FileUpload from './components/FileUpload';
import RateAndCriteria from './components/RateAndCriteria';
import ReportSections from './components/ReportSections';
function App() {
  return (
    <div className="App">
      <h1>Automatic student report system</h1>
      <FileUpload topicId="1"/>
      <RateAndCriteria topicId="1" />

    </div>
  );
}

export default App;