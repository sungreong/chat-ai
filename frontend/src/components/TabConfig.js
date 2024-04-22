// TabConfig.js
import GeneralChat from './GeneralChat';
import SQLQueries from './SQLQueries';
import React, { useState } from 'react';

const useTabState = () => {
  const [question, setQuestion] = useState("");
  const [history, setHistory] = useState([]);
  const [loading, setLoading] = useState(false);

  const handleSendQuestion = (sendFunction, user) => {
    if (!question || loading) return;
    setLoading(true);
    sendFunction(question, user);  // Placeholder for sending question logic
    setHistory([...history, { question, response: "Awaiting response..." }]);
    setQuestion("");
  };

  const handleStopClick = () => {
    setLoading(false);
    console.log("Stopped loading!");
  };

  return { question, setQuestion, handleSendQuestion, handleStopClick, loading, history };
};

const tabConfig = [
  {
    label: "General Chat",
    component: GeneralChat,
    useTabState,
  },
  {
    label: "SQL Queries",
    component: SQLQueries,
    useTabState,
  }
];

export default tabConfig;
