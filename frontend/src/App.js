import React, { useState, useEffect, useRef } from 'react';
import {
  Container, Typography, TextField, Box, Skeleton, CssBaseline,
  ThemeProvider, createTheme, List, ListItem, ListItemText, Button, Tabs, Tab
} from '@mui/material';
import "./App.css";
// Import a specific theme (e.g., 'github')
import 'highlight.js/styles/monokai-sublime.css';
import ToggleArrow from './components/toggle_arrow/toggle_arrow';
import Settings from './components/modelsetting/modelsetting';
import { useLLMParm } from './contexts/LLMParam';
import { useUser } from './contexts/UserContext';
import UserInfoForm from './components/userinfoform/userinfoform';
import Sidebar from './components/Sidebar';
import GeneralChat from './components/GeneralChat';
import SQLQueries from './components/SQLQueries';
import TabPanel from './components/TabPanel';
import tabConfig from './components/TabConfig';
import { WebSocketProvider } from './contexts/WebSocketContext';

import MainContent from './components/MainContent';
const theme = createTheme({
  palette: {
    // mode: 'blue',
  },
});


function App() {
  const [tabIndex, setTabIndex] = useState(0);
  const tabStates = tabConfig.map(config => config.useTabState());

  const [generalHistory, setGeneralHistory] = useState([]);
  const [sqlHistory, setSqlHistory] = useState([]);

  const [response, setResponse] = useState("");
  const [question, setQuestion] = useState("");
  const [loading, setLoading] = useState(false);
  const [history, setHistory] = useState([]);
  const [questionId, setQuestionId] = useState(0); // New state for tracking question ID
  const [isCollapsed, setIsCollapsed] = useState(false);
  const latestQuestionId = useRef(questionId);
  const WS = useRef(null);
  useEffect(() => {
    latestQuestionId.current = questionId;
  }, [questionId]); // Re-run this effect whenever `questionId` changes
  const { currentModel , modelSettings} = useLLMParm();  
  const { user, setUser } = useUser();

  const handleTabChange = (event, newValue) => {
    setTabIndex(newValue);
  };
  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <Container maxWidth="lg">
        <Box sx={{ display: 'flex', height: '100vh' }}>
          <Sidebar isCollapsed={isCollapsed} />
          <ToggleArrow isCollapsed={isCollapsed} setIsCollapsed={setIsCollapsed} />
          <WebSocketProvider>  
            <Box sx={{ flexGrow: 1, display: 'flex', flexDirection: 'column' }}>
              <Tabs value={tabIndex} onChange={handleTabChange} aria-label="Main Tabs">
                {tabConfig.map((tab, index) => (
                  <Tab key={index} label={tab.label} />
                ))}
              </Tabs>
              {tabConfig.map((tab, index) => (
                <TabPanel key={index} value={tabIndex} index={index}>
                  <tab.component {...tabStates[index]} />
                </TabPanel>
              ))}
            </Box>
          </WebSocketProvider>
        </Box>
      </Container>
    </ThemeProvider>
  );
}

export default App;
