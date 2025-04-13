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
  IconButton,
  CircularProgress
} from '@mui/material';
import { styled } from '@mui/material/styles';
import SendIcon from '@mui/icons-material/Send';
import ArrowBackIcon from '@mui/icons-material/ArrowBack';

const StyledPaper = styled(Paper)(({ theme }) => ({
  background: 'rgba(255, 255, 255, 0.9)',
  backdropFilter: 'blur(10px)',
  borderRadius: '20px',
  padding: theme.spacing(4),
  boxShadow: '0 8px 32px 0 rgba(31, 38, 135, 0.37)',
  maxWidth: '800px',
  margin: '0 auto',
  height: '80vh',
  display: 'flex',
  flexDirection: 'column',
}));

const ChatMessage = styled(Box)(({ theme, isUser }) => ({
  padding: theme.spacing(2),
  marginBottom: theme.spacing(2),
  borderRadius: '15px',
  maxWidth: '80%',
  alignSelf: isUser ? 'flex-end' : 'flex-start',
  backgroundColor: isUser ? '#2196F3' : '#E3F2FD',
  color: isUser ? 'white' : 'black',
  whiteSpace: 'pre-wrap',
}));

function AIChat() {
  const navigate = useNavigate();
  const [messages, setMessages] = useState([
    { 
      text: "Hello! I'm your financial AI assistant. How can I help you today?", 
      isUser: false 
    }
  ]);
  const [inputValue, setInputValue] = useState('');
  const [error, setError] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  useEffect(() => {
    const token = localStorage.getItem('token');
    if (!token) {
      navigate('/login');
    }
  }, [navigate]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!inputValue.trim() || isLoading) return;

    try {
      setIsLoading(true);
      const userMessage = inputValue.trim();
      setInputValue('');
      
      // Add user message
      setMessages(prev => [...prev, { text: userMessage, isUser: true }]);

      // TODO: Replace with actual API call to your LLM
      // Simulating API call with a timeout
      setTimeout(() => {
        const response = `This is a simulated response to: "${userMessage}". We will connect to our AI LLM here`;
        setMessages(prev => [...prev, { text: response, isUser: false }]);
        setIsLoading(false);
      }, 1000);

    } catch (err) {
      setError('Failed to send message. Please try again.');
      setIsLoading(false);
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
      <Container maxWidth="md">
        <StyledPaper elevation={3}>
          <Box sx={{ 
            display: 'flex', 
            alignItems: 'center', 
            mb: 2,
            justifyContent: 'space-between'
          }}>
            <IconButton 
              onClick={() => navigate('/profile')}
              sx={{ color: '#2196F3' }}
            >
              <ArrowBackIcon />
            </IconButton>
            <Typography variant="h5" align="center">
              AI Financial Assistant
            </Typography>
            <Box sx={{ width: 40 }} /> {/* Spacer for alignment */}
          </Box>

          {error && (
            <Typography color="error" align="center" gutterBottom>
              {error}
            </Typography>
          )}
          
          <Box sx={{ 
            flex: 1,
            overflowY: 'auto', 
            mb: 3,
            display: 'flex',
            flexDirection: 'column',
            gap: 2,
            pr: 1
          }}>
            {messages.map((message, index) => (
              <ChatMessage key={index} isUser={message.isUser}>
                <Typography>{message.text}</Typography>
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
            <div ref={messagesEndRef} />
          </Box>

          <form onSubmit={handleSubmit}>
            <Stack direction="row" spacing={1}>
              <TextField
                fullWidth
                variant="outlined"
                value={inputValue}
                onChange={(e) => setInputValue(e.target.value)}
                placeholder="Type your message..."
                multiline
                maxRows={4}
                disabled={isLoading}
                sx={{
                  '& .MuiOutlinedInput-root': {
                    borderRadius: '25px',
                  }
                }}
              />
              <IconButton 
                type="submit" 
                disabled={isLoading || !inputValue.trim()}
                sx={{
                  backgroundColor: '#2196F3',
                  color: 'white',
                  '&:hover': {
                    backgroundColor: '#1976D2',
                  },
                  '&:disabled': {
                    backgroundColor: '#BDBDBD',
                  }
                }}
              >
                <SendIcon />
              </IconButton>
            </Stack>
          </form>
        </StyledPaper>
      </Container>
    </Box>
  );
}

export default AIChat; 