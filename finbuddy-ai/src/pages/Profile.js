import { useState, useEffect } from 'react';
import { 
  Container, 
  Box, 
  Typography, 
  Paper, 
  Button, 
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Chip,
  CircularProgress
} from '@mui/material';
import { useNavigate } from 'react-router-dom';
import { styled } from '@mui/material/styles';

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

const TransactionPaper = styled(Paper)(({ theme }) => ({
  marginTop: theme.spacing(3),
  maxHeight: '400px',
  overflow: 'auto',
  background: 'white',
  borderRadius: '15px',
  boxShadow: '0 2px 10px rgba(0, 0, 0, 0.05)',
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
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        height: '100%'
      }}>
        <CircularProgress sx={{ color: '#2C3E50' }} />
      </Box>
    );
  }

  return (
    <Box sx={{ p: 3 }}>
      <StyledPaper elevation={3}>
        <Typography variant="h4" align="center" gutterBottom sx={{ color: '#2C3E50', fontWeight: 'bold' }}>
          Profile
        </Typography>
        {error && (
          <Typography color="error" align="center" gutterBottom>
            {error}
          </Typography>
        )}
        <Box sx={{ mt: 3 }}>
          <Typography variant="h6" sx={{ color: '#2C3E50' }}>Username: {user.username}</Typography>
          <Typography variant="h6" sx={{ color: '#2C3E50' }}>Email: {user.email}</Typography>
          <Typography variant="h6" sx={{ color: '#2C3E50' }}>Name: {user.first_name} {user.last_name}</Typography>
        </Box>

        {bankData.accounts && bankData.accounts.length > 0 && (
          <Box sx={{ mt: 4 }}>
            <Typography variant="h5" gutterBottom sx={{ color: '#2C3E50', fontWeight: 'bold' }}>
              Bank Account
            </Typography>
            <Paper sx={{ p: 2, mb: 3, background: 'white', borderRadius: '15px', boxShadow: '0 2px 10px rgba(0, 0, 0, 0.05)' }}>
              <Typography variant="h6" sx={{ color: '#2C3E50' }}>{bankData.accounts[0].name}</Typography>
              <Typography sx={{ color: '#2C3E50' }}>Account Number: ••••{bankData.accounts[0].mask}</Typography>
              <Typography sx={{ color: '#2C3E50' }}>Available Balance: ${bankData.accounts[0].balances.available.toFixed(2)}</Typography>
              <Typography sx={{ color: '#2C3E50' }}>Current Balance: ${bankData.accounts[0].balances.current.toFixed(2)}</Typography>
            </Paper>

            <Typography variant="h5" gutterBottom sx={{ color: '#2C3E50', fontWeight: 'bold' }}>
              Recent Transactions
            </Typography>
            <TransactionPaper>
              <TableContainer>
                <Table>
                  <TableHead>
                    <TableRow>
                      <TableCell sx={{ color: '#2C3E50', fontWeight: 'bold' }}>Date</TableCell>
                      <TableCell sx={{ color: '#2C3E50', fontWeight: 'bold' }}>Description</TableCell>
                      <TableCell sx={{ color: '#2C3E50', fontWeight: 'bold' }}>Category</TableCell>
                      <TableCell align="right" sx={{ color: '#2C3E50', fontWeight: 'bold' }}>Amount</TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {bankData.transactions.map((transaction) => (
                      <TableRow key={transaction.transaction_id}>
                        <TableCell sx={{ color: '#2C3E50' }}>{new Date(transaction.date).toLocaleDateString()}</TableCell>
                        <TableCell sx={{ color: '#2C3E50' }}>{transaction.name}</TableCell>
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
                            color: transaction.amount >= 0 ? '#4CAF50' : '#f44336',
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
      </StyledPaper>
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