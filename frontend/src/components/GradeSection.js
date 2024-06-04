import React, { useState } from 'react';
import axios from 'axios';

const GradeSection = () => {
  const [grades, setGrades] = useState([]);
  const [summary, setSummary] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleRateReports = async () => {
    setLoading(true);
    setError(null);

    try {
      const response = await axios.post('http://localhost:8000/reports/topic/1/rate');
      setGrades(response.data.grades);
      setSummary(response.data.summary);
      setLoading(false);
    } catch (error) {
      console.error('Error fetching grades:', error);
      setError('Error fetching grades');
      setLoading(false);
    }
  };

  return (
    <div className="container mt-3">
      <h2>All Report Grades</h2>
      <button onClick={handleRateReports} className="btn btn-primary mb-3">
        Rate Reports
      </button>
      {loading && <div>Loading...</div>}
      {error && <div className="alert alert-danger">{error}</div>}
      {!loading && !error && grades.length > 0 && (
        <>
          {grades.map((grade, index) => (
            <div key={index} className="card mb-3">
              <div className="card-body">
                <h5 className="card-title">Report {index + 1}</h5>
                <h6>Experiment Aim</h6>
                <p>Points: {grade["Experiment aim"]?.Grades?.points}</p>
                <p>{grade["Experiment aim"]?.Grades?.description}</p>
                <h6>Theoretical Background</h6>
                <p>Points: {grade["Theoretical background"]?.Grades?.points}</p>
                <p>{grade["Theoretical background"]?.Grades?.description}</p>
                {grade.Exercise_1 && (
                  <>
                    <h6>Exercise 1</h6>
                    <p>Points: {grade.Exercise_1?.Grades?.points}</p>
                    <p>{grade.Exercise_1?.Grades?.description}</p>
                  </>
                )}
                {grade.Exercise_2 && (
                  <>
                    <h6>Exercise 2</h6>
                    <p>Points: {grade.Exercise_2?.Grades?.points}</p>
                    <p>{grade.Exercise_2?.Grades?.description}</p>
                  </>
                )}
                {grade.Exercise_3 && (
                  <>
                    <h6>Exercise 3</h6>
                    <p>Points: {grade.Exercise_3?.Grades?.points}</p>
                    <p>{grade.Exercise_3?.Grades?.description}</p>
                  </>
                )}
                <h6>Conclusions</h6>
                <p>Points: {grade.Conclusions?.Grades?.points}</p>
                <p>{grade.Conclusions?.Grades?.description}</p>
              </div>
            </div>
          ))}
          <h2>Summary</h2>
          <div className="card mb-3">
            <div className="card-body">
              <p>{summary}</p>
            </div>
          </div>
        </>
      )}
    </div>
  );
};

export default GradeSection;
