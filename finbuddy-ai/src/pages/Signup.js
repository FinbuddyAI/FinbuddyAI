import { useState } from 'react';
import { 
  Container, 
  Box, 
  Typography, 
  Paper, 
  TextField, 
  Button, 
  Link,
  Stack
} from '@mui/material';
import { Link as RouterLink, useNavigate } from 'react-router-dom';
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

const StyledText = styled(Typography)(({ theme }) => ({
  color: '#2C3E50',
  fontWeight: 'bold',
  textShadow: '0 0 20px rgba(44, 62, 80, 0.2)',
}));

function Signup() {
  const navigate = useNavigate();
  const [formData, setFormData] = useState({
    email: '',
    password: '',
    username: '',
    first_name: '',
    last_name: '',
    phone_number: ''
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
        throw new Error('Signup failed');
      }

      const data = await response.json();
      localStorage.setItem('token', data.access_token);
      navigate('/bank-linking');
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
            Create Account
          </StyledText>
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
              required
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
              label="Username"
              name="username"
              value={formData.username}
              onChange={handleChange}
              margin="normal"
              required
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
              label="First Name"
              name="first_name"
              value={formData.first_name}
              onChange={handleChange}
              margin="normal"
              required
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
              label="Last Name"
              name="last_name"
              value={formData.last_name}
              onChange={handleChange}
              margin="normal"
              required
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
              label="Phone Number"
              name="phone_number"
              value={formData.phone_number}
              onChange={handleChange}
              margin="normal"
              required
              sx={{
                '& .MuiOutlinedInput-root': {
                  '&:hover fieldset': {
                    borderColor: '#2C3E50',
                  },
                },
              }}
            />
            <Stack spacing={2} sx={{ mt: 3 }}>
              <Button
                type="submit"
                fullWidth
                variant="contained"
                sx={{
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
                Sign Up
              </Button>
              <Button
                fullWidth
                variant="outlined"
                onClick={() => navigate('/')}
                sx={{ 
                  color: '#2C3E50',
                  borderColor: '#2C3E50',
                  borderRadius: '25px',
                  padding: '10px 30px',
                  '&:hover': {
                    borderColor: '#1a252f',
                    backgroundColor: 'rgba(44, 62, 80, 0.1)'
                  }
                }}
              >
                Back to Home
              </Button>
            </Stack>
            <Typography align="center" sx={{ mt: 2, color: '#34495E' }}>
              Already have an account?{' '}
              <Link component={RouterLink} to="/login" sx={{ color: '#2C3E50' }}>
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