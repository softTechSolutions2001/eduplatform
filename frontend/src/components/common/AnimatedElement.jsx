import React, { useEffect, useRef, useState } from 'react';
import PropTypes from 'prop-types';

/**
 * AnimatedElement Component
 *
 * This component adds reveal-on-scroll animations to any child elements.
 * It tracks when the element enters the viewport and applies appropriate
 * animation classes.
 *
 * Usage:
 * <AnimatedElement animation="fade-up" delay={300}>
 *   <YourComponent />
 * </AnimatedElement>
 */
const AnimatedElement = ({
  children,
  animation = 'fade',
  delay = 0,
  threshold = 0.2,
  className = '',
  once = true,
  ...props
}) => {
  const [isVisible, setIsVisible] = useState(false);
  const elementRef = useRef(null);

  // Map of animation types to CSS classes
  const animationClasses = {
    fade: 'animate-fade-in',
    'fade-up': 'animate-fade-in-up',
    'slide-down': 'animate-slide-down',
    reveal: 'reveal',
  };

  useEffect(() => {
    const element = elementRef.current;
    if (!element) return;

    const observer = new IntersectionObserver(
      ([entry]) => {
        if (entry.isIntersecting) {
          setIsVisible(true);
          if (once) {
            observer.unobserve(element);
          }
        } else if (!once) {
          setIsVisible(false);
        }
      },
      {
        threshold,
        rootMargin: '0px 0px -50px 0px',
      }
    );

    observer.observe(element);

    return () => {
      if (element) {
        observer.unobserve(element);
      }
    };
  }, [once, threshold]);

  // Calculate animation class based on type and visibility
  const getAnimationClass = () => {
    if (!isVisible) {
      return animation === 'reveal' ? 'reveal' : '';
    }

    return animation === 'reveal'
      ? 'reveal active'
      : animationClasses[animation] || animationClasses.fade;
  };

  // Calculate delay style
  const delayStyle = delay
    ? { animationDelay: `${delay}ms`, transitionDelay: `${delay}ms` }
    : {};

  return (
    <div
      ref={elementRef}
      className={`${getAnimationClass()} ${className}`}
      style={delayStyle}
      {...props}
    >
      {children}
    </div>
  );
};

AnimatedElement.propTypes = {
  children: PropTypes.node.isRequired,
  animation: PropTypes.oneOf(['fade', 'fade-up', 'slide-down', 'reveal']),
  delay: PropTypes.number,
  threshold: PropTypes.number,
  className: PropTypes.string,
  once: PropTypes.bool,
};

export default AnimatedElement;
