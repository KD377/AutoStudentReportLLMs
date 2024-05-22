import React from 'react';

const ReportSections = ({ criteria }) => {
  return (
    <div className="mt-3">
      <h2>1. Experiment Aim</h2>
      <p>{criteria.aim}</p>
      <h2>2. Theoretical Background</h2>
      <p>{criteria.background}</p>
      <h2>3. Research</h2>
      <p>{criteria.research}</p>
      <h2>4. Conclusions</h2>
      <p>{criteria.conclusions}</p>
    </div>
  );
};

export default ReportSections;
