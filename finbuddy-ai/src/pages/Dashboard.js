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

function Dashboard() {
  const navigate = useNavigate();
  const [bankData, setBankData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    const token = localStorage.getItem('token');
    if (!token) {
      navigate('/login');
      return;
    }

    const fetchBankData = async () => {
      try {
        const response = await fetch('http://localhost:8000/bank/data', {
          headers: {
            'Authorization': `Bearer ${token}`
          }
        });

        if (!response.ok) {
          throw new Error('Failed to fetch bank data');
        }

        const data = await response.json();
        setBankData(data);
      } catch (err) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    };

    fetchBankData();
  }, [navigate]);

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
            Dashboard
          </Typography>
          {error && (
            <Typography color="error" align="center" gutterBottom>
              {error}
            </Typography>
          )}
          
          {bankData ? (
            <Box>
              <Typography variant="h6" gutterBottom>
                Account Balance: ${bankData.account.balances.current.toFixed(2)}
              </Typography>
              <Typography variant="subtitle1" gutterBottom>
                Account: {bankData.account.name} (****{bankData.account.mask})
              </Typography>
              
              <Typography variant="h6" sx={{ mt: 3 }} gutterBottom>
                Recent Transactions
              </Typography>
              {bankData.transactions.slice(0, 5).map((transaction) => (
                <Box key={transaction.transaction_id} sx={{ mb: 2 }}>
                  <Typography variant="body1">
                    {transaction.name} - ${Math.abs(transaction.amount).toFixed(2)}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    {new Date(transaction.date).toLocaleDateString()} - {transaction.category}
                  </Typography>
                </Box>
              ))}
              
              <Stack spacing={2} sx={{ mt: 3 }}>
                <Button
                  variant="contained"
                  onClick={() => navigate('/link-bank')}
                  sx={{
                    background: 'linear-gradient(45deg, #2196F3 30%, #21CBF3 90%)',
                    borderRadius: '25px',
                    padding: '10px 30px',
                    '&:hover': {
                      background: 'linear-gradient(45deg, #1976D2 30%, #1E88E5 90%)',
                    }
                  }}
                >
                  Manage Bank Account
                </Button>
              </Stack>
            </Box>
          ) : (
            <Box sx={{ textAlign: 'center' }}>
              <Typography variant="body1" gutterBottom>
                No bank account linked yet.
              </Typography>
              <Button
                variant="contained"
                onClick={() => navigate('/link-bank')}
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
            </Box>
          )}
        </StyledPaper>
      </Container>
    </Box>
  );
}

export default Dashboard; 