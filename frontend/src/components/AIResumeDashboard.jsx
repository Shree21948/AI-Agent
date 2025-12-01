import React, { useState } from "react";

const AIResumeDashboard = () => {
  const [resumeText, setResumeText] = useState("");
  const [results, setResults] = useState(null);

  const handleAnalyze = () => {
    if (!resumeText.trim()) {
      alert("Please enter your resume text!");
      return;
    }

    // Mock analysis result (replace with real logic if needed)
    const mockResults = {
      skills: ["Python", "React", "Machine Learning"],
      mapping: { experience: 3, projects: 5 },
      recommendations: ["Add more projects", "Highlight leadership skills"],
      growth: "Intermediate to Advanced",
    };

    setResults(mockResults);
  };

  return (
    <div className="min-h-screen bg-gray-100 p-6">
      {/* Header */}
      <header className="mb-8 text-center">
        <h1 className="text-3xl font-bold text-blue-600">AI Resume Analyzer</h1>
        <p className="text-gray-700 mt-2">Paste your resume and get instant insights</p>
      </header>

      {/* Input Section */}
      <div className="mb-6">
        <textarea
          className="w-full h-48 p-4 border border-gray-300 rounded-lg shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-400 resize-none"
          placeholder="Paste your resume text here..."
          value={resumeText}
          onChange={(e) => setResumeText(e.target.value)}
        ></textarea>
        <button
          className="mt-4 px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition"
          onClick={handleAnalyze}
        >
          Analyze Resume
        </button>
      </div>

      {/* Results Section */}
      {results && (
        <div className="bg-white p-6 rounded-lg shadow-md">
          <h2 className="text-2xl font-semibold mb-4 text-gray-800">Analysis Results</h2>

          <div className="mb-4">
            <h3 className="font-semibold text-gray-700">Skills:</h3>
            <ul className="list-disc list-inside">
              {results.skills.map((skill, idx) => (
                <li key={idx}>{skill}</li>
              ))}
            </ul>
          </div>

          <div className="mb-4">
            <h3 className="font-semibold text-gray-700">Experience & Projects:</h3>
            <p>Experience: {results.mapping.experience} years</p>
            <p>Projects: {results.mapping.projects}</p>
          </div>

          <div className="mb-4">
            <h3 className="font-semibold text-gray-700">Recommendations:</h3>
            <ul className="list-disc list-inside">
              {results.recommendations.map((rec, idx) => (
                <li key={idx}>{rec}</li>
              ))}
            </ul>
          </div>

          <div>
            <h3 className="font-semibold text-gray-700">Growth:</h3>
            <p>{results.growth}</p>
          </div>
        </div>
      )}
    </div>
  );
};

export default AIResumeDashboard;
