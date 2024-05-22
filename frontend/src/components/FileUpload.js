// src/components/FileUpload.js
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
            console.error('Uplouding error:', error);
          });
  };

  return (
      <div>
        <form onSubmit={handleSubmit}>
          <input type="file" multiple onChange={handleFileChange} accept=".docx"/>
          <button type="submit">Upload</button>
        </form>
          {title && <p>Uploaded Report Title: {title}</p>}
      </div>
  );
};

export default FileUpload;
