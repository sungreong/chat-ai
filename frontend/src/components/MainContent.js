import React, { useState } from 'react';
import { Box, Tabs, Tab } from '@mui/material';
import GeneralChat from './GeneralChat';
import SQLQueries from './SQLQueries';
import TabPanel from './TabPanel';
// import { a11yProps } from './utils';

function a11yProps(index) {
    return {
      id: `simple-tab-${index}`,
      'aria-controls': `simple-tabpanel-${index}`,
    };
  }
function MainContent() {
  const [tabIndex, setTabIndex] = useState(0);
  
  const handleTabChange = (event, newValue) => {
    setTabIndex(newValue);
  };

  return (
    <Box sx={{ flexGrow: 1, overflow: 'auto', display: 'flex', flexDirection: 'column' }}>
      <Tabs value={tabIndex} onChange={handleTabChange} aria-label="basic tabs example">
        <Tab label="General Chat" {...a11yProps(0)} />
        <Tab label="SQL Queries" {...a11yProps(1)} />
      </Tabs>
      <TabPanel value={tabIndex} index={0}>
        <GeneralChat />
      </TabPanel>
      <TabPanel value={tabIndex} index={1}>
        <SQLQueries />
      </TabPanel>
    </Box>
  );
}

export default MainContent;
