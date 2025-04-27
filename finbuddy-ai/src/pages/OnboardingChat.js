import React, { useState, useEffect, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import { 
  Container, 
  Box, 
  Typography, 
  Paper,
  Button,
  TextField,
  Stack,
  CircularProgress,
  Alert
} from '@mui/material';
import { styled } from '@mui/material/styles';
import ReactMarkdown from 'react-markdown';

const StyledPaper = styled(Paper)(({ theme }) => ({
  background: 'rgba(255, 255, 255, 0.9)',
  backdropFilter: 'blur(10px)',
  borderRadius: '20px',
  padding: theme.spacing(4),
  boxShadow: '0 8px 32px 0 rgba(31, 38, 135, 0.37)',
  maxWidth: '800px',
  margin: '0 auto',
}));

const ChatMessage = styled(Box)(({ theme, isUser }) => ({
  padding: theme.spacing(2),
  marginBottom: theme.spacing(1),
  borderRadius: '15px',
  maxWidth: '80%',
  alignSelf: isUser ? 'flex-end' : 'flex-start',
  backgroundColor: isUser ? '#2196F3' : '#E3F2FD',
  color: isUser ? 'white' : 'black',
  whiteSpace: 'pre-line',
  '& p': {
    margin: '0.1em 0',
    lineHeight: '1.2',
  },
  '& ul, & ol': {
    margin: '0.1em 0',
    paddingLeft: '1em',
  },
  '& li': {
    margin: '0',
    padding: '0',
    lineHeight: '1.2',
  }
}));

function OnboardingChat() {
  const navigate = useNavigate();
  const [messages, setMessages] = useState([]);
  const [inputValue, setInputValue] = useState('');
  const [error, setError] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [isOnboardingComplete, setIsOnboardingComplete] = useState(false);
  const [userProfile, setUserProfile] = useState(null);
  const chatContainerRef = useRef(null);

  useEffect(() => {
    const token = localStorage.getItem('token');
    if (!token) {
      navigate('/login');
      return;
    }

    // Start the onboarding process
    startOnboarding();
  }, [navigate]);

  // Add auto-scroll effect
  useEffect(() => {
    if (chatContainerRef.current) {
      chatContainerRef.current.scrollTop = chatContainerRef.current.scrollHeight;
    }
  }, [messages, isLoading]); // Scroll when messages change or loading state changes

  const startOnboarding = async () => {
    try {
      setIsLoading(true);
      const response = await fetch('http://localhost:8000/onboarding/start', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
      });

      if (!response.ok) {
        throw new Error('Failed to start onboarding');
      }

      const data = await response.json();
      setMessages([{ text: data.message, isUser: false }]);
    } catch (err) {
      setError('Failed to start onboarding. Please try again.');
      console.error('Error:', err);
    } finally {
      setIsLoading(false);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!inputValue.trim() || isLoading) return;

    try {
      setIsLoading(true);
      const userMessage = inputValue.trim();
      setInputValue('');
      
      // Add user message
      setMessages(prev => [...prev, { text: userMessage, isUser: true }]);

      // Make API call to send message
      const response = await fetch('http://localhost:8000/onboarding/send-message', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        },
        body: JSON.stringify({ content: userMessage })
      });

      if (!response.ok) {
        throw new Error('Failed to get response');
      }

      const data = await response.json();
      
      // Add advisor's response
      setMessages(prev => [...prev, { text: data.message, isUser: false }]);

      // Check if onboarding is complete
      if (data.is_complete) {
        setIsOnboardingComplete(true);
        setUserProfile(data.profile);
        // You can handle the completed profile here (e.g., save to backend, navigate to dashboard)
        console.log('Onboarding complete! Profile:', data.profile);
      }
    } catch (err) {
      setError('Failed to send message. Please try again.');
      console.error('Error:', err);
    } finally {
      setIsLoading(false);
    }
  };

  const formatMessage = (text) => {
    // If the message contains financial summary, format it properly
    if (text.includes('Current Financial Summary:')) {
      return text.split('\n').map((line, index) => {
        if (line.startsWith('- ')) {
          return `• ${line.substring(2)}`;  // Convert - to bullet points
        }
        return line;
      }).join('\n');
    }
    return text;
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
      <Container maxWidth="md">
        <StyledPaper elevation={3}>
          <Typography variant="h4" align="center" gutterBottom>
            Financial Onboarding
          </Typography>
          {error && (
            <Alert severity="error" sx={{ mb: 2 }}>
              {error}
            </Alert>
          )}
          {isOnboardingComplete && (
            <Alert severity="success" sx={{ mb: 2 }}>
              Onboarding complete! Your profile has been created.
            </Alert>
          )}
          
          <Box 
            ref={chatContainerRef}
            sx={{ 
              height: '400px', 
              overflowY: 'auto', 
              mb: 3,
              display: 'flex',
              flexDirection: 'column',
              gap: 1,
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
                '&:hover': {
                  background: '#555',
                },
              },
            }}
          >
            {messages.map((message, index) => (
              <ChatMessage key={index} isUser={message.isUser}>
                <ReactMarkdown
                  components={{
                    p: ({node, ...props}) => <Typography component="p" sx={{ mb: 0.2 }} {...props} />,
                    li: ({node, ...props}) => <Typography component="li" sx={{ mb: 0, py: 0 }} {...props} />,
                    ul: ({node, ...props}) => <Typography component="ul" sx={{ mb: 0.2, mt: 0.2 }} {...props} />,
                    br: () => <br style={{ margin: '0.1em 0' }} />,
                  }}
                >
                  {formatMessage(message.text)}
                </ReactMarkdown>
              </ChatMessage>
            ))}
            {isLoading && (
              <ChatMessage isUser={false}>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                  <CircularProgress size={20} />
                  <Typography>Thinking...</Typography>
                </Box>
              </ChatMessage>
            )}
          </Box>

          {!isOnboardingComplete && (
            <form onSubmit={handleSubmit}>
              <Stack spacing={2}>
                <TextField
                  fullWidth
                  variant="outlined"
                  value={inputValue}
                  onChange={(e) => setInputValue(e.target.value)}
                  placeholder="Type your message..."
                  multiline
                  rows={2}
                  disabled={isLoading}
                />
                <Button
                  type="submit"
                  variant="contained"
                  fullWidth
                  disabled={isLoading || !inputValue.trim()}
                  sx={{
                    background: 'linear-gradient(45deg, #2196F3 30%, #21CBF3 90%)',
                    borderRadius: '25px',
                    padding: '10px 30px',
                    '&:hover': {
                      background: 'linear-gradient(45deg, #1976D2 30%, #1E88E5 90%)',
                    }
                  }}
                >
                  Send
                </Button>
              </Stack>
            </form>
          )}
        </StyledPaper>
      </Container>
    </Box>
  );
}

export default OnboardingChat; 