import React from 'react';
import { createRoot } from 'react-dom/client';
import { BrowserRouter } from 'react-router-dom';
import App from './App';
import ErrorBoundary from './shared/components/ErrorBoundary';
import { ThemeProvider } from './shared/theme/ThemeProvider';
import { SiteProvider } from './shared/site/SiteProvider';
import './shared/theme/theme.css';

createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <ErrorBoundary>
      <BrowserRouter>
        <ThemeProvider>
          <SiteProvider>
            <App />
          </SiteProvider>
        </ThemeProvider>
      </BrowserRouter>
    </ErrorBoundary>
  </React.StrictMode>
);
