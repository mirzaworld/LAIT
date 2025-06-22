import React from 'react';
import { useNavigate } from 'react-router-dom';
import toast from 'react-hot-toast';

interface SmartButtonProps {
  onClick?: () => void;
  href?: string;
  type?: 'button' | 'submit' | 'reset';
  className?: string;
  children: React.ReactNode;
  disabled?: boolean;
  loading?: boolean;
  variant?: 'primary' | 'secondary' | 'danger' | 'success';
  size?: 'sm' | 'md' | 'lg';
  external?: boolean;
}

/**
 * SmartButton component that prevents page refreshes and handles navigation properly
 */
const SmartButton: React.FC<SmartButtonProps> = ({
  onClick,
  href,
  type = 'button',
  className = '',
  children,
  disabled = false,
  loading = false,
  variant = 'primary',
  size = 'md',
  external = false
}) => {
  const navigate = useNavigate();

  const getVariantClasses = () => {
    switch (variant) {
      case 'primary':
        return 'bg-primary-600 text-white hover:bg-primary-700 focus:ring-primary-500';
      case 'secondary':
        return 'bg-gray-200 text-gray-900 hover:bg-gray-300 focus:ring-gray-500';
      case 'danger':
        return 'bg-red-600 text-white hover:bg-red-700 focus:ring-red-500';
      case 'success':
        return 'bg-green-600 text-white hover:bg-green-700 focus:ring-green-500';
      default:
        return 'bg-primary-600 text-white hover:bg-primary-700 focus:ring-primary-500';
    }
  };

  const getSizeClasses = () => {
    switch (size) {
      case 'sm':
        return 'px-3 py-1.5 text-sm';
      case 'md':
        return 'px-4 py-2 text-sm';
      case 'lg':
        return 'px-6 py-3 text-base';
      default:
        return 'px-4 py-2 text-sm';
    }
  };

  const baseClasses = `
    inline-flex items-center justify-center
    font-medium rounded-lg
    transition-colors duration-200
    focus:outline-none focus:ring-2 focus:ring-offset-2
    disabled:opacity-50 disabled:cursor-not-allowed
    ${getVariantClasses()}
    ${getSizeClasses()}
    ${className}
  `.trim().replace(/\s+/g, ' ');

  const handleClick = (e: React.MouseEvent<HTMLButtonElement>) => {
    e.preventDefault();
    e.stopPropagation();

    if (disabled || loading) {
      return;
    }

    try {
      // Handle navigation
      if (href) {
        if (external || href.startsWith('http')) {
          // External link - open in new tab
          window.open(href, '_blank', 'noopener,noreferrer');
        } else if (href.startsWith('#')) {
          // Anchor link - smooth scroll
          const element = document.querySelector(href);
          element?.scrollIntoView({ behavior: 'smooth' });
        } else if (href.startsWith('/')) {
          // Internal route - use React Router
          navigate(href);
        } else {
          // Relative path
          navigate(href);
        }
      }

      // Handle custom onClick
      if (onClick) {
        onClick();
      }
    } catch (error) {
      console.error('Button click error:', error);
      toast.error('An error occurred while processing your request');
    }
  };

  return (
    <button
      type={type}
      className={baseClasses}
      onClick={handleClick}
      disabled={disabled || loading}
    >
      {loading && (
        <svg
          className="animate-spin -ml-1 mr-2 h-4 w-4 text-current"
          xmlns="http://www.w3.org/2000/svg"
          fill="none"
          viewBox="0 0 24 24"
        >
          <circle
            className="opacity-25"
            cx="12"
            cy="12"
            r="10"
            stroke="currentColor"
            strokeWidth="4"
          />
          <path
            className="opacity-75"
            fill="currentColor"
            d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
          />
        </svg>
      )}
      {children}
    </button>
  );
};

export default SmartButton;
