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

const GradientText = styled(Typography)(({ theme }) => ({
  background: 'linear-gradient(45deg, #2196F3 30%, #21CBF3 90%)',
  WebkitBackgroundClip: 'text',
  WebkitTextFillColor: 'transparent',
  fontWeight: 'bold',
}));

const StyledPaper = styled(Paper)(({ theme }) => ({
  background: 'rgba(255, 255, 255, 0.9)',
  backdropFilter: 'blur(10px)',
  borderRadius: '20px',
  padding: theme.spacing(4),
  boxShadow: '0 8px 32px 0 rgba(31, 38, 135, 0.37)',
}));

function Home() {
  const navigate = useNavigate();
  const theme = useTheme();

  return (
    <Box sx={{ 
      minHeight: '100vh',
      background: 'linear-gradient(135deg, #1a1a1a 0%, #2a2a2a 100%)',
      display: 'flex',
      flexDirection: 'column'
    }}>
      <AppBar position="static" sx={{ background: 'transparent', boxShadow: 'none' }}>
        <Toolbar>
          <Typography variant="h6" component="div" sx={{ flexGrow: 1, color: 'white' }}>
            FinBuddy AI
          </Typography>
          <Button 
            variant="outlined" 
            sx={{ 
              color: 'white', 
              borderColor: 'white',
              '&:hover': {
                borderColor: '#2196F3',
                backgroundColor: 'rgba(33, 150, 243, 0.1)'
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
            <GradientText variant="h2" gutterBottom>
              FinBuddy AI
            </GradientText>
            <Typography 
              variant="h6" 
              sx={{ 
                color: theme.palette.text.secondary,
                maxWidth: '600px',
                margin: '0 auto',
                lineHeight: 1.6,
                mb: 4
              }}
            >
              A comprehensive, step-by-step plan focused on expense management, built as a web app with chat, dashboard, and SMS integration.
            </Typography>
            <Button 
              variant="contained" 
              size="large"
              sx={{
                background: 'linear-gradient(45deg, #2196F3 30%, #21CBF3 90%)',
                borderRadius: '25px',
                padding: '10px 30px',
                '&:hover': {
                  background: 'linear-gradient(45deg, #1976D2 30%, #1E88E5 90%)',
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