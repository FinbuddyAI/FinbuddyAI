import { useState } from 'react';
import { 
  Container, 
  Box, 
  TextField, 
  Button, 
  Typography, 
  Paper,
  Link,
  Stack
} from '@mui/material';
import { Link as RouterLink, useNavigate } from 'react-router-dom';
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

function Signup() {
  const navigate = useNavigate();
  const [formData, setFormData] = useState({
    email: '',
    password: '',
    username: '',
    first_name: '',
    last_name: ''
  });
  const [error, setError] = useState('');

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value,
    });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      const response = await fetch('http://localhost:8000/register', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(formData),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Signup failed');
      }

      const data = await response.json();
      if (data.access_token && data.user) {
        // Store token and user info
        localStorage.setItem('token', data.access_token);
        localStorage.setItem('user', JSON.stringify(data.user));
        navigate('/profile');
      } else {
        throw new Error('Invalid response from server');
      }
    } catch (err) {
      setError(err.message || 'Signup failed. Please try again.');
    }
  };

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
            Create Account
          </Typography>
          {error && (
            <Typography color="error" align="center" gutterBottom>
              {error}
            </Typography>
          )}
          <form onSubmit={handleSubmit}>
            <TextField
              fullWidth
              label="Email"
              name="email"
              value={formData.email}
              onChange={handleChange}
              margin="normal"
              required
            />
            <TextField
              fullWidth
              label="Password"
              name="password"
              type="password"
              value={formData.password}
              onChange={handleChange}
              margin="normal"
              required
            />
            <TextField
              fullWidth
              label="Username"
              name="username"
              value={formData.username}
              onChange={handleChange}
              margin="normal"
              required
            />
            <TextField
              fullWidth
              label="First Name"
              name="first_name"
              value={formData.first_name}
              onChange={handleChange}
              margin="normal"
              required
            />
            <TextField
              fullWidth
              label="Last Name"
              name="last_name"
              value={formData.last_name}
              onChange={handleChange}
              margin="normal"
              required
            />
            <Stack spacing={2} sx={{ mt: 3 }}>
              <Button
                type="submit"
                fullWidth
                variant="contained"
                sx={{
                  background: 'linear-gradient(45deg, #2196F3 30%, #21CBF3 90%)',
                  borderRadius: '25px',
                  padding: '10px 30px',
                  '&:hover': {
                    background: 'linear-gradient(45deg, #1976D2 30%, #1E88E5 90%)',
                  }
                }}
              >
                Sign Up
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
            <Typography align="center" sx={{ mt: 2 }}>
              Already have an account?{' '}
              <Link component={RouterLink} to="/login" color="primary">
                Sign in
              </Link>
            </Typography>
          </form>
        </StyledPaper>
      </Container>
    </Box>
  );
}

export default Signup; 