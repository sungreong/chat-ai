import React, { createContext, useContext, useState, useEffect } from 'react';

const LLMModelContext = createContext();

export const useLLMParm = () => useContext(LLMModelContext);

const modelSettingsMetadata = {
  "OPENAI": [
    { name: "apiToken", label: "API 토큰", type: "password" , defaultValue: '' , placeholder: 'API 토큰을 입력하세요(sk-...)'},
    { name: 'model', label: '모델', type: 'text', defaultValue: 'gpt-3.5-turbo' },
    { name: 'maxTokens', label: '최대 토큰 수 (maxTokens)', type: 'number', defaultValue: 100 },
    { name: 'topP', label: '상위 P% (topP)', type: 'number', step: '0.01', defaultValue: 0.95 },
    { name: 'temperature', label: '온도 (temperature)', type: 'number', step: '0.01', defaultValue: 0.3 },
    { name: 'frequencyPenalty', label: '빈도 패널티 (frequencyPenalty)', type: 'number', step: '0.01', defaultValue: 0.5 },
    { name: 'presencePenalty', label: '존재 패널티 (presencePenalty)', type: 'number', step: '0.01', defaultValue: 0.5 },
  ],
  "REMOTE": [
    { name: "apiToken", label: "API 토큰", type: "password" , defaultValue: '' , placeholder: 'API 토큰을 입력하세요'},
    { name: "url", label: "API URL", type: "text",  placeholder: 'API URL을 입력하세요(http://...)'},
    { name: 'model', label: '모델', type: 'text', defaultValue: 'custom-model' },
    { name: 'maxTokens', label: '최대 토큰 수 (maxTokens)', type: 'number', defaultValue: 200 },
    { name: 'topP', label: '상위 P% (topP)', type: 'number', step: '0.01', defaultValue: 0.9 },
  ],
  "OLLAMA": [
    {name: "apiToken",label: "API 토큰",
        type: "password",
        defaultValue: '',
        placeholder: 'API 토큰을 입력하세요'
    },
    {
        name: "url",
        label: "EndPoint URL",
        type: "text",
        defaultValue: "http://localhost:11434/api/generate",
        placeholder: 'API URL을 입력하세요(http://...)'
    },
    {
        name: 'model',
        label: '모델 선택 (model)',
        type: 'text',
        defaultValue: 'deepseek-coder:6.7b'
    },
    {
        name: 'num_predict',
        label: '최대 토큰 수 (num_predict)',
        type: 'number',
        defaultValue: 200
    },
    {
        name: 'top_p',
        label: '상위 P% (top_p)',
        type: 'number',
        step: '0.01',
        defaultValue: 0.9
    },
    {
        name: 'stream',
        label: '스트리밍 모드 (stream)',
        type: 'boolean',
        defaultValue: true
    },
    {
        name: 'seed',
        label: '시드 값 (seed)',
        type: 'number',
        defaultValue: 42
    },
    {
        name: 'top_k',
        label: '상위 K (top_k)',
        type: 'number',
        defaultValue: 20
    },
    {
        name: 'temperature',
        label: '온도 (temperature)',
        type: 'number',
        step: '0.1',
        defaultValue: 0.8
    },
    {
        name: 'repeat_penalty',
        label: '반복 패널티 (repeat_penalty)',
        type: 'number',
        step: '0.1',
        defaultValue: 1.2
    },
    {
        name: 'presence_penalty',
        label: '존재 패널티 (presence_penalty)',
        type: 'number',
        step: '0.1',
        defaultValue: 1.5
    },
    {
        name: 'frequency_penalty',
        label: '빈도 패널티 (frequency_penalty)',
        type: 'number',
        step: '0.1',
        defaultValue: 1.0
    },
    {
        name: 'stop',
        label: '종료 문자열 (stop)',
        type: 'text',
        defaultValue: '\\n, user:'
    }
]
  // 추가 모델 설정 메타데이터
};

export const LLMParamProvider = ({ children }) => {
  const [currentModel, setCurrentModel] = useState('OPENAI');
  // const [allModelMetadata, setAllModelMetadata] = useState(modelSettingsMetadata);
  const [allModelSettings, setAllModelSettings] = useState(modelSettingsMetadata); // 모든 모델의 설정을 저장
  const [modelSettings, setModelSettings] = useState(allModelSettings[currentModel]);

  const handleModelChange = (modelKey) => {
    setCurrentModel(modelKey);
    // 모델 변경 시 특별한 설정 업데이트 로직이 필요한 경우 여기에 추가
  };

  const handleModelSettingsChange = (newSettings) => {
    console.log('newSettings:', newSettings,currentModel);

    setAllModelSettings(prevSettings => ({
      ...prevSettings,
      [currentModel]: newSettings,
    }));

    setModelSettings(newSettings);

  };
  useEffect(() => {
    // currentModel이 변경될 때마다 modelSettings 업데이트
    setModelSettings(allModelSettings[currentModel]);
  }, [currentModel, allModelSettings]);


  return (
    <LLMModelContext.Provider value={{ 
      modelSettings,
      currentModel, 
      allModelSettings,
      handleModelChange,
      handleModelSettingsChange, // 변경된 handleModelSettingsChange 함수를 전달
    }}>
      {children}
    </LLMModelContext.Provider>
  );
};
