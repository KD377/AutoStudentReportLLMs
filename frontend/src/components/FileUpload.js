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
          console.log('Title', response.data.title);
        })
        .catch(error => {
          console.error('Uploading error:', error);
        });
  };

  const handleDeleteReports = async () => {
    try {
      const response = await axios.delete('http://localhost:8000/reports/delete');
      alert(response.data.message);
    } catch (error) {
      console.error('Error deleting reports:', error);
      alert('Error deleting reports');
    }
  };

  return (
    <div className="container mt-3">
      <form onSubmit={handleSubmit}>
        <div className="mb-3">
          <input type="file" multiple onChange={handleFileChange} accept=".docx" className="form-control" />
        </div>
        <button type="submit" className="btn btn-primary">Upload</button>
      </form>
      {title && <p>Uploaded Report Title: {title}</p>}
      <button onClick={handleDeleteReports} className="btn btn-danger mt-3">Delete All Reports</button>
    </div>
  );
};

export default FileUpload;
