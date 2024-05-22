import React, { useState } from 'react';
import axios from 'axios';

const FileUpload = () => {
  const [files, setFiles] = useState([]);
  const [title, setTitle] = useState('');

  const handleFileChange = (event) => {
    setFiles(event.target.files);
  };

  const handleSubmit = async (event) => {
    event.preventDefault();
    const formData = new FormData();
    Array.from(files).forEach(file => {
      formData.append('files', file);
    });

    await axios.post('http://localhost:8000/reports/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    }).then(response => {
      setTitle(response.data.title);
    }).catch(error => {
      console.error('Uploading error:', error);
    });
  };

  return (
    <div className="container mt-3">
      <h2>Upload File</h2>
      <form onSubmit={handleSubmit} className="mb-3">
        <input type="file" multiple onChange={handleFileChange} accept=".docx" className="form-control"/>
        <button type="submit" className="btn btn-primary mt-2">Upload</button>
      </form>
      {title && <div className="alert alert-success" role="alert">Report Uplouded</div>}
      <h1>Report title: {title}</h1>
    </div>
  );
};

export default FileUpload;