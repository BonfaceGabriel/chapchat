import React from 'react';
import ReactDOM from 'react-dom/client';
import App from './App.jsx';
import './index.css';
import { BrowserRouter } from 'react-router-dom'; // Import BrowserRouter
import { ThemeProvider, createTheme } from '@mui/material/styles';
import CssBaseline from '@mui/material/CssBaseline';

// Create a basic theme
const theme = createTheme({
    palette: {
        mode: 'light', // We can change this to 'dark' later
        primary: {
            main: '#5A67D8', // A nice indigo
        },
        secondary: {
            main: '#38B2AC', // Teal
        },
        background: {
            default: '#f4f7fe',
            paper: '#ffffff',
        }
    },
    typography: {
        fontFamily: '"Inter", "Roboto", "Helvetica", "Arial", sans-serif',
    },
    components: {
        MuiButton: {
            styleOverrides: {
                root: {
                    borderRadius: 8,
                    textTransform: 'none',
                }
            }
        }
    }
});


ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <ThemeProvider theme={theme}>
      <CssBaseline /> {/* A CSS reset for consistent styling */}
    <BrowserRouter> {/* Wrap App with the Router */}
      <App />
    </BrowserRouter>
    </ThemeProvider>
  </React.StrictMode>,
);
