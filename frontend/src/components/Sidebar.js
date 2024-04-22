import React from 'react';
import { Box, Typography } from '@mui/material';
import UserInfoForm from './userinfoform/userinfoform';
import Settings from './modelsetting/modelsetting';

function Sidebar({ isCollapsed }) {
  return (
    <Box sx={{
      width: isCollapsed ? '240px' : '0',
      overflow: 'hidden',
      transition: 'width 0.5s ease',
    }}>
      <Typography variant="h6">Sidebar</Typography>
      <UserInfoForm />
      <Settings />
    </Box>
  );
}

export default Sidebar;
