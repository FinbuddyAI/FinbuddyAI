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
import TimelineIcon from '@mui/icons-material/Timeline';
import ReceiptIcon from '@mui/icons-material/Receipt';
import AccountBalanceWalletIcon from '@mui/icons-material/AccountBalanceWallet';
import LogoutIcon from '@mui/icons-material/Logout';

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
  const [savingGoals, setSavingGoals] = useState([]);
  const [spendingGoals, setSpendingGoals] = useState([]);

  const handleLogout = () => {
    localStorage.removeItem('token');
    localStorage.removeItem('user');
    navigate('/login');
  };

  useEffect(() => {
    const fetchData = async () => {
      try {
        const token = localStorage.getItem('token');
        if (!token) return;

        // Fetch bank data
        const bankResponse = await fetch('http://localhost:8000/bank/data', {
          headers: {
            'Authorization': `Bearer ${token}`
          }
        });

        if (!bankResponse.ok) {
          throw new Error('Failed to fetch bank data');
        }

        const bankData = await bankResponse.json();
        setUserData(bankData);
        setTransactions(bankData.transactions.slice(0, 5));

        // Fetch saving goals
        const savingGoalsResponse = await fetch('http://localhost:8000/goals/saving', {
          headers: {
            'Authorization': `Bearer ${token}`
          }
        });

        if (savingGoalsResponse.ok) {
          const savingData = await savingGoalsResponse.json();
          setSavingGoals(savingData.saving_goals);
        }

        // Fetch spending goals
        const spendingGoalsResponse = await fetch('http://localhost:8000/goals/spending', {
          headers: {
            'Authorization': `Bearer ${token}`
          }
        });

        if (spendingGoalsResponse.ok) {
          const spendingData = await spendingGoalsResponse.json();
          setSpendingGoals(spendingData.spending_goals);
        }
      } catch (error) {
        console.error('Error fetching data:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, []);

  if (loading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', minHeight: '100vh' }}>
        <Typography>Loading...</Typography>
      </Box>
    );
  }

  const currentBalance = userData?.accounts[0]?.balances?.current || 0;
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
        <WelcomeBox>
          <Grid container alignItems="center" spacing={2}>
            <Grid item xs={12} md={6}>
              <Typography variant="h5" gutterBottom>
                Welcome back, {userName}!
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
              <Button
                variant="contained"
                startIcon={<LogoutIcon />}
                size="small"
                sx={{ 
                  background: 'white',
                  color: '#2C3E50',
                  '&:hover': {
                    background: 'rgba(255, 255, 255, 0.9)'
                  }
                }}
                onClick={handleLogout}
              >
                Logout
              </Button>
            </Grid>
          </Grid>
        </WelcomeBox>

        {/* Main Content Grid */}
        <Grid container spacing={2}>
          {/* Left Side */}
          <Grid item xs={12} md={7.2} container spacing={2}>
            {/* Top Row - Current Balance and Saving Goals */}
            <Grid item xs={12}>
              <Grid container spacing={2}>
                {/* Current Balance */}
                <Grid item xs={12} md={5}>
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

                {/* Saving Goals */}
                <Grid item xs={12} md={7}>
                  <StyledPaper>
                    <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 1 }}>
                      <Typography variant="subtitle1" color="text.secondary">
                        Saving Goals
                      </Typography>
                    </Box>
                    {savingGoals.length > 0 ? (
                      <Box>
                        {savingGoals.map((goal) => (
                          <Box key={goal.id} sx={{ mb: 2 }}>
                            <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 0.5 }}>
                              <Typography variant="body2" sx={{ textTransform: 'capitalize' }}>
                                {goal.category.replace('_', ' ')}
                              </Typography>
                              <Typography variant="body2">
                                ${goal.current_amount.toFixed(2)} / ${goal.target_amount.toFixed(2)}
                              </Typography>
                            </Box>
                            <LinearProgress 
                              variant="determinate" 
                              value={(goal.current_amount / goal.target_amount) * 100} 
                              sx={{ 
                                height: 6, 
                                borderRadius: 3,
                                backgroundColor: 'rgba(46, 204, 113, 0.2)',
                                '& .MuiLinearProgress-bar': {
                                  backgroundColor: '#2ecc71'
                                }
                              }}
                            />
                          </Box>
                        ))}
                      </Box>
                    ) : (
                      <Typography variant="body2" color="text.secondary">
                        No saving goals yet
                      </Typography>
                    )}
                  </StyledPaper>
                </Grid>
              </Grid>
            </Grid>

            {/* Monthly Spending */}
            <Grid item xs={10}>
              <StyledPaper>
                <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 1 }}>
                  <Typography variant="subtitle1" color="text.secondary">
                    Monthly Spending
                  </Typography>
                  <IconButton size="small" sx={{ color: '#2C3E50' }}>
                    <TimelineIcon />
                  </IconButton>
                </Box>
                {spendingGoals.length > 0 ? (
                  <Box>
                    {spendingGoals.map((goal) => (
                      <Box key={goal.id} sx={{ mb: 2 }}>
                        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 0.5 }}>
                          <Typography variant="body2" sx={{ textTransform: 'capitalize' }}>
                            {goal.category}
                          </Typography>
                          <Typography variant="body2">
                            ${goal.current_amount.toFixed(2)} / ${goal.target_amount.toFixed(2)}
                          </Typography>
                        </Box>
                        <LinearProgress 
                          variant="determinate" 
                          value={(goal.current_amount / goal.target_amount) * 100} 
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
                    ))}
                  </Box>
                ) : (
                  <Typography variant="body2" color="text.secondary">
                    No spending goals yet
                  </Typography>
                )}
              </StyledPaper>
            </Grid>
          </Grid>

          {/* Right Side - Recent Transactions */}
          <Grid item xs={12} md={4.8}>
            <StyledPaper sx={{ height: '100%' }}>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 1 }}>
                <Typography variant="subtitle1" color="text.secondary">
                  Recent Transactions
                </Typography>
                <IconButton size="small" sx={{ color: '#2C3E50' }}>
                  <ReceiptIcon />
                </IconButton>
              </Box>
              <List dense sx={{ 
                height: 'calc(100% - 48px)', 
                overflow: 'auto',
                '&::-webkit-scrollbar': {
                  width: '8px',
                },
                '&::-webkit-scrollbar-track': {
                  background: '#f1f1f1',
                  borderRadius: '4px',
                },
                '&::-webkit-scrollbar-thumb': {
                  background: '#888',
                  borderRadius: '4px',
                },
                '&::-webkit-scrollbar-thumb:hover': {
                  background: '#555',
                },
              }}>
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