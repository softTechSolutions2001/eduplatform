import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';

// Replace with actual API service when it's available
const fetchBlogPosts = async (limit = 3) => {
  // Simulating API call until the actual endpoint is available
  return new Promise(resolve => {
    setTimeout(() => {
      resolve({
        data: [
          {
            id: 1,
            title: '10 Technology Trends to Watch in 2025',
            excerpt:
              'Explore the emerging technologies that are reshaping industries and creating new opportunities for professionals.',
            slug: 'tech-trends-2025',
            date: 'April 14, 2025',
            readTime: '5 min read',
            category: 'Tech Trends',
          },
          {
            id: 2,
            title: '5 Evidence-Based Learning Techniques for Better Retention',
            excerpt:
              'Discover scientifically-proven strategies to improve your learning efficiency and remember more of what you study.',
            slug: 'learning-techniques',
            date: 'April 12, 2025',
            readTime: '4 min read',
            category: 'Learning Tips',
          },
          {
            id: 3,
            title: "From Beginner to Senior Developer: Lisa's Journey",
            excerpt:
              'Learn how Lisa transformed her career from a complete beginner to a senior developer in just 18 months.',
            slug: 'lisas-journey',
            date: 'April 10, 2025',
            readTime: '6 min read',
            category: 'Success Story',
          },
        ].slice(0, limit),
      });
    }, 500);
  });
};

const BlogPostList = ({
  title = 'Latest Insights',
  subtitle = 'Stay updated with industry trends, learning tips, and success stories',
  limit = 3,
}) => {
  const [posts, setPosts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const getBlogPosts = async () => {
      try {
        setLoading(true);
        // Replace with actual API call when available
        const response = await fetchBlogPosts(limit);
        setPosts(response.data);
        setLoading(false);
      } catch (err) {
        console.error('Failed to fetch blog posts:', err);
        setError('Failed to load blog posts');
        setLoading(false);
      }
    };

    getBlogPosts();
  }, [limit]);

  return (
    <section className="py-12 md:py-20 bg-white w-full">
      <div className="container mx-auto px-4 sm:px-6 lg:px-8">
        <div className="text-center mb-10 md:mb-16 reveal">
          <span className="bg-purple-50 text-purple-600 text-sm font-medium px-4 py-1.5 rounded-full inline-block mb-4">
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
            <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-purple-500"></div>
          </div>
        ) : error ? (
          <div className="bg-red-50 border-l-4 border-red-500 p-4 mb-8">
            <p className="text-red-700">{error}</p>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6 md:gap-8">
            {posts.map((post, index) => (
              <div
                className="card-premium reveal"
                style={{ animationDelay: `${(index + 1) * 100}ms` }}
                key={post.id}
              >
                <div className="w-full h-52 bg-gray-200 flex items-center justify-center text-gray-600">
                  {post.category}
                </div>
                <div className="p-6">
                  <div className="flex items-center mb-3 text-sm text-gray-500">
                    <span>{post.date}</span>
                    <span className="mx-2">•</span>
                    <span>{post.readTime}</span>
                  </div>
                  <h3 className="text-xl font-bold mb-3 font-display text-gray-900">
                    {post.title}
                  </h3>
                  <p className="text-gray-600 mb-4">{post.excerpt}</p>
                  <Link
                    to={`/blog/${post.slug}`}
                    className="text-primary-600 font-medium hover:text-primary-700 inline-flex items-center group"
                  >
                    <span>Read article</span>
                    <i className="fas fa-arrow-right ml-2 transform group-hover:translate-x-1 transition-transform"></i>
                  </Link>
                </div>
              </div>
            ))}
          </div>
        )}

        <div className="text-center mt-10 md:mt-14 reveal">
          <Link
            to="/blog"
            className="btn-premium bg-white border-2 border-purple-500 text-purple-600 hover:bg-purple-50"
          >
            View All Articles <i className="fas fa-arrow-right ml-2"></i>
          </Link>
        </div>
      </div>
    </section>
  );
};

export default BlogPostList;
