import React, { useState, useEffect } from 'react';
import { Box, Typography, TextField, Button, List, ListItem, ListItemText } from '@mui/material';
import { useWebSocket } from '../contexts/WebSocketContext';
import { marked } from 'marked';
import hljs from 'highlight.js';

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

function GeneralChat() {
    const [question, setQuestion] = useState('');
    const [loading, setLoading] = useState(false);
    const { sendMessage, stopMessage, generalHistory } = useWebSocket(); // Assuming stopMessage is available

    useEffect(() => {
        if (generalHistory.length && !loading) {
            // Assuming generalHistory updates could reflect in UI changes post message sending
            console.log("New message in history, updated UI accordingly");
        }
    }, [generalHistory, loading]);

    const handleSendQuestion = async () => {
        if (!question.trim() || loading) return;
        setLoading(true);
        await sendMessage({
            type: 'general',
            content: question,
            questionId: Date.now().toString()  // Managing uniqueness with timestamps
        },setLoading);
        setQuestion('');
    };

    const handleStopClick = () => {
        console.log("Stopping the operation");
        stopMessage(); // Call stopMessage from WebSocket context to signal stopping the operation
        setLoading(false); // Update loading state to reflect the UI change
    };

    return (
        <Box sx={{ flex: 1, my: 4 }}>
            <Typography variant="h4" gutterBottom>AI Assistant 🤓</Typography>
            <TextField
                label="Ask me Anything"
                multiline
                minRows={2}
                maxRows={6}
                variant="outlined"
                fullWidth
                value={question}
                onChange={(e) => setQuestion(e.target.value)}
                onKeyDown={e => {
                  if (e.key === "Enter" && !e.shiftKey) {
                    e.preventDefault(); // Prevent default to avoid newline on Enter
                    handleSendQuestion();
                  }
                }}
                disabled={loading}
            />
            <Button onClick={handleSendQuestion} disabled={loading || !question.trim()}>
                Send
            </Button>
            <Button onClick={handleStopClick} disabled={!loading}>
                Stop
            </Button>
            <List dense={true}>
                {generalHistory.map((item, index) => (
                    <ListItem key={index}>
                        <ListItemText
                        primary={<span dangerouslySetInnerHTML={{ __html: `Q: ${marked(item.question)}` }} />}
                        secondary={<span dangerouslySetInnerHTML={{ __html: `A: ${item.response}` }} />}
                        />
                    </ListItem>
                ))}
            </List>
        </Box>
    );
}

export default GeneralChat;
