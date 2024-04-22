import React, { useRef, useEffect } from 'react';
import { Box, Typography, TextField, Button, List, ListItem, ListItemText } from '@mui/material';
import { marked } from 'marked';

function SQLQueries({ question, setQuestion, handleSendQuestion,handleStopClick, loading, history }) {
  const sqlHistoryRef = useRef(null);

  useEffect(() => {
    if (sqlHistoryRef.current) {
      sqlHistoryRef.current.scrollTop = sqlHistoryRef.current.scrollHeight;
    }
  }, [history]);

  return (
    <Box sx={{ flex: 1, my: 4 }}>
      <Typography variant="h4" component="h1" gutterBottom>SQL Queries 📊</Typography>
      <TextField
        label="Enter SQL Query"
        multiline
        minRows={2}
        maxRows={6}
        variant="outlined"
        fullWidth
        value={question}
        disabled={loading}
        onChange={(e) => setQuestion(e.target.value)}
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
      <Typography variant="h6" gutterBottom>
        Message History
      </Typography>
      <List dense={true} ref={sqlHistoryRef}>
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
  );
}

export default SQLQueries;
