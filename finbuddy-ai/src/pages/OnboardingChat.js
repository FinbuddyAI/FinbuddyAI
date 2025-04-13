import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { 
  Container, 
  Box, 
  Typography, 
  Paper,
  Button,
  TextField,
  Stack
} from '@mui/material';
import { styled } from '@mui/material/styles';

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
  marginBottom: theme.spacing(2),
  borderRadius: '15px',
  maxWidth: '80%',
  alignSelf: isUser ? 'flex-end' : 'flex-start',
  backgroundColor: isUser ? '#2196F3' : '#E3F2FD',
  color: isUser ? 'white' : 'black',
}));

const questions = [
  "Question 1: What are your main financial goals for the next year?",
  "Question 2: How do you currently manage your monthly expenses?",
  "Question 3: What financial challenges are you facing right now?"
];

function OnboardingChat() {
  const navigate = useNavigate();
  const [currentQuestion, setCurrentQuestion] = useState(0);
  const [messages, setMessages] = useState([]);
  const [inputValue, setInputValue] = useState('');
  const [error, setError] = useState('');

  useEffect(() => {
    const token = localStorage.getItem('token');
    if (!token) {
      navigate('/login');
      return;
    }

    // Add initial bot message
    if (messages.length === 0 && currentQuestion < questions.length) {
      setMessages([{ text: questions[currentQuestion], isUser: false }]);
    }
  }, [navigate, currentQuestion, messages.length]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!inputValue.trim()) return;

    try {
      // Add user message
      setMessages(prev => [...prev, { text: inputValue, isUser: true }]);
      setInputValue('');

      // Move to next question
      if (currentQuestion < questions.length - 1) {
        setCurrentQuestion(prev => prev + 1);
        setMessages(prev => [...prev, { text: questions[currentQuestion + 1], isUser: false }]);
      }
    } catch (err) {
      setError('Failed to send message. Please try again.');
    }
  };

  const handleSkip = () => {
    if (currentQuestion < questions.length - 1) {
      setCurrentQuestion(prev => prev + 1);
      setMessages(prev => [...prev, { text: questions[currentQuestion + 1], isUser: false }]);
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
          <Typography variant="h4" align="center" gutterBottom>
            Financial Onboarding
          </Typography>
          {error && (
            <Typography color="error" align="center" gutterBottom>
              {error}
            </Typography>
          )}
          
          <Box sx={{ 
            height: '400px', 
            overflowY: 'auto', 
            mb: 3,
            display: 'flex',
            flexDirection: 'column',
            gap: 2
          }}>
            {messages.map((message, index) => (
              <ChatMessage key={index} isUser={message.isUser}>
                <Typography>{message.text}</Typography>
              </ChatMessage>
            ))}
          </Box>

          {currentQuestion < questions.length ? (
            <form onSubmit={handleSubmit}>
              <Stack spacing={2}>
                <TextField
                  fullWidth
                  variant="outlined"
                  value={inputValue}
                  onChange={(e) => setInputValue(e.target.value)}
                  placeholder="Type your response..."
                  multiline
                  rows={2}
                />
                <Box sx={{ display: 'flex', gap: 2 }}>
                  <Button
                    type="submit"
                    variant="contained"
                    fullWidth
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
                  <Button
                    variant="contained"
                    onClick={handleSkip}
                    fullWidth
                    sx={{
                      background: 'linear-gradient(45deg, #FF9800 30%, #FFB74D 90%)',
                      borderRadius: '25px',
                      padding: '10px 30px',
                      '&:hover': {
                        background: 'linear-gradient(45deg, #F57C00 30%, #FFA726 90%)',
                      }
                    }}
                  >
                    Skip
                  </Button>
                </Box>
              </Stack>
            </form>
          ) : (
            <Box sx={{ textAlign: 'center' }}>
              <Typography variant="h6" gutterBottom>
                Thank you for your responses!
              </Typography>
              <Button
                variant="contained"
                onClick={() => navigate('/profile')}
                sx={{
                  background: 'linear-gradient(45deg, #2196F3 30%, #21CBF3 90%)',
                  borderRadius: '25px',
                  padding: '10px 30px',
                  '&:hover': {
                    background: 'linear-gradient(45deg, #1976D2 30%, #1E88E5 90%)',
                  }
                }}
              >
                Back to Profile
              </Button>
            </Box>
          )}
        </StyledPaper>
      </Container>
    </Box>
  );
}

export default OnboardingChat; 