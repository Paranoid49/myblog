import { createContext, useContext, useEffect, useMemo, useState } from 'react';

const STORAGE_KEY = 'myblog_theme';

const THEME_REGISTRY = {
  light: { key: 'light' },
  dark: { key: 'dark' },
};

const ThemeContext = createContext({
  theme: 'light',
  setTheme: () => {},
  toggleTheme: () => {},
  themes: Object.keys(THEME_REGISTRY),
});

function readStoredTheme() {
  const value = window.localStorage.getItem(STORAGE_KEY);
  if (!value) return 'light';
  return THEME_REGISTRY[value] ? value : 'light';
}

export function ThemeProvider({ children }) {
  const [theme, setThemeState] = useState(readStoredTheme);

  useEffect(() => {
    setTheme(theme);
  }, []);

  function setTheme(nextTheme) {
    const resolved = THEME_REGISTRY[nextTheme] ? nextTheme : 'light';
    setThemeState(resolved);
    window.localStorage.setItem(STORAGE_KEY, resolved);
    document.documentElement.setAttribute('data-theme', resolved);
  }

  const value = useMemo(
    () => ({
      theme,
      themes: Object.keys(THEME_REGISTRY),
      setTheme,
      toggleTheme: () => setTheme(theme === 'light' ? 'dark' : 'light'),
    }),
    [theme]
  );

  return <ThemeContext.Provider value={value}>{children}</ThemeContext.Provider>;
}

export function useTheme() {
  return useContext(ThemeContext);
}

export function registerTheme(themeKey) {
  if (!themeKey) return;
  THEME_REGISTRY[themeKey] = { key: themeKey };
}
