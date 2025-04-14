import { useState } from 'react';
import { 
  Container, 
  Box, 
  Typography, 
  Paper, 
  TextField, 
  Button, 
  Link,
  Alert
} from '@mui/material';
import { styled } from '@mui/material/styles';
import { useNavigate } from 'react-router-dom';

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

const StyledText = styled(Typography)(({ theme }) => ({
  color: '#2C3E50',
  fontWeight: 'bold',
  textShadow: '0 0 20px rgba(44, 62, 80, 0.2)',
}));

function Login({ setIsAuthenticated }) {
  const navigate = useNavigate();
  const [formData, setFormData] = useState({
    email: '',
    password: '',
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
      const response = await fetch('http://localhost:8000/login', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(formData),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Login failed');
      }

      const data = await response.json();
      localStorage.setItem('token', data.access_token);
      setIsAuthenticated(true);
      navigate('/home');
    } catch (err) {
      setError(err.message);
    }
  };

  return (
    <Box sx={{ 
      minHeight: '100vh',
      background: 'linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%)',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      py: 4
    }}>
      <Container maxWidth="sm">
        <StyledPaper elevation={3}>
          <StyledText variant="h4" align="center" gutterBottom>
            Welcome to Finbuddy
          </StyledText>
          {error && (
            <Alert severity="error" sx={{ mb: 2 }}>
              {error}
            </Alert>
          )}
          <form onSubmit={handleSubmit}>
            <TextField
              fullWidth
              label="Email"
              name="email"
              value={formData.email}
              onChange={handleChange}
              margin="normal"
              sx={{
                '& .MuiOutlinedInput-root': {
                  '&:hover fieldset': {
                    borderColor: '#2C3E50',
                  },
                },
              }}
            />
            <TextField
              fullWidth
              label="Password"
              name="password"
              type="password"
              value={formData.password}
              onChange={handleChange}
              margin="normal"
              sx={{
                '& .MuiOutlinedInput-root': {
                  '&:hover fieldset': {
                    borderColor: '#2C3E50',
                  },
                },
              }}
            />
            <Button
              type="submit"
              fullWidth
              variant="contained"
              sx={{
                mt: 3,
                background: '#2C3E50',
                borderRadius: '25px',
                padding: '10px 30px',
                boxShadow: '0 4px 15px rgba(44, 62, 80, 0.3)',
                textShadow: '0 0 10px rgba(0, 0, 0, 0.1)',
                '&:hover': {
                  background: '#1a252f',
                  boxShadow: '0 6px 20px rgba(44, 62, 80, 0.4)',
                }
              }}
            >
              Sign In
            </Button>
          </form>
          <Box sx={{ mt: 2, textAlign: 'center' }}>
            <Link 
              href="/register" 
              variant="body2"
              sx={{ 
                color: '#2C3E50',
                textDecoration: 'none',
                '&:hover': {
                  textDecoration: 'underline',
                }
              }}
            >
              Don't have an account? Sign Up
            </Link>
          </Box>
        </StyledPaper>
      </Container>
    </Box>
  );
}

export default Login; 