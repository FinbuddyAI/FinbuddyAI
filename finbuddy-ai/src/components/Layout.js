import { Box } from '@mui/material';
import Sidebar from './Sidebar';

const Layout = ({ children }) => {
  return (
    <Box sx={{ display: 'flex', minHeight: '100vh' }}>
      <Sidebar />
      <Box
        component="main"
        sx={{
          flexGrow: 1,
          p: 3,
          width: { md: `calc(100% - 240px)` },
          ml: { md: '240px' },
          background: 'linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%)',
        }}
      >
        {children}
      </Box>
    </Box>
  );
};

export default Layout; 