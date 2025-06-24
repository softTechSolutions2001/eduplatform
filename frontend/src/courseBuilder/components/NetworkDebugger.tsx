import React, { useEffect, useState } from 'react';

const NetworkDebugger = () => {
  const [requests, setRequests] = useState([]);

  useEffect(() => {
    // Only use in development
    if (process.env.NODE_ENV !== 'development') return;

    // Create a proxy for fetch
    const originalFetch = window.fetch;
    window.fetch = async function (...args) {
      const [url, options] = args;

      // Log the request
      console.log(`[DEBUG] Fetch request to ${url}`, options);

      // Track this request
      const requestInfo = {
        type: 'fetch',
        url,
        method: options?.method || 'GET',
        time: new Date().toISOString(),
      };

      try {
        const response = await originalFetch.apply(this, args);

        // Clone the response to log it (reading the body consumes it)
        const clone = response.clone();
        clone.text().then(body => {
          console.log(`[DEBUG] Response from ${url}:`, {
            status: response.status,
            statusText: response.statusText,
            headers: Object.fromEntries([...response.headers]),
            body: body.substring(0, 500) + (body.length > 500 ? '...' : ''),
          });
        });

        // Update requests
        setRequests(prev =>
          [
            ...prev,
            { ...requestInfo, status: response.status, success: response.ok },
          ].slice(-10)
        );

        return response;
      } catch (error) {
        console.log(`[DEBUG] Error fetching ${url}:`, error);

        // Update requests with error
        setRequests(prev =>
          [
            ...prev,
            { ...requestInfo, error: error.message, success: false },
          ].slice(-10)
        );

        throw error;
      }
    };

    // Create a proxy for XMLHttpRequest (Axios uses this)
    const originalXHR = window.XMLHttpRequest.prototype.open;
    window.XMLHttpRequest.prototype.open = function () {
      const [method, url] = arguments;

      // Track this request
      const requestInfo = {
        type: 'xhr',
        url,
        method,
        time: new Date().toISOString(),
      };

      // Listen for load event
      this.addEventListener('load', function () {
        console.log(`[DEBUG] XHR response from ${url}:`, {
          status: this.status,
          statusText: this.statusText,
          response:
            this.responseText?.substring(0, 500) +
            (this.responseText?.length > 500 ? '...' : ''),
        });

        // Update requests
        setRequests(prev =>
          [
            ...prev,
            {
              ...requestInfo,
              status: this.status,
              success: this.status >= 200 && this.status < 300,
            },
          ].slice(-10)
        );
      });

      // Listen for error event
      this.addEventListener('error', function () {
        console.log(`[DEBUG] XHR error for ${url}`);

        // Update requests with error
        setRequests(prev =>
          [
            ...prev,
            { ...requestInfo, error: 'Network error', success: false },
          ].slice(-10)
        );
      });

      return originalXHR.apply(this, arguments);
    };

    // Cleanup
    return () => {
      window.fetch = originalFetch;
      window.XMLHttpRequest.prototype.open = originalXHR;
    };
  }, []);

  // Only render in development
  if (process.env.NODE_ENV !== 'development') return null;

  return (
    <div
      style={{
        position: 'fixed',
        bottom: '10px',
        right: '10px',
        backgroundColor: 'rgba(0,0,0,0.8)',
        color: 'white',
        padding: '10px',
        borderRadius: '5px',
        maxHeight: '300px',
        overflowY: 'auto',
        zIndex: 9999,
        fontSize: '12px',
        maxWidth: '400px',
        display: requests.length ? 'block' : 'none',
      }}
    >
      <h4>Recent Network Requests</h4>
      <ul style={{ listStyle: 'none', padding: 0 }}>
        {requests.map((req, i) => (
          <li
            key={i}
            style={{
              marginBottom: '5px',
              padding: '5px',
              backgroundColor: req.success
                ? 'rgba(0,128,0,0.2)'
                : 'rgba(255,0,0,0.2)',
              borderRadius: '3px',
            }}
          >
            <div>
              <strong>{req.method}</strong> {req.url.split('?')[0]}
            </div>
            <div>
              Status: {req.status || 'N/A'}
              {req.error && (
                <span style={{ color: 'red' }}> Error: {req.error}</span>
              )}
            </div>
          </li>
        ))}
      </ul>
    </div>
  );
};

export default NetworkDebugger;
