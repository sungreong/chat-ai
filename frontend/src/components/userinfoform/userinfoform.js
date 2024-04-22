import hljs from 'highlight.js';
import 'highlight.js/styles/github.css'; // 원하는 스타일을 선택하세요
import React, { useState, useEffect } from 'react';
import ReactDOM from 'react-dom';

import { TextField, Button, Box } from '@mui/material';
import { useUser} from './../../contexts/UserContext';
// PrettyJson 컴포넌트
const PrettyJson = ({ jsonData, onClose }) => {
  useEffect(() => {
    hljs.highlightAll();
  }, [jsonData]);

  const modalStyle = {
    position: 'fixed', 
    top: '20%', 
    left: '20%', 
    backgroundColor: 'white', 
    padding: '20px', 
    zIndex: 1000, 
    boxShadow: '0 4px 8px 0 rgba(0,0,0,0.2)',
    maxWidth: '60%',
    maxHeight: '60%',
    width: '50%',
    height: '50%',
    overflow: 'auto'
  };

  const prettyJson = JSON.stringify(jsonData, null, 2);

  // ReactDOM.createPortal을 사용하여 모달을 document.body에 직접 렌더링
  return ReactDOM.createPortal(
    (
      <div style={modalStyle}>
        <button onClick={onClose} style={{ float: 'right', fontSize: '16px' }}>닫기</button>
        <pre><code className="json">{prettyJson}</code></pre>
      </div>
    ),
    document.body  // 이 부분이 변경되었습니다.
  );
};


const UserInfoForm = () => {
  const { user, setUser } = useUser();
  const [parameters, setParameters] = useState('');
  const [showJson, setShowJson] = useState(false);

  // 사용자 정보를 백엔드로부터 불러오는 함수
  const fetchUserInfo = async (userId) => {
    try {
      const response = await fetch(`http://localhost:8000/users/${userId}`, {
        headers: {
          'Accept': 'application/json',
        },
      });      
      if (!response.ok) {
        throw new Error('Failed to fetch user info');
      }
      const data = await response.json();

      // 사용자 정보를 폼에 설정
      setParameters(data);
      setShowJson(true);
    } catch (error) {
      console.error('Error fetching user info:', error);
      alert('사용자 정보를 불러오는 데 실패했습니다.');
    }
  };

  return (
    <Box sx={{ '& > :not(style)': { m: 1 } }}>
      <TextField
        label="User ID"
        value={user}
        onChange={(e) => setUser(e.target.value)}
        required
      />
      <Button variant="contained" onClick={() => fetchUserInfo(user)}>불러오기</Button>
      {showJson && <PrettyJson jsonData={parameters} onClose={() => setShowJson(false)} />}
    </Box>
  );
};

export default UserInfoForm;
