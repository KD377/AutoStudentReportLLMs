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

  return (
    <div className="container mt-3">
      <h2>Rate and Generate Criteria</h2>
      <button onClick={handleGenerateCriteria} className="btn btn-info">Generate Criteria</button>
      <ReportSections criteria={criteria} />
    </div>
  );
};

export default RateAndCriteria;
