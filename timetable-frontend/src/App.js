import React, { useState } from 'react';
import { BrowserRouter as Router, Route, Link, Routes, useLocation } from 'react-router-dom';
import './App.css';

function AddInfo() {
  const [teacherCount, setTeacherCount] = useState(0);
  const [subjectCount, setSubjectCount] = useState(0);
  const [sectionCount, setSectionCount] = useState(0);
  const [teachers, setTeachers] = useState([]);
  const [subjects, setSubjects] = useState([]);
  const [sections, setSections] = useState([]);
  const [error, setError] = useState('');

  const handleTeacherCountChange = (e) => setTeacherCount(Number(e.target.value));
  const handleSubjectCountChange = (e) => setSubjectCount(Number(e.target.value));
  const handleSectionCountChange = (e) => setSectionCount(Number(e.target.value));

  const handleInputChange = (e, setter) => {
    const index = Number(e.target.dataset.index);
    setter((prev) => {
      const newValues = [...prev];
      newValues[index] = e.target.value;
      return newValues;
    });
  };

  const validateAndSubmit = () => {
    if (teachers.length !== teacherCount || subjects.length !== subjectCount || sections.length !== sectionCount) {
      setError('Please fill in all fields.');
      return;
    }

    if ([...teachers, ...subjects, ...sections].some((value) => !value)) {
      setError('Please fill in all fields.');
      return;
    }

    setError('');
    console.log('Teachers:', teachers);
    console.log('Subjects:', subjects);
    console.log('Sections:', sections);
    // Add info submission logic here
  };

  const renderTextBoxes = (count, label, values, setter) => {
    return Array.from({ length: count }).map((_, i) => (
      <div key={i} className="dynamic-input">
        <label>{`${label} ${i + 1}:`}</label>
        <input
          type="text"
          placeholder={`${label} ${i + 1}`}
          value={values[i] || ''}
          data-index={i}
          onChange={(e) => handleInputChange(e, setter)}
          className="inputBox"
        />
      </div>
    ));
  };

  return (
    <div className="add-info">
      <h2>Add Info</h2>
      <div className="input-section">
        <label>Number of Teachers:</label>
        <input type="number" value={teacherCount} onChange={handleTeacherCountChange} className="inputBox" />
      </div>
      {renderTextBoxes(teacherCount, 'Teacher', teachers, setTeachers)}

      <div className="input-section">
        <label>Number of Subjects:</label>
        <input type="number" value={subjectCount} onChange={handleSubjectCountChange} className="inputBox" />
      </div>
      {renderTextBoxes(subjectCount, 'Subject', subjects, setSubjects)}

      <div className="input-section">
        <label>Number of Sections:</label>
        <input type="number" value={sectionCount} onChange={handleSectionCountChange} className="inputBox" />
      </div>
      {renderTextBoxes(sectionCount, 'Section', sections, setSections)}

      {error && <div className="error">{error}</div>}
      <button onClick={validateAndSubmit} className="button add-info-button">Add Info</button>
    </div>
  );
}

function GenerateInfo() {
  const [teacherName, setTeacherName] = useState('');
  const [hours, setHours] = useState('');
  const [day, setDay] = useState('');
  const [error, setError] = useState('');

  const handleGenerate = () => {
    if (!teacherName || !hours || !day) {
      setError('Please fill in all fields.');
      return;
    }

    setError('');
    console.log('Generate info:', { teacherName, hours, day });
    // Generate info logic here
  };

  return (
    <div className="generate-info">
      <h2>Generate Info</h2>
      <div className="input-section">
        <label>Teacher Name:</label>
        <input type="text" value={teacherName} onChange={(e) => setTeacherName(e.target.value)} className="inputBox" />
      </div>
      <div className="input-section">
        <label>Hours:</label>
        <input type="text" value={hours} onChange={(e) => setHours(e.target.value)} className="inputBox" />
      </div>
      <div className="input-section">
        <label>Day:</label>
        <input type="text" value={day} onChange={(e) => setDay(e.target.value)} className="inputBox" />
      </div>
      {error && <div className="error">{error}</div>}
      <button onClick={handleGenerate} className="button">Generate</button>
    </div>
  );
}

function App() {
  const location = useLocation();

  return (
    <div className="App">
      <h1>Timetable Dashboard</h1>
      {location.pathname === '/' && (
        <div className="buttons">
          <Link to="/add-info"><button className="button">Add Info</button></Link>
          <Link to="/generate-info"><button className="button">Generate Info</button></Link>
        </div>
      )}
      <Routes>
        <Route path="/add-info" element={<AddInfo />} />
        <Route path="/generate-info" element={<GenerateInfo />} />
      </Routes>
    </div>
  );
}

export default function WrappedApp() {
  return (
    <Router>
      <App />
    </Router>
  );
}
