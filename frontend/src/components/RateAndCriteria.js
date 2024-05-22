// src/components/RateAndCriteria.js
import React from 'react';
import { useState } from 'react';
import axios from 'axios';
import ReportSections from './ReportSections';
const RateAndCriteria = ({ topicId }) => {
  const handleRate = async () => {
    try {
      const response = await axios.post(`http://localhost:8000/reports/topic/${topicId}/rate`);
      alert(response.data.message);
    } catch (error) {
      alert(error.response.data.detail);
    }
  };

  const [criteria, setCriteria] = useState({});
  const handleGenerateCriteria = async () => {
      const response = await axios.post(`http://localhost:8000/criteria/topic/${topicId}/generate`);
      setCriteria(response.data.criteria);
    }

  return (
    <div>
      <button onClick={handleRate}>Rate Documents</button>
      <button onClick={handleGenerateCriteria}>Generate Criteria</button>
        <ReportSections criteria={criteria} />
    </div>
  );
};

export default RateAndCriteria;
