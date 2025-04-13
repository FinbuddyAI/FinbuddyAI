import { useState, useEffect } from 'react';
import { 
  Container, 
  Box, 
  Typography, 
  Paper,
  Button,
  Stack,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Chip
} from '@mui/material';
import { useNavigate } from 'react-router-dom';
import { styled } from '@mui/material/styles';

const StyledPaper = styled(Paper)(({ theme }) => ({
  background: 'rgba(255, 255, 255, 0.9)',
  backdropFilter: 'blur(10px)',
  borderRadius: '20px',
  padding: theme.spacing(4),
  boxShadow: '0 8px 32px 0 rgba(31, 38, 135, 0.37)',
  maxWidth: '800px',
  margin: '0 auto',
}));

const TransactionPaper = styled(Paper)(({ theme }) => ({
  marginTop: theme.spacing(3),
  maxHeight: '400px',
  overflow: 'auto',
  background: 'rgba(255, 255, 255, 0.8)',
}));

function Profile() {
  const navigate = useNavigate();
  const [user, setUser] = useState(null);
  const [bankData, setBankData] = useState(null);
  const [error, setError] = useState('');

  useEffect(() => {
    const token = localStorage.getItem('token');
    const cachedUser = localStorage.getItem('user');

    if (!token) {
      navigate('/login');
      return;
    }

    if (cachedUser) {
      try {
        setUser(JSON.parse(cachedUser));
      } catch (err) {
        console.error('Error parsing cached user:', err);
        localStorage.removeItem('user');
      }
    }

    // Fetch user profile and bank data
    Promise.all([
      fetch('http://localhost:8000/profile', {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      }),
      fetch('http://localhost:8000/bank/data', {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      })
    ])
      .then(async ([profileRes, bankRes]) => {
        if (!profileRes.ok || !bankRes.ok) {
          if (profileRes.status === 401 || bankRes.status === 401) {
            localStorage.removeItem('token');
            localStorage.removeItem('user');
            navigate('/login');
          }
          throw new Error('Failed to fetch data');
        }
        const profileData = await profileRes.json();
        const bankData = await bankRes.json();
        setUser(profileData.user);
        setBankData(bankData);
        localStorage.setItem('user', JSON.stringify(profileData.user));
      })
      .catch(err => {
        console.error('Fetch error:', err);
        setError(err.message);
        if (!cachedUser) {
          navigate('/login');
        }
      });
  }, [navigate]);

  const handleLogout = () => {
    localStorage.removeItem('token');
    localStorage.removeItem('user');
    navigate('/login');
  };

  if (!user || !bankData) {
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
      <Container maxWidth="md">
        <StyledPaper elevation={3}>
          <Typography variant="h4" align="center" gutterBottom>
            Profile
          </Typography>
          {error && (
            <Typography color="error" align="center" gutterBottom>
              {error}
            </Typography>
          )}
          <Box sx={{ mt: 3 }}>
            <Typography variant="h6">Username: {user.username}</Typography>
            <Typography variant="h6">Email: {user.email}</Typography>
            <Typography variant="h6">Name: {user.first_name} {user.last_name}</Typography>
          </Box>

          {bankData.accounts && bankData.accounts.length > 0 && (
            <Box sx={{ mt: 4 }}>
              <Typography variant="h5" gutterBottom>
                Bank Account
              </Typography>
              <Paper sx={{ p: 2, mb: 3 }}>
                <Typography variant="h6">{bankData.accounts[0].name}</Typography>
                <Typography>Account Number: ••••{bankData.accounts[0].mask}</Typography>
                <Typography>Available Balance: ${bankData.accounts[0].balances.available.toFixed(2)}</Typography>
                <Typography>Current Balance: ${bankData.accounts[0].balances.current.toFixed(2)}</Typography>
              </Paper>

              <Typography variant="h5" gutterBottom>
                Recent Transactions
              </Typography>
              <TransactionPaper>
                <TableContainer>
                  <Table>
                    <TableHead>
                      <TableRow>
                        <TableCell>Date</TableCell>
                        <TableCell>Description</TableCell>
                        <TableCell>Category</TableCell>
                        <TableCell align="right">Amount</TableCell>
                      </TableRow>
                    </TableHead>
                    <TableBody>
                      {bankData.transactions.map((transaction) => (
                        <TableRow key={transaction.transaction_id}>
                          <TableCell>{new Date(transaction.date).toLocaleDateString()}</TableCell>
                          <TableCell>{transaction.name}</TableCell>
                          <TableCell>
                            <Chip 
                              label={transaction.category}
                              size="small"
                              sx={{ 
                                backgroundColor: getCategoryColor(transaction.category),
                                color: 'white'
                              }}
                            />
                          </TableCell>
                          <TableCell 
                            align="right"
                            sx={{ 
                              color: transaction.amount >= 0 ? 'green' : 'red',
                              fontWeight: 'bold'
                            }}
                          >
                            ${Math.abs(transaction.amount).toFixed(2)}
                          </TableCell>
                        </TableRow>
                      ))}
                    </TableBody>
                  </Table>
                </TableContainer>
              </TransactionPaper>
            </Box>
          )}

          <Box sx={{ mt: 3, display: 'flex', justifyContent: 'center', gap: 2 }}>
            <Button
              variant="contained"
              onClick={() => navigate('/onboarding')}
              sx={{
                background: 'linear-gradient(45deg, #4CAF50 30%, #81C784 90%)',
                borderRadius: '25px',
                padding: '10px 30px',
                '&:hover': {
                  background: 'linear-gradient(45deg, #388E3C 30%, #66BB6A 90%)',
                }
              }}
            >
              Start Onboarding
            </Button>
            <Button
              variant="contained"
              onClick={() => navigate('/chat')}
              sx={{
                background: 'linear-gradient(45deg, #2196F3 30%, #21CBF3 90%)',
                borderRadius: '25px',
                padding: '10px 30px',
                '&:hover': {
                  background: 'linear-gradient(45deg, #1976D2 30%, #1E88E5 90%)',
                }
              }}
            >
              Chat with AI
            </Button>
            <Button
              variant="contained"
              onClick={handleLogout}
              sx={{
                background: 'linear-gradient(45deg, #f44336 30%, #e57373 90%)',
                borderRadius: '25px',
                padding: '10px 30px',
                '&:hover': {
                  background: 'linear-gradient(45deg, #d32f2f 30%, #ef5350 90%)',
                }
              }}
            >
              Logout
            </Button>
          </Box>
        </StyledPaper>
      </Container>
    </Box>
  );
}

function getCategoryColor(category) {
  const colors = {
    'Food': '#FF6B6B',
    'Transportation': '#4ECDC4',
    'Travel': '#45B7D1',
    'Shopping': '#96CEB4',
    'Rent': '#FFEEAD',
    'Other': '#D4A5A5'
  };
  return colors[category] || '#666666';
}

export default Profile; 