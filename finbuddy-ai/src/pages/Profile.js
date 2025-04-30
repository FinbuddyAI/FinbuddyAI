import { useState, useEffect } from 'react';
import { 
  Container, 
  Box, 
  Typography, 
  Paper, 
  Button, 
  Avatar,
  TextField,
  FormControlLabel,
  Checkbox,
  RadioGroup,
  Radio,
  FormControl,
  FormLabel,
  Divider
} from '@mui/material';
import { useNavigate } from 'react-router-dom';
import { styled } from '@mui/material/styles';
import PersonIcon from '@mui/icons-material/Person';
import AccountBalanceIcon from '@mui/icons-material/AccountBalance';
import AddIcon from '@mui/icons-material/Add';
import SmartToyIcon from '@mui/icons-material/SmartToy';
import LogoutIcon from '@mui/icons-material/Logout';

const StyledPaper = styled(Paper)(({ theme }) => ({
  background: 'white',
  borderRadius: '12px',
  padding: theme.spacing(2),
  boxShadow: '0 4px 20px rgba(0, 0, 0, 0.1)',
  transition: 'transform 0.2s ease-in-out, box-shadow 0.2s ease-in-out',
  '&:hover': {
    transform: 'translateY(-5px)',
    boxShadow: '0 8px 30px rgba(0, 0, 0, 0.15)',
  },
}));

const TitleBox = styled(Paper)(({ theme }) => ({
  background: 'linear-gradient(135deg, #2C3E50 0%, #3498db 100%)',
  borderRadius: '12px',
  padding: theme.spacing(2),
  color: 'white',
  marginBottom: theme.spacing(2),
  position: 'relative',
}));

function Profile() {
  const navigate = useNavigate();
  const [user, setUser] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const [editMode, setEditMode] = useState(false);
  const [formData, setFormData] = useState({
    firstName: '',
    lastName: '',
    email: '',
    phone: '',
    suggestionPreference: '1 week',
    contactMethods: {
      email: true,
      phone: false
    }
  });

  useEffect(() => {
    const token = localStorage.getItem('token');
    const cachedUser = localStorage.getItem('user');

    if (!token) {
      navigate('/login');
      return;
    }

    if (cachedUser) {
      try {
        const parsedUser = JSON.parse(cachedUser);
        setUser(parsedUser);
        setFormData({
          firstName: parsedUser.first_name || '',
          lastName: parsedUser.last_name || '',
          email: parsedUser.email || '',
          phone: parsedUser.phone || '',
          suggestionPreference: parsedUser.suggestion_preference || '1 week',
          contactMethods: {
            email: parsedUser.email_contact || true,
            phone: parsedUser.phone_contact || false
          }
        });
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
            return;
          }
          throw new Error('Failed to fetch data');
        }
        const profileData = await profileRes.json();
        setUser(profileData.user);
        localStorage.setItem('user', JSON.stringify(profileData.user));
        
        // Update form data with new user data
        setFormData({
          firstName: profileData.user.first_name || '',
          lastName: profileData.user.last_name || '',
          email: profileData.user.email || '',
          phone: profileData.user.phone || '',
          suggestionPreference: profileData.user.suggestion_preference || '1 week',
          contactMethods: {
            email: profileData.user.email_contact || true,
            phone: profileData.user.phone_contact || false
          }
        });
      })
      .catch(err => {
        console.error('Fetch error:', err);
        if (!cachedUser) {
          navigate('/login');
        }
      })
      .finally(() => {
        setIsLoading(false);
      });
  }, [navigate]);

  const handleContactMethodChange = (method) => (event) => {
    setFormData({
      ...formData,
      contactMethods: {
        ...formData.contactMethods,
        [method]: event.target.checked
      }
    });
  };

  const handleInputChange = (field) => (event) => {
    setFormData({
      ...formData,
      [field]: event.target.value
    });
  };

  const handleSaveProfile = () => {
    // Here you would typically make an API call to update the user's profile
    setEditMode(false);
  };

  const handleLogout = () => {
    localStorage.removeItem('token');
    localStorage.removeItem('user');
    navigate('/login');
  };

  if (isLoading) {
    return (
      <Box sx={{ 
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        height: '100vh'
      }}>
        <Typography>Loading...</Typography>
      </Box>
    );
  }

  if (!user) {
    return (
      <Box sx={{ 
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        height: '100vh'
      }}>
        <Typography>Error loading profile. Please try again.</Typography>
      </Box>
    );
  }

  return (
    <Box sx={{ 
      minHeight: '100vh',
      background: 'linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%)',
      display: 'flex',
      flexDirection: 'column',
      p: 2
    }}>
      <Container maxWidth="lg">
        <TitleBox>
          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <Box>
              <Typography variant="h5" sx={{ color: 'white', fontWeight: 'bold' }}>
                Profile & Settings
              </Typography>
              <Typography variant="body2" sx={{ color: 'rgba(255, 255, 255, 0.8)' }}>
                Manage your account preferences and security settings
              </Typography>
            </Box>
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
          </Box>
          <Button
            variant="contained"
            startIcon={<SmartToyIcon />}
            size="small"
            sx={{ 
              mt: 2,
              background: 'white',
              color: '#2C3E50',
              '&:hover': {
                background: 'rgba(255, 255, 255, 0.9)'
              }
            }}
            onClick={() => navigate('/onboarding')}
          >
            Start Onboarding Chat
          </Button>
        </TitleBox>

        <Box sx={{ display: 'flex', gap: 2 }}>
          {/* Left Column - Profile Overview */}
          <Box sx={{ flex: 2 }}>
            <StyledPaper>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
                <Typography variant="subtitle1" color="text.secondary">
                  Profile Overview
                </Typography>
                {editMode ? (
                  <Button 
                    size="small" 
                    variant="contained" 
                    onClick={handleSaveProfile}
                  >
                    Save Changes
                  </Button>
                ) : (
                  <Button 
                    size="small" 
                    variant="outlined" 
                    onClick={() => setEditMode(true)}
                  >
                    Edit Profile
                  </Button>
                )}
              </Box>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                <Avatar sx={{ width: 60, height: 60, mr: 2 }}>
                  <PersonIcon sx={{ fontSize: 30 }} />
                </Avatar>
                <Box>
                  <Typography variant="body2" color="text.secondary">
                    Current Plan
                  </Typography>
                  <Typography variant="subtitle1">
                    Free Plan
                  </Typography>
                </Box>
              </Box>
              <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1.5 }}>
                <Box sx={{ display: 'flex', alignItems: 'center' }}>
                  <Typography variant="body2" sx={{ width: '80px', color: 'text.secondary' }}>Name:</Typography>
                  {editMode ? (
                    <Box sx={{ display: 'flex', gap: 1, flex: 1 }}>
                      <TextField
                        size="small"
                        value={formData.firstName}
                        onChange={handleInputChange('firstName')}
                        placeholder="First Name"
                        sx={{ flex: 1 }}
                      />
                      <TextField
                        size="small"
                        value={formData.lastName}
                        onChange={handleInputChange('lastName')}
                        placeholder="Last Name"
                        sx={{ flex: 1 }}
                      />
                    </Box>
                  ) : (
                    <Typography variant="body2">{user.first_name} {user.last_name}</Typography>
                  )}
                </Box>
                <Box sx={{ display: 'flex', alignItems: 'center' }}>
                  <Typography variant="body2" sx={{ width: '80px', color: 'text.secondary' }}>Email:</Typography>
                  {editMode ? (
                    <TextField
                      size="small"
                      value={formData.email}
                      onChange={handleInputChange('email')}
                      fullWidth
                    />
                  ) : (
                    <Typography variant="body2">{user.email}</Typography>
                  )}
                </Box>
                <Box sx={{ display: 'flex', alignItems: 'center' }}>
                  <Typography variant="body2" sx={{ width: '80px', color: 'text.secondary' }}>Phone:</Typography>
                  {editMode ? (
                    <TextField
                      size="small"
                      value={formData.phone}
                      onChange={handleInputChange('phone')}
                      fullWidth
                    />
                  ) : (
                    <Typography variant="body2">{user.phone || 'Not set'}</Typography>
                  )}
                </Box>
              </Box>
            </StyledPaper>

            {/* Security Settings */}
            <StyledPaper sx={{ mt: 2 }}>
              <Typography variant="subtitle1" color="text.secondary" gutterBottom>
                Security Settings
              </Typography>
              <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1.5 }}>
                <TextField
                  size="small"
                  label="Current Password"
                  type="password"
                  fullWidth
                />
                <TextField
                  size="small"
                  label="New Password"
                  type="password"
                  fullWidth
                />
                <TextField
                  size="small"
                  label="Confirm New Password"
                  type="password"
                  fullWidth
                />
                <Button 
                  variant="contained" 
                  size="small"
                  sx={{ alignSelf: 'flex-start' }}
                >
                  Update Password
                </Button>
              </Box>
            </StyledPaper>
        </Box>

          {/* Right Column - Preferences */}
          <Box sx={{ flex: 1 }}>
            <StyledPaper>
              <Typography variant="subtitle1" color="text.secondary" gutterBottom>
                Preferences
            </Typography>
              <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
                <FormControl component="fieldset" size="small">
                  <FormLabel component="legend">Suggestion Preference</FormLabel>
                  <RadioGroup
                    value={formData.suggestionPreference}
                    onChange={(e) => setFormData({ ...formData, suggestionPreference: e.target.value })}
                  >
                    <FormControlLabel value="1 day" control={<Radio size="small" />} label="1 day" />
                    <FormControlLabel value="1 week" control={<Radio size="small" />} label="1 week" />
                    <FormControlLabel value="1 month" control={<Radio size="small" />} label="1 month" />
                  </RadioGroup>
                </FormControl>

                <FormControl component="fieldset" size="small">
                  <FormLabel component="legend">Contact Method</FormLabel>
                  <FormControlLabel
                    control={
                      <Checkbox
                        size="small"
                        checked={formData.contactMethods.email}
                        onChange={handleContactMethodChange('email')}
                      />
                    }
                    label="Email"
                  />
                  <FormControlLabel
                    control={
                      <Checkbox
                        size="small"
                        checked={formData.contactMethods.phone}
                        onChange={handleContactMethodChange('phone')}
                      />
                    }
                    label="Phone"
                  />
                </FormControl>
              </Box>
            </StyledPaper>

            {/* Connected Accounts */}
            <StyledPaper sx={{ mt: 2 }}>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 1 }}>
                <Typography variant="subtitle1" color="text.secondary">
                  Connected Accounts
            </Typography>
                <Button 
                            size="small"
                  variant="outlined" 
                  startIcon={<AddIcon />}
                            sx={{ 
                    color: '#3498db',
                    borderColor: '#3498db',
                    '&:hover': {
                      borderColor: '#2980b9',
                      backgroundColor: 'rgba(52, 152, 219, 0.1)'
                    }
                  }}
                >
                  Add Account
                </Button>
              </Box>
              <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1.5 }}>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1.5 }}>
                  <AccountBalanceIcon sx={{ color: '#2C3E50', fontSize: '1.2rem' }} />
                  <Box>
                    <Typography variant="body2">Chase Bank</Typography>
                    <Typography variant="caption" color="text.secondary">••••1234</Typography>
                  </Box>
                </Box>
                <Divider />
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1.5 }}>
                  <AccountBalanceIcon sx={{ color: '#2C3E50', fontSize: '1.2rem' }} />
                  <Box>
                    <Typography variant="body2">Bank of America</Typography>
                    <Typography variant="caption" color="text.secondary">••••5678</Typography>
                  </Box>
                </Box>
              </Box>
            </StyledPaper>
          </Box>
        </Box>
      </Container>
    </Box>
  );
}

export default Profile; 