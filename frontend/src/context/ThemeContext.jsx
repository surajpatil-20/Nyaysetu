import { createContext, useContext, useState, useEffect } from 'react';

const ThemeContext = createContext();

export const FONT_SIZES = {
  normal: {
    id: 'normal',
    label: 'Standard',
    sizePx: '16px',
    scale: '100%',
    badge: '16px',
    desc: 'Default interface typography optimized for standard displays.'
  },
  medium: {
    id: 'medium',
    label: 'Medium',
    sizePx: '18px',
    scale: '112%',
    badge: '18px',
    desc: 'Enhanced readability for case analysis, statutes, and legal citations.'
  },
  large: {
    id: 'large',
    label: 'Large',
    sizePx: '20px',
    scale: '125%',
    badge: '20px',
    desc: 'Maximum legibility for in-depth judicial dossiers and orders.'
  }
};

export function ThemeProvider({ children }) {
  // Theme state: 'light' or 'dark'
  const [theme, setThemeState] = useState(() => {
    try {
      const savedTheme = localStorage.getItem('nyaysetu_theme');
      if (savedTheme === 'light' || savedTheme === 'dark') {
        return savedTheme;
      }
      return 'light';
    } catch {
      return 'light';
    }
  });

  // Font size state: 'normal', 'medium', or 'large'
  const [fontSize, setFontSizeState] = useState(() => {
    try {
      const savedSize = localStorage.getItem('nyaysetu_font_size');
      if (FONT_SIZES[savedSize]) {
        return savedSize;
      }
      return 'normal';
    } catch {
      return 'normal';
    }
  });

  // Apply theme to document root
  useEffect(() => {
    try {
      localStorage.setItem('nyaysetu_theme', theme);
    } catch (e) {
      console.warn('Unable to persist theme to localStorage', e);
    }

    const root = document.documentElement;
    root.setAttribute('data-theme', theme);
    if (theme === 'dark') {
      root.classList.add('dark');
      root.classList.remove('light');
    } else {
      root.classList.add('light');
      root.classList.remove('dark');
    }
  }, [theme]);

  // Apply font size to document root
  useEffect(() => {
    try {
      localStorage.setItem('nyaysetu_font_size', fontSize);
    } catch (e) {
      console.warn('Unable to persist font size to localStorage', e);
    }

    const root = document.documentElement;
    root.setAttribute('data-font-size', fontSize);
    const sizeConfig = FONT_SIZES[fontSize] || FONT_SIZES.normal;
    root.style.fontSize = sizeConfig.sizePx;
  }, [fontSize]);

  const toggleTheme = () => {
    setThemeState((prev) => (prev === 'dark' ? 'light' : 'dark'));
  };

  const setTheme = (newTheme) => {
    if (newTheme === 'dark' || newTheme === 'light') {
      setThemeState(newTheme);
    }
  };

  const setFontSize = (newSize) => {
    if (FONT_SIZES[newSize]) {
      setFontSizeState(newSize);
    }
  };

  const resetPreferences = () => {
    setThemeState('light');
    setFontSizeState('normal');
  };

  return (
    <ThemeContext.Provider
      value={{
        theme,
        toggleTheme,
        setTheme,
        isDark: theme === 'dark',
        fontSize,
        setFontSize,
        fontSizeConfig: FONT_SIZES[fontSize] || FONT_SIZES.normal,
        fontSizes: FONT_SIZES,
        resetPreferences,
      }}
    >
      {children}
    </ThemeContext.Provider>
  );
}

export function useTheme() {
  const context = useContext(ThemeContext);
  if (!context) {
    throw new Error('useTheme must be used within a ThemeProvider');
  }
  return context;
}
