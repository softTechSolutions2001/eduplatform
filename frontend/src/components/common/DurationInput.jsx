import { useCallback, useState } from 'react';
import {
  formatDuration,
  parseDurationToMinutes,
} from '../../utils/formatDuration';

/**
 * DurationInput Component
 *
 * Provides an intuitive interface for inputting course/lesson durations
 * with 10-minute increments and automatic hours/minutes conversion.
 *
 * Features:
 * - Input/output in minutes for consistency with backend
 * - Display in human-readable format (e.g., "2 hours 30 minutes")
 * - Quick increment/decrement buttons with 10-minute steps
 * - Manual text input with validation
 * - Supports both controlled and uncontrolled usage
 */
const DurationInput = ({
  value = 0, // Duration in minutes
  onChange = () => {}, // Callback with duration in minutes
  min = 10, // Minimum duration in minutes
  max = 600, // Maximum duration in minutes (10 hours)
  step = 10, // Step size in minutes
  placeholder = 'Enter duration...',
  className = '',
  disabled = false,
  required = false,
  error = null,
  label = null,
  showQuickButtons = true,
  id = null,
  ...props
}) => {
  const [isTextInput, setIsTextInput] = useState(false);
  const [textValue, setTextValue] = useState('');

  // Convert minutes to display format
  const displayValue = formatDuration(value);

  // Common duration presets (in minutes)
  const quickDurations = [
    { label: '15 min', value: 15 },
    { label: '30 min', value: 30 },
    { label: '45 min', value: 45 },
    { label: '1 hour', value: 60 },
    { label: '1.5 hours', value: 90 },
    { label: '2 hours', value: 120 },
  ];

  // Handle increment/decrement
  const handleAdjust = useCallback(
    adjustment => {
      const newValue = Math.max(min, Math.min(max, value + adjustment));
      onChange(newValue);
    },
    [value, min, max, onChange]
  );

  // Handle manual text input
  const handleTextChange = useCallback(e => {
    setTextValue(e.target.value);
  }, []);

  // Handle text input submit
  const handleTextSubmit = useCallback(() => {
    const parsedMinutes = parseDurationToMinutes(textValue);
    if (parsedMinutes && parsedMinutes >= min && parsedMinutes <= max) {
      onChange(parsedMinutes);
    }
    setIsTextInput(false);
    setTextValue('');
  }, [textValue, min, max, onChange]);

  // Handle text input blur
  const handleTextBlur = useCallback(() => {
    handleTextSubmit();
  }, [handleTextSubmit]);

  // Handle text input key press
  const handleTextKeyPress = useCallback(
    e => {
      if (e.key === 'Enter') {
        handleTextSubmit();
      } else if (e.key === 'Escape') {
        setIsTextInput(false);
        setTextValue('');
      }
    },
    [handleTextSubmit]
  );

  // Switch to text input mode
  const switchToTextInput = useCallback(() => {
    setIsTextInput(true);
    setTextValue(displayValue);
  }, [displayValue]);

  // Quick duration selection
  const handleQuickDuration = useCallback(
    duration => {
      onChange(duration);
    },
    [onChange]
  );

  const inputClasses = [
    'w-full px-3 py-2 border rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500',
    disabled ? 'bg-gray-100 cursor-not-allowed' : 'bg-white',
    error ? 'border-red-300' : 'border-gray-300',
    className,
  ]
    .filter(Boolean)
    .join(' ');

  const buttonClasses =
    'px-2 py-1 text-sm border border-gray-300 rounded hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed';

  return (
    <div className="space-y-2">
      {/* Label */}
      {label && (
        <label htmlFor={id} className="block text-sm font-medium text-gray-700">
          {label}
          {required && <span className="text-red-500 ml-1">*</span>}
        </label>
      )}

      {/* Main input area */}
      <div className="flex items-center space-x-2">
        {/* Decrement button */}
        <button
          type="button"
          onClick={() => handleAdjust(-step)}
          disabled={disabled || value <= min}
          className={buttonClasses}
          title={`Decrease by ${step} minutes`}
        >
          −
        </button>

        {/* Duration display/input */}
        <div className="flex-1 relative">
          {isTextInput ? (
            <input
              type="text"
              value={textValue}
              onChange={handleTextChange}
              onBlur={handleTextBlur}
              onKeyDown={handleTextKeyPress}
              className={inputClasses}
              placeholder={placeholder}
              autoFocus
              {...props}
            />
          ) : (
            <button
              type="button"
              onClick={switchToTextInput}
              disabled={disabled}
              className={`${inputClasses} text-left cursor-pointer hover:bg-gray-50`}
              title="Click to edit duration manually"
            >
              {displayValue || placeholder}
            </button>
          )}
        </div>

        {/* Increment button */}
        <button
          type="button"
          onClick={() => handleAdjust(step)}
          disabled={disabled || value >= max}
          className={buttonClasses}
          title={`Increase by ${step} minutes`}
        >
          +
        </button>
      </div>

      {/* Quick duration buttons */}
      {showQuickButtons && !disabled && (
        <div className="flex flex-wrap gap-1">
          {quickDurations.map(duration => (
            <button
              key={duration.value}
              type="button"
              onClick={() => handleQuickDuration(duration.value)}
              className={`px-2 py-1 text-xs border rounded text-gray-600 hover:bg-gray-50 focus:outline-none focus:ring-1 focus:ring-blue-500 ${
                value === duration.value
                  ? 'bg-blue-50 border-blue-300 text-blue-700'
                  : 'border-gray-300'
              }`}
              title={`Set duration to ${duration.label}`}
            >
              {duration.label}
            </button>
          ))}
        </div>
      )}

      {/* Error message */}
      {error && <p className="text-sm text-red-600 mt-1">{error}</p>}

      {/* Help text */}
      <p className="text-xs text-gray-500">
        Duration in minutes. Use +/− buttons for {step}-minute increments, or
        click to enter manually.
      </p>
    </div>
  );
};

export default DurationInput;
