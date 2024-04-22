import React, { useState, useEffect, useRef } from 'react';
import {
  Container,
  Typography,
  TextField,
  Box,
  Skeleton,
  CssBaseline,
  ThemeProvider,
  createTheme,
  List,
  ListItem,
  ListItemText,
  Button,
} from '@mui/material';
import { marked } from 'marked';
import "./App.css";
import hljs from 'highlight.js';
// Import a specific theme (e.g., 'github')
import 'highlight.js/styles/monokai-sublime.css';
import ToggleArrow from './components/toggle_arrow/toggle_arrow';
import Settings from './components/modelsetting/modelsetting';
import { useLLMParm } from './contexts/LLMParam';
import { useUser } from './contexts/UserContext';
import UserInfoForm from './components/userinfoform/userinfoform';
const theme = createTheme({
  palette: {
    // mode: 'blue',
  },
});

// Define a new renderer
const renderer = new marked.Renderer();

// Override the code block rendering
renderer.code = (code, language) => {
  // Sanitization of `code` should be done here if necessary
  return `
    <div class="custom-code-block">
      <button class="copy-btn" onclick="copyToClipboard(this)">Copy</button>
      <pre><code class="hljs ${language}">${code}</code></pre>
    </div>
  `;
};

// Set the renderer in marked
marked.setOptions({
  renderer: renderer,
  highlight: function(code, lang) {
    const language = hljs.getLanguage(lang) ? lang : 'plaintext';
    return hljs.highlight(code, { language }).value;
  },
  langPrefix: 'hljs language-', // Use this to style the <pre> with the language class
});
function App() {
  const [response, setResponse] = useState("");
  const [question, setQuestion] = useState("");
  const [loading, setLoading] = useState(false);
  const [history, setHistory] = useState([]);
  const [questionId, setQuestionId] = useState(0); // New state for tracking question ID
  const [isCollapsed, setIsCollapsed] = useState(false);
  const messageHistoryRef = useRef(null);
  const latestQuestionId = useRef(questionId);
  const WS = useRef(null);
  useEffect(() => {
    latestQuestionId.current = questionId;
  }, [questionId]); // Re-run this effect whenever `questionId` changes
  const { currentModel , modelSettings} = useLLMParm();  
  const { user, setUser } = useUser();
  useEffect(() => {
    console.log(currentModel);
    console.log(modelSettings);
  }, [currentModel]);
  
  const handleSendQuestion = () => {
    if (question && !loading) {
      setLoading(true);
  
      // Check if WebSocket connection exists and is open
      if (!WS.current || WS.current.readyState !== WebSocket.OPEN) {
        // Establish a new WebSocket connection if needed
        WS.current = new WebSocket(`ws://localhost:8000/ws/${user}`);
        WS.current.onmessage = (event) => {
          const eventData = JSON.parse(event.data);
          const parsedResponse = marked.parse(eventData.content);
          // Update response and history
          setResponse(parsedResponse);
          setHistory(prevHistory => prevHistory.map(item =>
            item.id === (latestQuestionId.current-1) ? { ...item, response: parsedResponse } : item
          ));
          // Set loading to false after receiving the response
          if (eventData.is_last) {
            setLoading(false);
            WS.current.close();
            WS.current = null; // Ensure the reference is cleared

          }
        };
  
        WS.current.onopen = () => {
          // Send question once WebSocket is open
          sendQuestion();
        };
  
        WS.current.onerror = (error) => {
          console.error("WebSocket Error: ", error);
          setLoading(false);
          // Handle WebSocket error (e.g., show an error message)
        };
      } else {
        // If WebSocket is already open, proceed to send question
        sendQuestion();
      }
    }
  };
  const handleStopClick = async () => {
    try {
      // `action` 값을 `set`으로 설정하여 서버에 취소 신호를 보냅니다.
      const response = await fetch('http://localhost:8000/cancel/set', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        // 필요한 경우 인증 토큰 등 추가 헤더를 설정할 수 있습니다.
      });
  
      if (!response.ok) {
        throw new Error('Network response was not ok');
      }
  
      const responseData = await response.json();
      console.log('Server response:', responseData.message);
  
      // WebSocket 연결이 열려있다면 닫습니다.
      if (WS.current && WS.current.readyState === WebSocket.OPEN) {
        // WS.current.close();
        console.log('WebSocket connection closed.');
        setLoading(false);
        WS.current.close();
        WS.current = null; // Ensure the reference is cleared
      }
    } catch (error) {
      console.error('Failed to send cancel request:', error);
    }
  };
  
  const sendQuestion = () => {
    const currentQuestionId = questionId;
    setQuestionId(id => id + 1);
    setHistory(prevHistory => [...prevHistory, { id: currentQuestionId, question, response: "" }]);
  
    try {
      WS.current.send(JSON.stringify({ id: currentQuestionId, question }));
    } catch (error) {
      console.error("Sending Question Error: ", error);
      setLoading(false);
    }
    setQuestion(""); // Clear the input field
  };
  useEffect(() => {
    // history가 변경될 때마다 실행
    if (messageHistoryRef.current) {
      // 스크롤을 Message History 섹션의 가장 하단으로 이동
      messageHistoryRef.current.scrollTop = messageHistoryRef.current.scrollHeight;
    }
  }, [history]); // 의존성 배열에 history를 추가하여 history가 변경될 때마다 useEffect가 실행되도록 함

  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <Container maxWidth="lg">
        <Box sx={{ display: 'flex', height: '100vh' }}>
          <Box sx={{
              width: isCollapsed ? '240px' : '0', // 사이드바 상태에 따라 너비 조절
              overflow: 'hidden',
              transition: 'width 0.5s ease', // 부드러운 토글 효과
            }}>
              {/* 사이드바 내용 */}
              <Typography variant="h6">Sidebar</Typography>
              {/* 사이드바 토글 버튼 */}
              <UserInfoForm />
              <Settings />
          </Box>
          {/* 메인 컨텐츠 영역 */}
          <ToggleArrow isCollapsed={isCollapsed} setIsCollapsed={setIsCollapsed} />

          <Box sx={{ flexGrow: 1, overflow: 'auto', display: 'flex', flexDirection: 'column' }}>

            <Box sx={{ flex: 0.5, my: 4 }}> {/* TextField를 담을 섹션, 비율 30% */}
              <Typography variant="h4" component="h1" gutterBottom>
                AI Assistant 🤓
              </Typography>
              <TextField
                id="outlined-basic"
                label="Ask me Anything"
                multiline
                minRows={2}
                maxRows={6}
                variant="outlined"
                style={{ width: '100%' }}
                value={question}
                disabled={loading}
                onChange={e => setQuestion(e.target.value)}
                onKeyDown={e => {
                  if (e.key === "Enter" && !e.shiftKey) {
                    e.preventDefault(); // Prevent default to avoid newline on Enter
                    handleSendQuestion();
                  }
                }}
              />
              <Button onClick={handleStopClick} disabled={!loading}>
                Stop
              </Button>
            </Box>
            {!response && loading && (
              <>
                <Skeleton />
                <Skeleton animation="wave" />
                <Skeleton animation={false} />
              </>
            )}
            <Box 
              ref={messageHistoryRef} // 여기에 ref를 추가하여 해당 DOM 요소에 접근
              sx={{ flex: 9.5, my: 4, overflow: 'auto' }}> {/* Message History 섹션, 비율 70% */}
              <Typography variant="h6" gutterBottom>
                Message History
              </Typography>
              <List dense={true}>
                {history.map((item, index) => (
                  <ListItem key={index}>
                    <ListItemText
                      primary={<span dangerouslySetInnerHTML={{ __html: `Q: ${marked(item.question)}` }} />}
                      secondary={<span dangerouslySetInnerHTML={{ __html: `A: ${item.response}` }} />}
                    />
                  </ListItem>
                ))}
              </List>
              </Box>
            </Box>
         </Box>
      </Container>
    </ThemeProvider>
  );
}

export default App;
