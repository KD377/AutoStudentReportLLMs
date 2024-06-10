import React, { useState } from 'react';
import axios from 'axios';
import ReportSections from './ReportSections';

const RateAndCriteria = ({ topicId }) => {
  const [criteria, setCriteria] = useState({});

  const handleRate = async () => {
    try {
      const response = await axios.post(`http://localhost:8000/reports/topic/${topicId}/rate`);
      alert(response.data.message);
    } catch (error) {
      alert(error.response.data.detail);
    }
  };

  const handleGenerateCriteria = async () => {
    const response = await axios.post(`http://localhost:8000/criteria/topic/${topicId}/generate`);
    setCriteria(response.data.criteria);
  };

  const handleSaveCriteria = async () => {
    try {
      const response = await axios.post('http://localhost:8000/criteria/update', criteria);
      alert(response.data.message);
    } catch (error) {
      console.error('Error saving criteria:', error);
      alert('Error saving criteria');
    }
  };

  return (
    <div className="container mt-3">
      <h2>Rate and Generate Criteria</h2>
      <button onClick={handleGenerateCriteria} className="btn btn-info">Generate Criteria</button>
      <ReportSections criteria={criteria} setCriteria={setCriteria} />
      <button onClick={handleSaveCriteria} className="btn btn-success mt-3">Save Criteria</button>
    </div>
  );
};

export default RateAndCriteria;
