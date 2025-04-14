import { Box, Typography, Paper, Button } from '@mui/material';
import { styled } from '@mui/material/styles';
import { useNavigate } from 'react-router-dom';
import SmartToyIcon from '@mui/icons-material/SmartToy';

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

  return (
    <Box sx={{ p: 3 }}>
      <StyledPaper elevation={3}>
        <Typography variant="h4" sx={{ color: '#2C3E50', fontWeight: 'bold', mb: 3 }}>
          Welcome to Finbuddy
        </Typography>
        <Typography variant="body1" sx={{ color: '#2C3E50', mb: 4 }}>
          Your personal financial assistant is here to help you manage your finances, set goals, and make better financial decisions.
        </Typography>
        <Button
          variant="contained"
          color="primary"
          size="large"
          startIcon={<SmartToyIcon />}
          onClick={() => navigate('/onboarding-chat')}
          sx={{
            borderRadius: '12px',
            padding: '12px 24px',
            fontSize: '1.1rem',
            textTransform: 'none',
            boxShadow: '0 4px 12px rgba(0, 0, 0, 0.1)',
            '&:hover': {
              boxShadow: '0 6px 16px rgba(0, 0, 0, 0.15)',
            }
          }}
        >
          Start Onboarding Chat
        </Button>
      </StyledPaper>
    </Box>
  );
}

export default Home; 