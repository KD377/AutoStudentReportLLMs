import React from 'react';

const ReportSections = ({ criteria, setCriteria }) => {
  const handleInputChange = (e, field) => {
    setCriteria(prev => ({ ...prev, [field]: e.target.value }));
  };

  return (
    <div className="mt-3">
      <h2>1. Experiment Aim</h2>
      <textarea value={criteria.aim || ''} onChange={(e) => handleInputChange(e, 'aim')} className="form-control" rows="4" />

      <h2>2. Theoretical Background</h2>
      <textarea value={criteria.background || ''} onChange={(e) => handleInputChange(e, 'background')} className="form-control" rows="4" />

      <h2>3. Research</h2>
      <textarea value={criteria.research || ''} onChange={(e) => handleInputChange(e, 'research')} className="form-control" rows="4" />

      <h2>4. Conclusions</h2>
      <textarea value={criteria.conclusions || ''} onChange={(e) => handleInputChange(e, 'conclusions')} className="form-control" rows="4" />
    </div>
  );
};

export default ReportSections;
