import React, { useState, useEffect } from 'react';
import { 
  Box, 
  Typography, 
  Paper, 
  Button,
  Grid,
  LinearProgress,
  Container
} from '@mui/material';
import { styled } from '@mui/material/styles';
import { useNavigate } from 'react-router-dom';
import AddCircleOutlineIcon from '@mui/icons-material/AddCircleOutline';
import ChatIcon from '@mui/icons-material/Chat';
import TimelineIcon from '@mui/icons-material/Timeline';
import CheckCircleIcon from '@mui/icons-material/CheckCircle';
import AttachMoneyIcon from '@mui/icons-material/AttachMoney';

const StyledPaper = styled(Paper)(({ theme }) => ({
  background: 'white',
  borderRadius: '16px',
  padding: theme.spacing(2),
  boxShadow: '0 4px 20px rgba(0, 0, 0, 0.1)',
  transition: 'transform 0.2s ease-in-out, box-shadow 0.2s ease-in-out',
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

const StatBox = styled(Paper)(({ theme }) => ({
  background: 'white',
  borderRadius: '12px',
  padding: theme.spacing(2),
  textAlign: 'center',
  height: '100%',
  display: 'flex',
  flexDirection: 'column',
  justifyContent: 'center',
  alignItems: 'center',
  gap: theme.spacing(1)
}));

function Goals() {
  const navigate = useNavigate();
  const [savingGoals, setSavingGoals] = useState([]);
  const [spendingGoals, setSpendingGoals] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchGoals = async () => {
      try {
        const token = localStorage.getItem('token');
        if (!token) {
          navigate('/login');
          return;
        }

        // Fetch saving goals
        const savingResponse = await fetch('http://localhost:8000/goals/saving', {
          headers: {
            'Authorization': `Bearer ${token}`
          }
        });

        if (savingResponse.ok) {
          const savingData = await savingResponse.json();
          setSavingGoals(savingData.saving_goals);
        }

        // Fetch spending goals
        const spendingResponse = await fetch('http://localhost:8000/goals/spending', {
          headers: {
            'Authorization': `Bearer ${token}`
          }
        });

        if (spendingResponse.ok) {
          const spendingData = await spendingResponse.json();
          setSpendingGoals(spendingData.spending_goals);
        }
      } catch (error) {
        console.error('Error fetching goals:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchGoals();
  }, [navigate]);

  if (loading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', minHeight: '100vh' }}>
        <Typography>Loading...</Typography>
      </Box>
    );
  }

  const totalSaved = savingGoals.reduce((sum, goal) => sum + goal.current_amount, 0);
  const activeGoalsCount = savingGoals.length + spendingGoals.length;
  const completedGoalsCount = savingGoals.filter(goal => goal.current_amount >= goal.target_amount).length;

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
                Your Financial Goals
              </Typography>
              <Typography variant="caption" sx={{ fontSize: '0.9rem' }}>
                Track, manage, and achieve your financial dreams step-by-step.
              </Typography>
            </Grid>
            <Grid item xs={12} md={6} sx={{ display: 'flex', justifyContent: 'flex-end', gap: 1 }}>
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
                Add Goals
              </Button>
            </Grid>
          </Grid>
        </WelcomeBox>

        {/* Main Content Row */}
        <Grid container spacing={2}>
          {/* Left Box - Goal Progress Overview */}
          <Grid item xs={12} md={8}>
            <StyledPaper sx={{ height: 'fit-content' }}>
              <Typography variant="h6" gutterBottom>
                Goal Progress Overview
              </Typography>
              <Box sx={{ display: 'flex', flexDirection: 'column', gap: 4 }}>
                <Grid container spacing={2}>
                  <Grid item xs={4}>
                    <StatBox>
                      <AttachMoneyIcon sx={{ color: '#2ecc71', fontSize: '2rem' }} />
                      <Typography variant="h6">${totalSaved.toFixed(2)}</Typography>
                      <Typography variant="body2" color="text.secondary">Total Saved</Typography>
                    </StatBox>
                  </Grid>
                  <Grid item xs={4}>
                    <StatBox>
                      <TimelineIcon sx={{ color: '#3498db', fontSize: '2rem' }} />
                      <Typography variant="h6">{activeGoalsCount}</Typography>
                      <Typography variant="body2" color="text.secondary">Active Goals</Typography>
                    </StatBox>
                  </Grid>
                  <Grid item xs={4}>
                    <StatBox>
                      <CheckCircleIcon sx={{ color: '#2ecc71', fontSize: '2rem' }} />
                      <Typography variant="h6">{completedGoalsCount}</Typography>
                      <Typography variant="body2" color="text.secondary">Completed</Typography>
                    </StatBox>
                  </Grid>
                </Grid>

                <Box sx={{ mt: 1 }}>
                  <Typography variant="h6" gutterBottom>
                    Saving Goals
                  </Typography>
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
              </Box>
            </StyledPaper>
          </Grid>

          {/* Right Box - Goals Ideal for You */}
          <Grid item xs={12} md={4}>
            <StyledPaper sx={{ height: 'fit-content' }}>
              <Typography variant="h6" gutterBottom>
                Goals Ideal for You
              </Typography>
              <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
                <Paper sx={{ p: 2, background: '#f8f9fa' }}>
                  <Typography variant="subtitle1">New Car</Typography>
                  <Typography variant="body2" color="text.secondary">
                    Save for your dream car with a personalized plan
                  </Typography>
                </Paper>
                <Paper sx={{ p: 2, background: '#f8f9fa' }}>
                  <Typography variant="subtitle1">Vacation</Typography>
                  <Typography variant="body2" color="text.secondary">
                    Plan your perfect getaway with a dedicated savings goal
                  </Typography>
                </Paper>
              </Box>
            </StyledPaper>
          </Grid>
        </Grid>

        {/* Active Goals Section */}
        <Box sx={{ mt: 2 }}>
          <StyledPaper>
            <Typography variant="h6" gutterBottom>
              Active Goals
            </Typography>
            <Grid container spacing={2}>
              {spendingGoals.map((goal) => (
                <Grid item xs={12} sm={6} key={goal.id}>
                  <Paper sx={{ p: 1, height: '100%' }}>
                    <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 1 }}>
                      <Typography variant="subtitle1" sx={{ textTransform: 'capitalize' }}>
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
                  </Paper>
                </Grid>
              ))}
            </Grid>
          </StyledPaper>
        </Box>
      </Container>
    </Box>
  );
}

export default Goals; 