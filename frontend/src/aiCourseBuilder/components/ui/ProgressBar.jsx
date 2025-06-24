import { useContext } from 'react';
import { DirectionContext } from '../../../contexts/DirectionContext.jsx';

const ProgressBar = ({
  progress = 0,
  total = 100,
  showPercentage = true,
  showLabel = true,
  label = 'Progress',
  size = 'md',
  variant = 'primary',
  animated = false,
  striped = false,
  className = '',
}) => {
  const { direction } = useContext(DirectionContext) || { direction: 'ltr' };
  const isRtl = direction === 'rtl';
  const percentage = Math.min(Math.max((progress / total) * 100, 0), 100);

  const sizeClasses = {
    sm: 'h-1',
    md: 'h-2',
    lg: 'h-3',
    xl: 'h-4',
  };

  const variantClasses = {
    primary: 'bg-blue-600',
    success: 'bg-green-600',
    warning: 'bg-yellow-600',
    danger: 'bg-red-600',
    info: 'bg-cyan-600',
    purple: 'bg-purple-600',
  };

  const backgroundClasses = {
    primary: 'bg-blue-100',
    success: 'bg-green-100',
    warning: 'bg-yellow-100',
    danger: 'bg-red-100',
    info: 'bg-cyan-100',
    purple: 'bg-purple-100',
  };

  return (
    <div className={`w-full ${className}`} dir={direction}>
      {/* Label and Percentage */}
      {(showLabel || showPercentage) && (
        <div className="flex justify-between items-center mb-1">
          {showLabel && (
            <span className="text-sm font-medium text-gray-700">{label}</span>
          )}
          {showPercentage && (
            <span className="text-sm text-gray-500">
              {Math.round(percentage)}%
            </span>
          )}
        </div>
      )}

      {/* Progress Bar */}
      <div
        className={`
        w-full rounded-full overflow-hidden
        ${sizeClasses[size]}
        ${backgroundClasses[variant]}
      `}
      >
        <div
          className={`
            h-full transition-all duration-300 ease-out rounded-full
            ${variantClasses[variant]}
            ${animated ? 'animate-pulse' : ''}
            ${striped ? 'bg-stripe animate-stripe' : ''}
          `}
          style={{ width: `${percentage}%`, float: isRtl ? 'right' : 'left' }}
        >
          {striped && (
            <div className="h-full bg-gradient-to-r from-transparent via-white/30 to-transparent opacity-50"></div>
          )}
        </div>
      </div>

      {/* Progress Text (if not showing percentage above) */}
      {!showPercentage && !showLabel && (
        <div className="mt-1 text-xs text-gray-500 text-center">
          {progress} of {total}
        </div>
      )}
    </div>
  );
};

export default ProgressBar;
