import React from 'react';
import { Link } from 'react-router-dom';

const NotFoundPage = () => {
  return (
    <div className="not-found-container" style={styles.container}>
      <h1 style={styles.heading}>404</h1>
      <h2 style={styles.subHeading}>Oops! Page Not Found</h2>
      <p style={styles.message}>
        The page you're looking for doesn't exist or has been moved.
      </p>
      <Link to="/" style={styles.link}>
        Go Back to Home
      </Link>
    </div>
  );
};

// Optional Inline Styles
const styles = {
  container: {
    display: 'flex',
    flexDirection: 'column',
    alignItems: 'center',
    justifyContent: 'center',
    height: '100vh',
    textAlign: 'center',
    backgroundColor: '#f9f9f9',
    color: '#333',
    padding: '20px',
  },
  heading: {
    fontSize: '6rem',
    fontWeight: 'bold',
    marginBottom: '20px',
  },
  subHeading: {
    fontSize: '2rem',
    marginBottom: '10px',
  },
  message: {
    fontSize: '1.2rem',
    marginBottom: '20px',
  },
  link: {
    fontSize: '1rem',
    color: '#007BFF',
    textDecoration: 'none',
    fontWeight: 'bold',
  },
};

export default NotFoundPage;
