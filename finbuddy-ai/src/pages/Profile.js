import { useState, useEffect } from 'react';
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

const StyledPaper = styled(Paper)(({ theme }) => ({
  background: 'rgba(255, 255, 255, 0.9)',
  backdropFilter: 'blur(10px)',
  borderRadius: '20px',
  padding: theme.spacing(4),
  boxShadow: '0 8px 32px 0 rgba(31, 38, 135, 0.37)',
  maxWidth: '600px',
  margin: '0 auto',
}));

function Profile() {
  const navigate = useNavigate();
  const [user, setUser] = useState(null);
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

    // Always verify with server
    fetch('http://localhost:8000/profile', {
      headers: {
        'Authorization': `Bearer ${token}`
      }
    })
      .then(response => {
        if (!response.ok) {
          if (response.status === 401) {
            localStorage.removeItem('token');
            localStorage.removeItem('user');
            navigate('/login');
          }
          throw new Error('Failed to fetch profile');
        }
        return response.json();
      })
      .then(data => {
        setUser(data);
        localStorage.setItem('user', JSON.stringify(data));
      })
      .catch(err => {
        console.error('Profile fetch error:', err);
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

  if (!user) {
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
          <Stack spacing={2} sx={{ mt: 3 }}>
            <Button
              fullWidth
              variant="contained"
              onClick={handleLogout}
              sx={{
                background: 'linear-gradient(45deg, #2196F3 30%, #21CBF3 90%)',
                borderRadius: '25px',
                padding: '10px 30px',
                '&:hover': {
                  background: 'linear-gradient(45deg, #1976D2 30%, #1E88E5 90%)',
                }
              }}
            >
              Logout
            </Button>
            <Button
              fullWidth
              variant="contained"
              onClick={() => navigate('/')}
              sx={{
                background: 'linear-gradient(45deg, #2196F3 30%, #21CBF3 90%)',
                borderRadius: '25px',
                padding: '10px 30px',
                '&:hover': {
                  background: 'linear-gradient(45deg, #1976D2 30%, #1E88E5 90%)',
                }
              }}
            >
              Back to Home
            </Button>
          </Stack>
        </StyledPaper>
      </Container>
    </Box>
  );
}

export default Profile; 