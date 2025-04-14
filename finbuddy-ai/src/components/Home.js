import React from 'react';
import { 
  AppBar, 
  Toolbar, 
  Typography, 
  Container, 
  Box, 
  Button,
  useTheme,
  Paper
} from '@mui/material';
import { styled } from '@mui/material/styles';
import { useNavigate } from 'react-router-dom';

const StyledText = styled(Typography)(({ theme }) => ({
  color: '#2C3E50',
  fontWeight: 'bold',
  textShadow: '0 0 20px rgba(44, 62, 80, 0.2)',
}));

const StyledPaper = styled(Paper)(({ theme }) => ({
  background: 'white',
  borderRadius: '20px',
  padding: theme.spacing(4),
  boxShadow: '0 4px 20px rgba(0, 0, 0, 0.1)',
  transition: 'transform 0.2s ease-in-out, box-shadow 0.2s ease-in-out',
  '&:hover': {
    transform: 'translateY(-5px)',
    boxShadow: '0 8px 30px rgba(0, 0, 0, 0.15)',
  },
}));

function Home() {
  const navigate = useNavigate();
  const theme = useTheme();

  return (
    <Box sx={{ 
      minHeight: '100vh',
      background: 'linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%)',
      display: 'flex',
      flexDirection: 'column'
    }}>
      <AppBar position="static" sx={{ 
        background: 'rgba(255, 255, 255, 0.9)',
        boxShadow: '0 2px 10px rgba(0, 0, 0, 0.1)',
        backdropFilter: 'blur(10px)',
      }}>
        <Toolbar>
          <Typography variant="h6" component="div" sx={{ flexGrow: 1, color: '#2C3E50' }}>
            FinBuddy AI
          </Typography>
          <Button 
            variant="outlined" 
            sx={{ 
              color: '#2C3E50', 
              borderColor: '#2C3E50',
              '&:hover': {
                borderColor: '#1a252f',
                backgroundColor: 'rgba(44, 62, 80, 0.1)'
              }
            }}
            onClick={() => navigate('/login')}
          >
            Login
          </Button>
        </Toolbar>
      </AppBar>

      <Container maxWidth="md" sx={{ flex: 1, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
        <StyledPaper elevation={3}>
          <Box sx={{ textAlign: 'center' }}>
            <StyledText variant="h2" gutterBottom>
              FinBuddy AI
            </StyledText>
            <Typography 
              variant="h6" 
              sx={{ 
                color: '#34495E',
                maxWidth: '600px',
                margin: '0 auto',
                lineHeight: 1.6,
                mb: 4,
                textShadow: '0 0 10px rgba(0, 0, 0, 0.1)',
                fontWeight: 500
              }}
            >
              A comprehensive, step-by-step plan focused on expense management, built as a web app with chat, dashboard, and SMS integration.
            </Typography>
            <Button 
              variant="contained" 
              size="large"
              sx={{
                background: '#2C3E50',
                borderRadius: '25px',
                padding: '10px 30px',
                boxShadow: '0 4px 15px rgba(44, 62, 80, 0.3)',
                textShadow: '0 0 10px rgba(0, 0, 0, 0.1)',
                '&:hover': {
                  background: '#1a252f',
                  boxShadow: '0 6px 20px rgba(44, 62, 80, 0.4)',
                }
              }}
              onClick={() => navigate('/signup')}
            >
              Get Started
            </Button>
          </Box>
        </StyledPaper>
      </Container>
    </Box>
  );
}

export default Home; 