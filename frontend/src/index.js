import React from 'react';
import ReactDOM from 'react-dom/client';
import './index.css';
import App from './App';
import { LLMParamProvider } from './contexts/LLMParam';
import { UserProvider } from './contexts/UserContext'; // UserProvider를 임포트

const root = ReactDOM.createRoot(document.getElementById('root'));
root.render(
    <UserProvider> {/* UserProvider 추가 */}
        <LLMParamProvider>
            <App />
        </LLMParamProvider>
    </UserProvider>
);

// If you want to start measuring performance in your app, pass a function
// to log results (for example: reportWebVitals(console.log))
// or send to an analytics endpoint. Learn more: https://bit.ly/CRA-vitals
