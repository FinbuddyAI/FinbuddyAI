import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { ThemeProvider, createTheme } from '@mui/material';
import CssBaseline from '@mui/material/CssBaseline';
import Login from './pages/Login';
import Signup from './pages/Signup';
import Profile from './pages/Profile';
import OnboardingChat from './pages/OnboardingChat';
import AIChat from './pages/AIChat';
import Home from './components/Home';

const theme = createTheme({
  palette: {
    primary: {
      main: '#2196F3',
    },
    secondary: {
      main: '#dc004e',
    },
    background: {
      default: '#1a1a1a',
    },
  },
});

function App() {
  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <Router>
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/login" element={<Login />} />
          <Route path="/signup" element={<Signup />} />
          <Route path="/profile" element={<Profile />} />
          <Route path="/onboarding" element={<OnboardingChat />} />
          <Route path="/chat" element={<AIChat />} />
        </Routes>
      </Router>
    </ThemeProvider>
  );
}

export default App;