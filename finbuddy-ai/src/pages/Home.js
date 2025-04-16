import React, { useState, useEffect } from 'react';
import { 
  Box, 
  Typography, 
  Paper, 
  Button,
  Grid,
  LinearProgress,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  Divider,
  Container,
  IconButton
} from '@mui/material';
import { styled } from '@mui/material/styles';
import { useNavigate } from 'react-router-dom';
import AddCircleOutlineIcon from '@mui/icons-material/AddCircleOutline';
import ChatIcon from '@mui/icons-material/Chat';
import FastfoodIcon from '@mui/icons-material/Fastfood';
import ShoppingBagIcon from '@mui/icons-material/ShoppingBag';
import AccountBalanceIcon from '@mui/icons-material/AccountBalance';
import TrendingUpIcon from '@mui/icons-material/TrendingUp';
import SavingsIcon from '@mui/icons-material/Savings';
import TimelineIcon from '@mui/icons-material/Timeline';
import AttachMoneyIcon from '@mui/icons-material/AttachMoney';
import ReceiptIcon from '@mui/icons-material/Receipt';
import AccountBalanceWalletIcon from '@mui/icons-material/AccountBalanceWallet';

const StyledPaper = styled(Paper)(({ theme }) => ({
  background: 'white',
  borderRadius: '16px',
  padding: theme.spacing(2),
  boxShadow: '0 4px 20px rgba(0, 0, 0, 0.1)',
  transition: 'transform 0.2s ease-in-out, box-shadow 0.2s ease-in-out',
  height: '100%',
  minHeight: '120px',
  display: 'flex',
  flexDirection: 'column',
  '&:hover': {
    transform: 'translateY(-5px)',
    boxShadow: '0 8px 30px rgba(0, 0, 0, 0.15)',
  },
}));

const WelcomeBox = styled(Paper)(({ theme }) => ({
  background: 'linear-gradient(135deg, #2C3E50 0%, #3498db 100%)',
  borderRadius: '16px',
  padding: theme.spacing(2),
  color: 'white',
  marginBottom: theme.spacing(3),
  minHeight: '60px',
  display: 'flex',
  alignItems: 'center'
}));

function Home() {
  const navigate = useNavigate();
  const [userData, setUserData] = useState(null);
  const [transactions, setTransactions] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const token = localStorage.getItem('token');
        if (!token) {
          navigate('/login');
          return;
        }

        const response = await fetch('http://localhost:8000/bank/data', {
          headers: {
            'Authorization': `Bearer ${token}`
          }
        });

        if (!response.ok) {
          throw new Error('Failed to fetch data');
        }

        const data = await response.json();
        setUserData(data);
        setTransactions(data.transactions.slice(0, 5));
      } catch (error) {
        console.error('Error fetching data:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, [navigate]);

  if (loading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', minHeight: '100vh' }}>
        <Typography>Loading...</Typography>
      </Box>
    );
  }

  const currentBalance = userData?.accounts[0]?.balances?.current || 0;
  const monthlySpending = transactions.reduce((sum, t) => sum + Math.abs(t.amount), 0);
  const foodSpending = transactions
    .filter(t => t.category.toLowerCase() === 'food')
    .reduce((sum, t) => sum + Math.abs(t.amount), 0);
  const otherSpending = monthlySpending - foodSpending;

  const userName = userData?.user?.first_name || 'User';

  return (
    <Box sx={{ 
      minHeight: '100vh',
      background: 'linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%)',
      display: 'flex',
      flexDirection: 'column',
      p: 2
    }}>
      <Container maxWidth="lg">
        {/* Welcome Box */}
        <WelcomeBox>
          <Grid container alignItems="center" spacing={2}>
            <Grid item xs={12} md={6}>
              <Typography variant="h5" gutterBottom>
                Welcome, {userName}!
              </Typography>
              <Typography variant="body1">
                Your finances are looking good today! Keep up the good work!
              </Typography>
            </Grid>
            <Grid item xs={12} md={6} sx={{ display: 'flex', justifyContent: 'flex-end', gap: 1 }}>
              <Button
                variant="contained"
                startIcon={<AddCircleOutlineIcon />}
                size="small"
                sx={{ 
                  background: 'white',
                  color: '#2C3E50',
                  '&:hover': {
                    background: 'rgba(255, 255, 255, 0.9)'
                  }
                }}
              >
                Add Goal
              </Button>
              <Button
                variant="contained"
                startIcon={<ChatIcon />}
                size="small"
                sx={{ 
                  background: 'white',
                  color: '#2C3E50',
                  '&:hover': {
                    background: 'rgba(255, 255, 255, 0.9)'
                  }
                }}
                onClick={() => navigate('/chat')}
              >
                Chat with AI
              </Button>
            </Grid>
          </Grid>
        </WelcomeBox>

        {/* Three Cards Row */}
        <Grid container spacing={2} sx={{ mb: 4 }}>
          {/* Current Balance */}
          <Grid item xs={12} md={4}>
            <StyledPaper>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 1 }}>
                <Typography variant="subtitle1" color="text.secondary">
                  Current Balance
                </Typography>
                <IconButton size="small" sx={{ color: '#2C3E50' }}>
                  <AccountBalanceWalletIcon />
                </IconButton>
              </Box>
              <Typography variant="h5" sx={{ color: '#2C3E50', fontWeight: 'bold' }}>
                ${currentBalance.toFixed(2)}
              </Typography>
            </StyledPaper>
          </Grid>

          {/* Monthly Spending */}
          <Grid item xs={12} md={4}>
            <StyledPaper>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 1 }}>
                <Typography variant="subtitle1" color="text.secondary">
                  Monthly Spending
                </Typography>
                <IconButton size="small" sx={{ color: '#2C3E50' }}>
                  <AttachMoneyIcon />
                </IconButton>
              </Box>
              <Box sx={{ mb: 1 }}>
                <Box sx={{ display: 'flex', alignItems: 'center', mb: 0.5 }}>
                  <FastfoodIcon sx={{ mr: 1, color: '#e74c3c', fontSize: '1.2rem' }} />
                  <Typography variant="body2" sx={{ flexGrow: 1 }}>Food</Typography>
                  <Typography variant="body2">${foodSpending.toFixed(2)}</Typography>
                </Box>
                <LinearProgress 
                  variant="determinate" 
                  value={(foodSpending / monthlySpending) * 100} 
                  sx={{ 
                    height: 6, 
                    borderRadius: 3,
                    backgroundColor: 'rgba(231, 76, 60, 0.2)',
                    '& .MuiLinearProgress-bar': {
                      backgroundColor: '#e74c3c'
                    }
                  }}
                />
              </Box>
              <Box>
                <Box sx={{ display: 'flex', alignItems: 'center', mb: 0.5 }}>
                  <ShoppingBagIcon sx={{ mr: 1, color: '#3498db', fontSize: '1.2rem' }} />
                  <Typography variant="body2" sx={{ flexGrow: 1 }}>Other</Typography>
                  <Typography variant="body2">${otherSpending.toFixed(2)}</Typography>
                </Box>
                <LinearProgress 
                  variant="determinate" 
                  value={(otherSpending / monthlySpending) * 100} 
                  sx={{ 
                    height: 6, 
                    borderRadius: 3,
                    backgroundColor: 'rgba(52, 152, 219, 0.2)',
                    '& .MuiLinearProgress-bar': {
                      backgroundColor: '#3498db'
                    }
                  }}
                />
              </Box>
            </StyledPaper>
          </Grid>

          {/* Saving Progress */}
          <Grid item xs={12} md={4}>
            <StyledPaper>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 1 }}>
                <Typography variant="subtitle1" color="text.secondary">
                  Saving Progress
                </Typography>
                <IconButton size="small" sx={{ color: '#2C3E50' }}>
                  <TrendingUpIcon />
                </IconButton>
              </Box>
              <Typography variant="body2" color="text.secondary">
                No active goals yet
              </Typography>
            </StyledPaper>
          </Grid>
        </Grid>

        {/* Two Cards Row */}
        <Grid container spacing={2} mt={4}>
          {/* Active Goals */}
          <Grid item xs={12} md={6}>
            <StyledPaper>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 1 }}>
                <Typography variant="subtitle1" color="text.secondary">
                  Active Goals
                </Typography>
                <IconButton size="small" sx={{ color: '#2C3E50' }}>
                  <TimelineIcon />
                </IconButton>
              </Box>
              <Typography variant="body2" color="text.secondary">
                No active goals yet
              </Typography>
            </StyledPaper>
          </Grid>

          {/* Recent Activity */}
          <Grid item xs={12} md={6}>
            <StyledPaper>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 1 }}>
                <Typography variant="subtitle1" color="text.secondary">
                  Recent Activity
                </Typography>
                <IconButton size="small" sx={{ color: '#2C3E50' }}>
                  <ReceiptIcon />
                </IconButton>
              </Box>
              <List dense sx={{ maxHeight: '200px', overflow: 'auto' }}>
                {transactions.map((transaction, index) => (
                  <React.Fragment key={transaction.transaction_id}>
                    <ListItem>
                      <ListItemIcon sx={{ minWidth: '36px' }}>
                        {transaction.category.toLowerCase() === 'food' ? 
                          <FastfoodIcon sx={{ color: '#e74c3c', fontSize: '1.2rem' }} /> : 
                          <ShoppingBagIcon sx={{ color: '#3498db', fontSize: '1.2rem' }} />
                        }
                      </ListItemIcon>
                      <ListItemText
                        primary={transaction.name}
                        secondary={new Date(transaction.date).toLocaleDateString()}
                        primaryTypographyProps={{ variant: 'body2' }}
                        secondaryTypographyProps={{ variant: 'caption' }}
                      />
                      <Typography 
                        variant="body2" 
                        sx={{ 
                          color: transaction.amount >= 0 ? '#2ecc71' : '#e74c3c',
                          fontWeight: 'bold'
                        }}
                      >
                        ${Math.abs(transaction.amount).toFixed(2)}
                      </Typography>
                    </ListItem>
                    {index < transactions.length - 1 && <Divider />}
                  </React.Fragment>
                ))}
              </List>
            </StyledPaper>
          </Grid>
        </Grid>
      </Container>
    </Box>
  );
}

export default Home; 