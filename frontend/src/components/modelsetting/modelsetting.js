import React, { useEffect, useState } from 'react';
import ReactDOM from 'react-dom';
import styles from './modelsetting.module.css';
import { useLLMParm } from '../../contexts/LLMParam'; // 경로는 실제 구조에 맞게 조정하세요
import { useUser } from '../../contexts/UserContext';
import CustomPasswordInput from './../passwordinput/passwordinput'; // 경로는 실제 구조에 맞게 조정하세요
// import VisibilityIcon from '@material-ui/icons/Visibility';
// import VisibilityOffIcon from '@material-ui/icons/VisibilityOff';

function SettingsFields({ selectedModel, modelSettings, handleModelSettingInputChange, allModelSettings }) {

  const settingsArray = Object.values(modelSettings).filter(setting => typeof setting === 'object');

  return (
    <>
      {settingsArray.map((setting,index) => (
        <div key={`${selectedModel}-${setting.name}`} className={styles.formGroup}>
          {setting.name === 'apiToken' && (
            <React.Fragment>
              <label htmlFor={`${selectedModel}-${setting.name}`} className={styles.label}>API Token:</label>
              <CustomPasswordInput
                id={`${selectedModel}-${setting.name}`}
                name={setting.name}
                placeholder={setting.placeholder}
                value={setting.defaultValue || ''}
                onChange={handleModelSettingInputChange}
              />
            </React.Fragment>
          )}
          {setting.name !== 'apiToken' && (
            <React.Fragment>
              <label htmlFor={`${selectedModel}-${setting.name}`} className={styles.label}>{setting.label}:</label>
              <input
                id={`${selectedModel}-${setting.name}`}
                type={setting.type}
                name={setting.name}
                className={styles.inputField}
                placeholder={setting.placeholder || ''}
                value={setting.defaultValue || ''}
                onChange={handleModelSettingInputChange}
                step={setting.step || 'any'}
              />
            </React.Fragment>
          )}

        </div>
      ))}
    </>
  );
}


function SettingsModal({ onClose}) {
  const { 
    modelSettings, 
    currentModel, 
    allModelSettings, 
    handleModelSettingsChange, 
    handleModelChange 
  } = useLLMParm();
  const { user } = useUser(); // 사용자 정보 컨텍스트에서 사용자 정보 가져오기  
  const [selectedModel, setSelectedModel] = useState(currentModel); // Initialize with currentModel from context

  const saveSettingsToBackend = async () => {
    // 사용자 ID와 모델 설정 정보를 포함하여 백엔드로 전송
    // 예시로 'user123'을 사용자 ID로 설정합니다. 실제 구현에서는 적절한 사용자 ID를 사용하세요.
    try {
      console.log('user:', user); 
      console.log('selectedModel:', selectedModel);
      console.log('modelSettings:', modelSettings);
      console.log(JSON.stringify({
        model_type: selectedModel,
        parameters: modelSettings
      }))

      const modelSettingsObj = modelSettings.reduce((acc, setting) => {
        acc[setting.name] = setting.defaultValue;
        return acc;
      }, {});
      const response = await fetch(`http://localhost:8000/users/${encodeURIComponent(user)}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          // 필요에 따라 추가 헤더를 설정할 수 있습니다.
        },
        body: JSON.stringify({
            model_type: selectedModel,
            parameters: modelSettingsObj,
            // 
          })
      });
  
      if (!response.ok) {
        throw new Error('Failed to save settings to backend');
      }
  
      // 응답 처리
      const data = await response.json();
      console.log('Settings saved successfully:', data);
      onClose(); // 모달 닫기
    } catch (error) {
      console.error('Error saving settings:', error);
      alert('설정을 저장하는 데 실패했습니다.');
      // 필요하다면 여기에서 에러 처리 로직을 추가하세요.
    }
  };
  

  // 모델 설정 입력 처리
  const handleModelSelectChange = (e) => {
    const model = e.target.value;
    setSelectedModel(model); // 선택된 모델 상태 업데이트
    handleModelChange(model); // Context 내의 모델 변경 처리
  };

  const handleModelSettingInputChange = (e) => {
    const { name, value } = e.target;
  
    // 입력 값을 적절히 변환 (숫자 또는 원본 문자열)
    let parsedValue = parseFloat(value);
    parsedValue = isNaN(parsedValue) ? value : parsedValue;
  
    // 변경할 설정을 찾아 defaultValue 업데이트
    const updatedSettingsArray = modelSettings.map(setting => {
      if (setting.name === name) {
        return { ...setting, defaultValue: parsedValue };
      }
      return setting;
    });
  
    // 상위 컴포넌트 또는 전역 상태 관리 로직을 통해 전체 설정 업데이트
    handleModelSettingsChange(updatedSettingsArray);
  };
  
  
  return ReactDOM.createPortal(
    <div className={styles.modalOverlay}>
      <div className={styles.modalWindow}>
        <h2 className={styles.modalTitle}>API 설정</h2>
        <form className={styles.modalForm} onSubmit={(e) => e.preventDefault()}>
          <div className={styles.formGroup}>
            <label htmlFor="modelSelect" className={styles.label}>모델 선택:</label>
            <select 
              id="modelSelect" 
              className={styles.selectField} 
              value={selectedModel} 
              onChange={handleModelSelectChange}
            >
              {Object.keys(allModelSettings).map((modelKey) => (
                <option key={modelKey} value={modelKey}>{modelKey}</option>
              ))}
            </select>
          </div>
          <SettingsFields 
            selectedModel={selectedModel}
            modelSettings={modelSettings}
            handleModelSettingInputChange={handleModelSettingInputChange}
            allModelSettings={allModelSettings}
          />          
          <div className={styles.buttonsContainer}>
            <button type="button" onClick={onClose} className={`${styles.button} ${styles.cancelButton}`}>
              취소
            </button>
            <button type="submit" onClick={saveSettingsToBackend} className={`${styles.button} ${styles.saveButton}`}>
              저장
            </button>
          </div>
        </form>
      </div>
    </div>,
    document.body
  );
}

function Settings() {
  const [isModalOpen, setIsModalOpen] = useState(false);
  const openModal = () => setIsModalOpen(true);
  const closeModal = () => setIsModalOpen(false);
  return (
    <div>
      <button type="button" onClick={openModal} className={styles.settingsButton}>
        Model 설정
      </button>
      {isModalOpen && (
        <SettingsModal
          onClose={closeModal}
        />
      )}
    </div>
  );
}

export default Settings;
