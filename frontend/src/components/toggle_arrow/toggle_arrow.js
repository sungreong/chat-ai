import React from 'react';
import styles from "./toggle_arrow.module.css"; // CSS 모듈 임포트

function ToggleArrow({ isCollapsed, setIsCollapsed }) {
    const toggleSidebar = () => {
        setIsCollapsed(!isCollapsed);
    };

    return (
        <div className={styles['toggle-container']} onClick={toggleSidebar}>
            <div className={`${styles['arrow']} ${isCollapsed ? styles['collapsed'] : ''}`}></div>
        </div>
    );
}

export default ToggleArrow;
