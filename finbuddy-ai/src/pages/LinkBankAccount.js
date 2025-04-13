import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { 
  Container, 
  Box, 
  Typography, 
  Paper,
  Button,
  Stack
} from '@mui/material';
import { styled } from '@mui/material/styles';

const StyledPaper = styled(Paper)(({ theme }) => ({
  background: 'rgba(255, 255, 255, 0.9)',
  backdropFilter: 'blur(10px)',
  borderRadius: '20px',
  padding: theme.spacing(4),
  boxShadow: '0 8px 32px 0 rgba(31, 38, 135, 0.37)',
  maxWidth: '600px',
  margin: '0 auto',
}));

const LinkBankAccount = () => {
  const navigate = useNavigate();
  const [isLinked, setIsLinked] = useState(false);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    checkBankStatus();
  }, [navigate, checkBankStatus]);

  const checkBankStatus = async () => {
    const token = localStorage.getItem('token');
    if (!token) {
      navigate('/login');
      return;
    }

    try {
      const response = await fetch('http://localhost:8000/bank/data', {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });
      
      if (response.ok) {
        setIsLinked(true);
      } else {
        setIsLinked(false);
      }
    } catch (error) {
      setIsLinked(false);
    } finally {
      setLoading(false);
    }
  };

  const handleLinkAccount = async () => {
    const token = localStorage.getItem('token');
    if (!token) {
      navigate('/login');
      return;
    }

    try {
      setLoading(true);
      const response = await fetch('http://localhost:8000/bank/link', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });

      if (!response.ok) {
        throw new Error('Failed to link bank account');
      }

      setIsLinked(true);
      navigate('/dashboard');
    } catch (error) {
      setError('Failed to link bank account. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleDisconnect = async () => {
    const token = localStorage.getItem('token');
    if (!token) {
      navigate('/login');
      return;
    }

    try {
      setLoading(true);
      const response = await fetch('http://localhost:8000/bank/disconnect', {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });

      if (!response.ok) {
        throw new Error('Failed to disconnect bank account');
      }

      setIsLinked(false);
    } catch (error) {
      setError('Failed to disconnect bank account. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <Box sx={{ 
        minHeight: '100vh',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center'
      }}>
        <Typography>Loading...</Typography>
      </Box>
    );
  }

  return (
    <Box sx={{ 
      minHeight: '100vh',
      background: 'linear-gradient(135deg, #1a1a1a 0%, #2a2a2a 100%)',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      py: 4
    }}>
      <Container maxWidth="sm">
        <StyledPaper elevation={3}>
          <Typography variant="h4" align="center" gutterBottom>
            Bank Account
          </Typography>
          {error && (
            <Typography color="error" align="center" gutterBottom>
              {error}
            </Typography>
          )}
          
          {isLinked ? (
            <Box sx={{ textAlign: 'center' }}>
              <Typography variant="body1" gutterBottom>
                Your bank account is currently linked.
              </Typography>
              <Stack spacing={2} sx={{ mt: 3 }}>
                <Button
                  variant="contained"
                  onClick={handleDisconnect}
                  disabled={loading}
                  sx={{
                    background: 'linear-gradient(45deg, #f44336 30%, #ff5252 90%)',
                    borderRadius: '25px',
                    padding: '10px 30px',
                    '&:hover': {
                      background: 'linear-gradient(45deg, #d32f2f 30%, #f44336 90%)',
                    }
                  }}
                >
                  Disconnect Bank Account
                </Button>
                <Button
                  variant="contained"
                  onClick={() => navigate('/dashboard')}
                  sx={{
                    background: 'linear-gradient(45deg, #2196F3 30%, #21CBF3 90%)',
                    borderRadius: '25px',
                    padding: '10px 30px',
                    '&:hover': {
                      background: 'linear-gradient(45deg, #1976D2 30%, #1E88E5 90%)',
                    }
                  }}
                >
                  Go to Dashboard
                </Button>
              </Stack>
            </Box>
          ) : (
            <Box sx={{ textAlign: 'center' }}>
              <Typography variant="body1" gutterBottom>
                Link your bank account to get started with financial insights.
              </Typography>
              <Stack spacing={2} sx={{ mt: 3 }}>
                <Button
                  variant="contained"
                  onClick={handleLinkAccount}
                  disabled={loading}
                  sx={{
                    background: 'linear-gradient(45deg, #2196F3 30%, #21CBF3 90%)',
                    borderRadius: '25px',
                    padding: '10px 30px',
                    '&:hover': {
                      background: 'linear-gradient(45deg, #1976D2 30%, #1E88E5 90%)',
                    }
                  }}
                >
                  Link Bank Account
                </Button>
                <Button
                  variant="contained"
                  onClick={() => navigate('/dashboard')}
                  sx={{
                    background: 'linear-gradient(45deg, #2196F3 30%, #21CBF3 90%)',
                    borderRadius: '25px',
                    padding: '10px 30px',
                    '&:hover': {
                      background: 'linear-gradient(45deg, #1976D2 30%, #1E88E5 90%)',
                    }
                  }}
                >
                  Back to Dashboard
                </Button>
              </Stack>
            </Box>
          )}
        </StyledPaper>
      </Container>
    </Box>
  );
};

export default LinkBankAccount; 