const colors = require('tailwindcss/colors');

/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './src/templates/**/*.html',
    './src/static/**/*.js',
    './src/**/templates/**/*.html',
  ],
  theme: {
    extend: {
      colors: {
        // Import standard Tailwind colors
        emerald: colors.emerald,
        amber: colors.amber,
        slate: colors.slate,
        teal: colors.teal,
        // OBCMS Ocean Blue - Primary brand color
        ocean: {
          50: '#e0f2fe',
          100: '#bae6fd',
          200: '#7dd3fc',
          300: '#38bdf8',
          400: '#0ea5e9',
          500: '#0284c7',
          600: '#0369a1',  // WCAG AA compliant on white (4.5:1)
          700: '#075985',  // WCAG AA compliant (7.0:1)
          800: '#0c4a6e',  // Safe for body text (10.7:1)
          900: '#082f49',  // Safe for headers (14.3:1)
        },

        // OBCMS Gold - Warnings, highlights & prosperity (alias for amber)
        gold: colors.amber,
      },

      backgroundImage: {
        // Primary brand gradient (Ocean → Teal → Emerald)
        'gradient-primary': 'linear-gradient(135deg, #0369a1 0%, #0d9488 50%, #059669 100%)',

        // Ocean gradients
        'gradient-ocean': 'radial-gradient(circle at top left, #0ea5e9 0%, #0284c7 100%)',
        'gradient-ocean-linear': 'linear-gradient(135deg, #0284c7 0%, #0369a1 100%)',

        // Emerald gradients
        'gradient-emerald': 'radial-gradient(circle at bottom right, #10b981 0%, #059669 100%)',
        'gradient-emerald-linear': 'linear-gradient(135deg, #10b981 0%, #059669 100%)',

        // Teal gradients
        'gradient-teal-flow': 'linear-gradient(135deg, #14b8a6 0%, #0d9488 50%, #0f766e 100%)',
        'gradient-teal': 'linear-gradient(135deg, #14b8a6 0%, #0d9488 100%)',

        // Gold gradients
        'gradient-gold': 'linear-gradient(135deg, #fbbf24 0%, #f59e0b 50%, #d97706 100%)',
        'gradient-gold-shine': 'linear-gradient(135deg, #fef3c7 0%, #fbbf24 50%, #f59e0b 100%)',

        // Special gradients
        'gradient-sunrise': 'linear-gradient(135deg, #0ea5e9 0%, #14b8a6 33%, #fbbf24 66%, #f59e0b 100%)',
        'gradient-hero': 'linear-gradient(135deg, #0c4a6e 0%, #075985 50%, #0369a1 100%)',

        // Subtle background gradients
        'gradient-bg-ocean': 'linear-gradient(180deg, rgba(14, 165, 233, 0.05) 0%, rgba(20, 184, 166, 0.03) 50%, transparent 100%)',
        'gradient-bg-emerald': 'linear-gradient(180deg, rgba(16, 185, 129, 0.08) 0%, rgba(5, 150, 105, 0.04) 50%, transparent 100%)',
        'gradient-bg-gold': 'linear-gradient(180deg, rgba(251, 191, 36, 0.08) 0%, rgba(245, 158, 11, 0.04) 50%, transparent 100%)',
      },

      boxShadow: {
        'ocean': '0 4px 14px -2px rgba(3, 105, 161, 0.15)',
        'ocean-lg': '0 10px 30px -5px rgba(3, 105, 161, 0.20)',
        'emerald': '0 4px 14px -2px rgba(5, 150, 105, 0.15)',
        'emerald-lg': '0 10px 30px -5px rgba(5, 150, 105, 0.20)',
        'teal': '0 4px 14px -2px rgba(13, 148, 136, 0.15)',
        'teal-lg': '0 10px 30px -5px rgba(13, 148, 136, 0.20)',
        'gold': '0 4px 14px -2px rgba(217, 119, 6, 0.15)',
        'gold-lg': '0 10px 30px -5px rgba(217, 119, 6, 0.20)',
      },

      ringColor: {
        'ocean': 'rgba(3, 105, 161, 0.20)',
        'emerald': 'rgba(5, 150, 105, 0.20)',
        'teal': 'rgba(13, 148, 136, 0.20)',
        'gold': 'rgba(217, 119, 6, 0.20)',
      },

      borderRadius: {
        'xl': '1rem',
        '2xl': '1.5rem',
        '3xl': '1.75rem',
      },

      fontFamily: {
        sans: ['Inter', 'system-ui', '-apple-system', 'BlinkMacSystemFont', 'Segoe UI', 'sans-serif'],
      },

      fontSize: {
        'xxs': '0.65rem',
      },

      spacing: {
        '128': '32rem',
        '144': '36rem',
      },

      animation: {
        'fade-in': 'fadeIn 0.3s ease-in-out',
        'slide-up': 'slideUp 0.3s ease-out',
        'slide-down': 'slideDown 0.3s ease-out',
        'scale-in': 'scaleIn 0.2s ease-out',
      },

      keyframes: {
        fadeIn: {
          '0%': { opacity: '0' },
          '100%': { opacity: '1' },
        },
        slideUp: {
          '0%': { transform: 'translateY(10px)', opacity: '0' },
          '100%': { transform: 'translateY(0)', opacity: '1' },
        },
        slideDown: {
          '0%': { transform: 'translateY(-10px)', opacity: '0' },
          '100%': { transform: 'translateY(0)', opacity: '1' },
        },
        scaleIn: {
          '0%': { transform: 'scale(0.95)', opacity: '0' },
          '100%': { transform: 'scale(1)', opacity: '1' },
        },
      },
    },
  },
  plugins: [
    // Add custom utilities
    function({ addUtilities }) {
      const newUtilities = {
        '.text-gradient-ocean': {
          'background': 'linear-gradient(135deg, #0369a1 0%, #0d9488 100%)',
          '-webkit-background-clip': 'text',
          '-webkit-text-fill-color': 'transparent',
          'background-clip': 'text',
        },
        '.text-gradient-emerald': {
          'background': 'linear-gradient(135deg, #059669 0%, #10b981 100%)',
          '-webkit-background-clip': 'text',
          '-webkit-text-fill-color': 'transparent',
          'background-clip': 'text',
        },
        '.text-gradient-gold': {
          'background': 'linear-gradient(135deg, #d97706 0%, #fbbf24 100%)',
          '-webkit-background-clip': 'text',
          '-webkit-text-fill-color': 'transparent',
          'background-clip': 'text',
        },
      };

      addUtilities(newUtilities, ['responsive', 'hover']);
    },
  ],

  // Safelist commonly used dynamic classes
  safelist: [
    // Ocean colors
    'text-ocean-600',
    'text-ocean-700',
    'bg-ocean-50',
    'bg-ocean-100',
    'bg-ocean-600',
    'border-ocean-600',
    'hover:bg-ocean-700',
    'focus:ring-ocean-500',

    // Emerald colors
    'text-emerald-600',
    'text-emerald-700',
    'bg-emerald-50',
    'bg-emerald-100',
    'bg-emerald-600',
    'border-emerald-600',
    'hover:bg-emerald-700',
    'focus:ring-emerald-500',

    // Teal colors
    'text-teal-600',
    'text-teal-700',
    'bg-teal-50',
    'bg-teal-100',
    'bg-teal-600',
    'border-teal-600',
    'hover:bg-teal-700',

    // Gold colors
    'text-gold-600',
    'text-gold-700',
    'bg-gold-50',
    'bg-gold-100',
    'bg-gold-600',
    'border-gold-600',
    'hover:bg-gold-700',
  ],
};
