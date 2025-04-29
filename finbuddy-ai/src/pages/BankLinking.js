import { useState } from 'react';
import { 
  Container, 
  Box, 
  Typography, 
  Paper, 
  Button,
  Stack
} from '@mui/material';
import { useNavigate } from 'react-router-dom';
import { styled } from '@mui/material/styles';
import AccountBalanceIcon from '@mui/icons-material/AccountBalance';

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

const StyledText = styled(Typography)(({ theme }) => ({
  color: '#2C3E50',
  fontWeight: 'bold',
  textShadow: '0 0 20px rgba(44, 62, 80, 0.2)',
}));

function BankLinking() {
  const navigate = useNavigate();
  const [isLinking, setIsLinking] = useState(false);

  const handleMockLinking = async () => {
    setIsLinking(true);
    try {
      // Simulate API call delay
      await new Promise(resolve => setTimeout(resolve, 2000));
      navigate('/onboarding');
    } catch (err) {
      console.error('Error during mock linking:', err);
    } finally {
      setIsLinking(false);
    }
  };

  return (
    <Box sx={{ 
      minHeight: '100vh',
      background: 'linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%)',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      py: 4
    }}>
      <Container maxWidth="sm">
        <StyledPaper elevation={3}>
          <StyledText variant="h4" align="center" gutterBottom>
            Link Your Bank Accounts
          </StyledText>
          <Typography variant="body1" align="center" sx={{ mb: 4, color: '#34495E' }}>
            To get started with Finbuddy, we need to connect to your bank accounts. 
            This will help us provide personalized financial insights and recommendations.
          </Typography>
          <Stack spacing={2}>
            <Button
              variant="contained"
              startIcon={<AccountBalanceIcon />}
              onClick={handleMockLinking}
              disabled={isLinking}
              fullWidth
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
            >
              {isLinking ? 'Linking...' : 'Mock linking my bank accounts'}
            </Button>
          </Stack>
        </StyledPaper>
      </Container>
    </Box>
  );
}

export default BankLinking; 