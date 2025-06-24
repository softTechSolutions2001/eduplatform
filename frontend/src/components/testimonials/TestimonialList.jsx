import React, { useState, useEffect } from 'react';

// Replace with actual API service when available
const fetchTestimonials = async (limit = 3) => {
  // Simulating API call until the actual endpoint is available
  return new Promise(resolve => {
    setTimeout(() => {
      resolve({
        data: [
          {
            id: 1,
            name: 'Sarah Johnson',
            role: 'Software Engineer, Tech Innovations Inc.',
            quote:
              "SoftTech's adaptive learning system transformed my educational journey. The personalized approach and interactive labs helped me secure my dream job as a software developer.",
            avatar_color: '#3d74f4',
            rating: 5,
          },
          {
            id: 2,
            name: 'Dr. Michael Chen',
            role: 'Computer Science Professor, Bay Area University',
            quote:
              "As an educator, I'm impressed by the pedagogical thought behind every aspect of this platform. My students have shown remarkable improvement in comprehension and practical applications.",
            avatar_color: '#19b29a',
            rating: 5,
          },
          {
            id: 3,
            name: 'Alex Rodriguez',
            role: 'Data Scientist, Analytics Pro',
            quote:
              'The personalized learning paths and AI assistant helped me understand complex concepts I struggled with for years. The community forums provided invaluable peer support throughout my journey.',
            avatar_color: '#ff7425',
            rating: 5,
          },
        ].slice(0, limit),
      });
    }, 600);
  });
};

const TestimonialList = ({
  title = 'Community Voices',
  subtitle = 'Join our collaborative community where knowledge sharing and peer learning thrive',
  limit = 3,
}) => {
  const [testimonials, setTestimonials] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Function to render avatar
  const renderAvatar = (name, bgColor) => {
    const initials = name
      .split(' ')
      .map(part => part[0])
      .join('')
      .toUpperCase();
    return (
      <div
        className="h-12 w-12 rounded-full flex items-center justify-center text-white shadow-sm overflow-hidden mr-4"
        style={{ backgroundColor: bgColor }}
      >
        <div className="h-full w-full flex items-center justify-center">
          {initials}
        </div>
      </div>
    );
  };

  useEffect(() => {
    const getTestimonials = async () => {
      try {
        setLoading(true);
        // Replace with actual API call when available
        const response = await fetchTestimonials(limit);
        setTestimonials(response.data);
        setLoading(false);
      } catch (err) {
        console.error('Failed to fetch testimonials:', err);
        setError('Failed to load testimonials');
        setLoading(false);
      }
    };

    getTestimonials();
  }, [limit]);

  return (
    <section className="py-12 md:py-20 bg-white w-full">
      <div className="container mx-auto px-4 sm:px-6 lg:px-8">
        <div className="text-center mb-10 md:mb-16 reveal">
          <span className="bg-blue-50 text-blue-600 text-sm font-medium px-4 py-1.5 rounded-full inline-block mb-4">
            {title.toUpperCase()}
          </span>
          <h2 className="text-2xl md:text-3xl lg:text-4xl font-bold mb-4 font-display text-gray-900">
            {title}
          </h2>
          <p className="text-gray-600 max-w-2xl mx-auto text-base lg:text-lg">
            {subtitle}
          </p>
        </div>

        {loading ? (
          <div className="flex justify-center my-12">
            <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-blue-500"></div>
          </div>
        ) : error ? (
          <div className="bg-red-50 border-l-4 border-red-500 p-4 mb-8">
            <p className="text-red-700">{error}</p>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 md:gap-8">
            {testimonials.map((testimonial, index) => (
              <div
                className="bg-gray-50 p-6 md:p-8 rounded-2xl shadow-testimonial hover:shadow-xl transition-all hover:-translate-y-1 reveal"
                style={{ animationDelay: `${(index + 1) * 100}ms` }}
                key={testimonial.id}
              >
                <div className="text-yellow-400 flex mb-4">
                  {[...Array(testimonial.rating)].map((_, i) => (
                    <i className="fas fa-star" key={i}></i>
                  ))}
                </div>
                <p className="text-gray-700 mb-6 italic">{testimonial.quote}</p>
                <div className="flex items-center">
                  {renderAvatar(testimonial.name, testimonial.avatar_color)}
                  <div>
                    <h4 className="font-semibold text-gray-900">
                      {testimonial.name}
                    </h4>
                    <p className="text-sm text-gray-500">{testimonial.role}</p>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </section>
  );
};

export default TestimonialList;
