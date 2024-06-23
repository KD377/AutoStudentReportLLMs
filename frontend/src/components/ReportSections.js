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

      <h2>3. Exercise 1</h2>
      <textarea value={criteria.exercise1 || ''} onChange={(e) => handleInputChange(e, 'exercise1')} className="form-control" rows="4" />

      <h2>4. Exercise 2</h2>
      <textarea value={criteria.exercise2 || ''} onChange={(e) => handleInputChange(e, 'exercise2')} className="form-control" rows="4" />

      <h2>5. Exercise 3</h2>
      <textarea value={criteria.exercise3 || ''} onChange={(e) => handleInputChange(e, 'exercise3')} className="form-control" rows="4" />

      <h2>6. Conclusions</h2>
      <textarea value={criteria.conclusions || ''} onChange={(e) => handleInputChange(e, 'conclusions')} className="form-control" rows="4" />
    </div>
  );
};

export default ReportSections;
