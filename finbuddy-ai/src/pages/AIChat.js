import React, { useState, useRef, useEffect } from 'react';
import { Box, Container, TextField, Button, Paper, Typography, Avatar } from '@mui/material';
import { styled } from '@mui/material/styles';
import SendIcon from '@mui/icons-material/Send';
import SmartToyIcon from '@mui/icons-material/SmartToy';
import PersonIcon from '@mui/icons-material/Person';

const StyledPaper = styled(Paper)(({ theme }) => ({
  padding: theme.spacing(3),
  marginTop: theme.spacing(3),
  borderRadius: '12px',
  backgroundColor: '#ffffff',
  height: 'calc(100vh - 100px)',
  display: 'flex',
  flexDirection: 'column',
}));

const MessageContainer = styled(Box)(({ theme }) => ({
  display: 'flex',
  marginBottom: theme.spacing(2),
  alignItems: 'flex-start',
}));

const MessageBubble = styled(Box)(({ theme, isUser }) => ({
  backgroundColor: isUser ? theme.palette.primary.main : '#f5f5f5',
  color: isUser ? '#fff' : '#000',
  padding: theme.spacing(1.5),
  borderRadius: '12px',
  maxWidth: '70%',
  wordWrap: 'break-word',
  marginLeft: isUser ? 'auto' : theme.spacing(1),
  marginRight: isUser ? theme.spacing(1) : 'auto',
}));

const ChatContainer = styled(Box)({
  flexGrow: 1,
  overflowY: 'auto',
  marginBottom: '20px',
  padding: '10px',
});

const InputContainer = styled(Box)(({ theme }) => ({
  display: 'flex',
  gap: theme.spacing(1),
  padding: theme.spacing(2),
  borderTop: '1px solid #e0e0e0',
}));

function AIChat() {
  const [messages, setMessages] = useState([
    { text: "Hi! I'm your personal financial assistant. How can I help you today?", isUser: false }
  ]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const chatContainerRef = useRef(null);

  useEffect(() => {
    if (chatContainerRef.current) {
      chatContainerRef.current.scrollTop = chatContainerRef.current.scrollHeight;
    }
  }, [messages]);

  const handleSend = async () => {
    if (!input.trim()) return;

    const userMessage = { text: input, isUser: true };
    setMessages(prev => [...prev, userMessage]);
    setInput('');
    setIsLoading(true);

    try {
      const response = await fetch('http://localhost:8000/chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        },
        body: JSON.stringify({ message: input })
      });

      if (!response.ok) {
        throw new Error('Failed to get response');
      }

      const data = await response.json();
      setMessages(prev => [...prev, { text: data.response, isUser: false }]);
    } catch (error) {
      console.error('Error:', error);
      setMessages(prev => [...prev, { 
        text: "I'm sorry, I'm having trouble connecting right now. Please try again later.", 
        isUser: false 
      }]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  return (
    <Container maxWidth="md">
      <StyledPaper elevation={3}>
        <Typography variant="h5" gutterBottom sx={{ textAlign: 'center', color: '#1976d2' }}>
          Chat with Your Financial Assistant
        </Typography>
        
        <ChatContainer ref={chatContainerRef}>
          {messages.map((message, index) => (
            <MessageContainer key={index}>
              <Avatar sx={{ 
                bgcolor: message.isUser ? 'primary.main' : 'secondary.main',
                marginRight: message.isUser ? 'auto' : '0',
                marginLeft: message.isUser ? '8px' : '0',
                order: message.isUser ? 2 : 0
              }}>
                {message.isUser ? <PersonIcon /> : <SmartToyIcon />}
              </Avatar>
              <MessageBubble isUser={message.isUser}>
                <Typography>{message.text}</Typography>
              </MessageBubble>
            </MessageContainer>
          ))}
          {isLoading && (
            <MessageContainer>
              <Avatar sx={{ bgcolor: 'secondary.main' }}>
                <SmartToyIcon />
              </Avatar>
              <MessageBubble isUser={false}>
                <Typography>Thinking...</Typography>
              </MessageBubble>
            </MessageContainer>
          )}
        </ChatContainer>

        <InputContainer>
          <TextField
            fullWidth
            multiline
            maxRows={4}
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder="Type your message here..."
            variant="outlined"
            disabled={isLoading}
          />
          <Button
            variant="contained"
            color="primary"
            endIcon={<SendIcon />}
            onClick={handleSend}
            disabled={isLoading || !input.trim()}
          >
            Send
          </Button>
        </InputContainer>
      </StyledPaper>
    </Container>
  );
}

export default AIChat; 