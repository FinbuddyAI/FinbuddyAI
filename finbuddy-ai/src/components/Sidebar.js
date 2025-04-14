import { useState } from 'react';
import { 
  Box, 
  Drawer, 
  List, 
  ListItem, 
  ListItemIcon, 
  ListItemText, 
  Typography,
  Divider,
  ListItemButton,
  useTheme,
  useMediaQuery
} from '@mui/material';
import { 
  Home as HomeIcon,
  Chat as ChatIcon,
  Flag as GoalsIcon,
  Analytics as AnalyticsIcon,
  Person as ProfileIcon,
  Settings as SettingsIcon
} from '@mui/icons-material';
import { useNavigate, useLocation } from 'react-router-dom';
import { styled } from '@mui/material/styles';

const drawerWidth = 240;

const StyledDrawer = styled(Drawer)(({ theme }) => ({
  width: drawerWidth,
  flexShrink: 0,
  '& .MuiDrawer-paper': {
    width: drawerWidth,
    boxSizing: 'border-box',
    background: 'white',
    borderRight: 'none',
    boxShadow: '0 4px 20px rgba(0, 0, 0, 0.1)',
  },
}));

const LogoBox = styled(Box)(({ theme }) => ({
  padding: theme.spacing(2),
  display: 'flex',
  alignItems: 'center',
  justifyContent: 'center',
  borderBottom: `1px solid ${theme.palette.divider}`,
}));

const LogoText = styled(Typography)(({ theme }) => ({
  color: '#2C3E50',
  fontWeight: 'bold',
  fontSize: '1.5rem',
  textShadow: '0 0 20px rgba(44, 62, 80, 0.2)',
}));

const StyledListItemButton = styled(ListItemButton)(({ theme, selected }) => ({
  borderRadius: '8px',
  margin: theme.spacing(0.5, 1),
  '&.Mui-selected': {
    backgroundColor: 'rgba(44, 62, 80, 0.1)',
    '&:hover': {
      backgroundColor: 'rgba(44, 62, 80, 0.15)',
    },
  },
  '&:hover': {
    backgroundColor: 'rgba(44, 62, 80, 0.05)',
  },
}));

const menuItems = [
  { text: 'Home', icon: <HomeIcon />, path: '/home' },
  { text: 'Chat', icon: <ChatIcon />, path: '/chat' },
  { text: 'Goals', icon: <GoalsIcon />, path: '/goals' },
  { text: 'Analytics', icon: <AnalyticsIcon />, path: '/analytics' },
  { text: 'Profile', icon: <ProfileIcon />, path: '/profile' },
  { text: 'Settings', icon: <SettingsIcon />, path: '/settings' },
];

function Sidebar() {
  const navigate = useNavigate();
  const location = useLocation();
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('md'));

  const handleNavigation = (path) => {
    navigate(path);
  };

  return (
    <StyledDrawer
      variant={isMobile ? 'temporary' : 'permanent'}
      anchor="left"
      open={true}
    >
      <LogoBox>
        <LogoText>Finbuddy</LogoText>
      </LogoBox>
      <Divider />
      <List>
        {menuItems.map((item) => (
          <ListItem key={item.text} disablePadding>
            <StyledListItemButton
              selected={location.pathname === item.path}
              onClick={() => handleNavigation(item.path)}
            >
              <ListItemIcon sx={{ color: '#2C3E50' }}>
                {item.icon}
              </ListItemIcon>
              <ListItemText 
                primary={item.text} 
                sx={{ 
                  color: '#2C3E50',
                  '& .MuiTypography-root': {
                    fontWeight: location.pathname === item.path ? 'bold' : 'normal',
                  }
                }}
              />
            </StyledListItemButton>
          </ListItem>
        ))}
      </List>
    </StyledDrawer>
  );
}

export default Sidebar; 