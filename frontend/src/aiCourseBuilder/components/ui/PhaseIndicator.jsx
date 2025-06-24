import AccessTimeIcon from '@mui/icons-material/AccessTime';
import CheckIcon from '@mui/icons-material/Check';
import React, { useContext } from 'react';
import { DirectionContext } from '../../../contexts/DirectionContext.jsx';

const PhaseIndicator = ({
  phases = [],
  currentPhase = 0,
  completedPhases = [],
  variant = 'horizontal',
  showLabels = true,
  showProgress = true,
  className = '',
}) => {
  // Get the current direction (LTR or RTL)
  const { direction } = useContext(DirectionContext) || { direction: 'ltr' };
  const isRtl = direction === 'rtl';

  // Convert currentPhase from ID to index if it's a string
  const currentPhaseIndex =
    typeof currentPhase === 'string'
      ? phases.findIndex(p => p.id === currentPhase)
      : currentPhase;

  const getPhaseStatus = phaseIndex => {
    if (completedPhases.includes(phaseIndex)) return 'completed';
    if (phaseIndex === currentPhaseIndex) return 'current';
    if (phaseIndex < currentPhaseIndex) return 'completed';
    return 'upcoming';
  };

  const getPhaseIcon = (phase, status) => {
    if (status === 'completed') {
      return <CheckIcon className="h-4 w-4 text-white" />;
    }

    if (status === 'current') {
      return (
        <div className="w-3 h-3 bg-white rounded-full animate-pulse"></div>
      );
    }

    return <div className="w-3 h-3 bg-gray-400 rounded-full"></div>;
  };

  const getPhaseClasses = status => {
    switch (status) {
      case 'completed':
        return 'bg-green-600 border-green-600 text-white';
      case 'current':
        return 'bg-blue-600 border-blue-600 text-white ring-4 ring-blue-100';
      case 'upcoming':
        return 'bg-gray-200 border-gray-300 text-gray-500';
      default:
        return 'bg-gray-200 border-gray-300 text-gray-500';
    }
  };

  const getConnectorClasses = (fromStatus, toStatus) => {
    if (
      fromStatus === 'completed' &&
      (toStatus === 'completed' || toStatus === 'current')
    ) {
      return 'bg-green-600';
    }
    return 'bg-gray-300';
  };

  if (variant === 'vertical') {
    return (
      <div className={`space-y-4 ${className}`}>
        {phases.map((phase, index) => {
          const status = getPhaseStatus(index);
          return (
            <div
              key={index}
              className={`flex items-start ${isRtl ? 'space-x-reverse space-x-3' : 'space-x-3'}`}
            >
              {/* Phase Circle */}
              <div
                className={`
                relative flex items-center justify-center w-8 h-8 rounded-full border-2 transition-all duration-200
                ${getPhaseClasses(status)}
              `}
              >
                {getPhaseIcon(phase, status)}
              </div>

              {/* Phase Content */}
              <div className="flex-1 min-w-0">
                {showLabels && (
                  <div>
                    <h4
                      className={`text-sm font-medium ${
                        status === 'current'
                          ? 'text-blue-900'
                          : status === 'completed'
                            ? 'text-green-900'
                            : 'text-gray-700'
                      }`}
                    >
                      {phase.name || `Phase ${index + 1}`}
                    </h4>
                    {phase.description && (
                      <p className="text-xs text-gray-500 mt-1">
                        {phase.description}
                      </p>
                    )}
                  </div>
                )}

                {showProgress && phase.progress !== undefined && (
                  <div className="mt-2">
                    <div className="flex justify-between text-xs text-gray-500 mb-1">
                      <span>Progress</span>
                      <span>{Math.round(phase.progress)}%</span>
                    </div>
                    <div className="w-full bg-gray-200 rounded-full h-1.5">
                      <div
                        className={`h-1.5 rounded-full transition-all duration-300 ${
                          status === 'completed'
                            ? 'bg-green-600'
                            : status === 'current'
                              ? 'bg-blue-600'
                              : 'bg-gray-400'
                        }`}
                        style={{
                          width: `${Math.min(phase.progress || 0, 100)}%`,
                        }}
                      ></div>
                    </div>
                  </div>
                )}

                {status === 'current' && phase.estimatedTime && (
                  <div className="flex items-center mt-2 text-xs text-blue-600">
                    <AccessTimeIcon
                      style={{
                        width: '0.75rem',
                        height: '0.75rem',
                        marginRight: '0.25rem',
                      }}
                    />
                    <span>{phase.estimatedTime} remaining</span>
                  </div>
                )}
              </div>

              {/* Connector Line */}
              {index < phases.length - 1 && (
                <div className="absolute left-4 mt-8 w-px h-6 bg-gray-300"></div>
              )}
            </div>
          );
        })}
      </div>
    );
  }

  // Horizontal layout
  return (
    <div
      className={`flex items-center ${isRtl ? 'flex-row-reverse' : ''} ${className}`}
    >
      {phases.map((phase, index) => {
        const status = getPhaseStatus(index);
        const nextStatus =
          index < phases.length - 1 ? getPhaseStatus(index + 1) : null;

        return (
          <React.Fragment key={index}>
            {/* Phase Container */}
            <div className="flex flex-col items-center">
              {/* Phase Circle */}
              <div
                className={`
                relative flex items-center justify-center w-10 h-10 rounded-full border-2 transition-all duration-200
                ${getPhaseClasses(status)}
              `}
              >
                {getPhaseIcon(phase, status)}

                {/* Phase Number (if no icon) */}
                {status === 'upcoming' && (
                  <span className="text-sm font-medium">{index + 1}</span>
                )}
              </div>

              {/* Phase Label */}
              {showLabels && (
                <div className="mt-2 text-center max-w-24">
                  <h4
                    className={`text-xs font-medium ${
                      status === 'current'
                        ? 'text-blue-900'
                        : status === 'completed'
                          ? 'text-green-900'
                          : 'text-gray-700'
                    }`}
                  >
                    {phase.name || `Phase ${index + 1}`}
                  </h4>
                  {status === 'current' &&
                    showProgress &&
                    phase.progress !== undefined && (
                      <div className="mt-1 text-xs text-blue-600">
                        {Math.round(phase.progress)}%
                      </div>
                    )}
                  {status === 'current' && phase.estimatedTime && (
                    <div className="flex items-center justify-center mt-1 text-xs text-blue-600">
                      <AccessTimeIcon
                        style={{
                          width: '0.75rem',
                          height: '0.75rem',
                          marginRight: '0.25rem',
                        }}
                      />
                      <span>{phase.estimatedTime}</span>
                    </div>
                  )}
                </div>
              )}
            </div>

            {/* Connector Line */}
            {index < phases.length - 1 && (
              <div
                className={`
                flex-1 h-0.5 mx-3 transition-all duration-200
                ${getConnectorClasses(status, nextStatus)}
              `}
              ></div>
            )}
          </React.Fragment>
        );
      })}
    </div>
  );
};

export default PhaseIndicator;
