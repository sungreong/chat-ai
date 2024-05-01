import React, { createContext, useContext, useEffect, useRef, useState } from 'react';
import { marked } from 'marked';
import { useUser } from './UserContext';

const WebSocketContext = createContext(null);

export const WebSocketProvider = ({ children }) => {
    const [generalHistory, setGeneralHistory] = useState([]);
    const [sqlHistory, setSqlHistory] = useState([]);
    const { user, setUser } = useUser();

    const ws = useRef(null);
    // Inside your component
    useEffect(() => {
      console.log("Updated generalHistory:", generalHistory);
    }, [generalHistory]); // This useEffect will run after generalHistory changes.

    // TODO: USER 정보
    const sendMessage = (message, setLoading) => {
      if (!ws.current || ws.current.readyState !== WebSocket.OPEN) {
          ws.current = new WebSocket(`ws://localhost:8000/ws/${user}`);
          ws.current.onmessage = (event) => {
            
            const eventData = JSON.parse(event.data);
            // console.log("onmessage", eventData.content)
            const parsedResponse = marked.parse(eventData.content);
            // Update response and history
            const updateHistory = message.type === 'general' ? setGeneralHistory : setSqlHistory;
            // console.log("parsedResponse", updateHistory)
            updateHistory(prevHistory => prevHistory.map(item =>
              item.id === eventData.id ? { ...item, response: parsedResponse } : item
            ));
            // Set loading to false after receiving the response
            if (eventData.is_last) {
              console.log("terminate...")
              ws.current.close();
              ws.current = null; // Ensure the reference is cleared
              setLoading(false); // Update loading state to reflect the UI change
            }
          };
    
          ws.current.onopen = () => {
            // Send question once WebSocket is open
            sendQuestion(message);
          };
    
          ws.current.onerror = (error) => {
            console.error("WebSocket Error: ", error);
            // Handle WebSocket error (e.g., show an error message)
          };        } 
      else {
          sendQuestion(message);
      }
    };
    const sendQuestion = (message) => {
      console.log("message_type", message.type)
      const updateHistory = message.type === 'general' ? setGeneralHistory : setSqlHistory;
      updateHistory(prevHistory => [...prevHistory, { id: message.questionId, question : message.content, response: "" }]);
      console.log("generalHistory", generalHistory)
      try {
        ws.current.send(JSON.stringify({ id: message.questionId, question : message.content }));
      } catch (error) {
        console.error("Sending Question Error: ", error);
      }
    };
    const stopMessage = async () => {
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
        console.log("ws", ws)
        // WebSocket 연결이 열려있다면 닫습니다.
        if (ws.current && ws.current.readyState === WebSocket.OPEN) {
          // ws.current.close();
          console.log('WebSocket connection closed.');
          ws.current.close();
          ws.current = null; // Ensure the reference is cleared
        }
      } catch (error) {
        console.error('Failed to send cancel request:', error);
      }
    };

    return (
        <WebSocketContext.Provider value={{ generalHistory, sqlHistory, sendMessage, stopMessage }}>
            {children}
        </WebSocketContext.Provider>
    );
};

export const useWebSocket = () => useContext(WebSocketContext);
