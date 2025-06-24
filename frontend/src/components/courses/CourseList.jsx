import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { courseService } from '../../services/api';

const CourseList = ({
  title = 'Featured Courses',
  subtitle = 'Explore our comprehensive educational content',
  limit = 3,
  featured = true,
  category = null,
  showViewAll = true,
}) => {
  const [courses, setCourses] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchCourses = async () => {
      try {
        setLoading(true);
        const params = {
          limit,
          is_published: true,
        };

        if (featured) {
          params.is_featured = true;
        }

        if (category) {
          params.category = category;
        }

        const response = await courseService.getAllCourses(params);
        const coursesData = response.data.results || response.data || [];

        if (coursesData.length > 0) {
          setCourses(coursesData);
        } else {
          // Fallback data if no courses are returned
          setCourses(
            [
              {
                id: 1,
                title: 'Full-Stack Web Development Bootcamp',
                slug: 'web-development',
                subtitle:
                  'Learn front-end and back-end development with modern frameworks.',
                duration: '60 hours',
                level: 'Intermediate',
                has_certificate: true,
                price: 89.99,
                discount_price: null,
                rating: 4.8,
                reviews_count: 2400,
                category: { name: 'Programming' },
                is_bestseller: true,
                bg_color: 'primary-500',
                text_color: 'primary-600',
                bg_light: 'blue-50',
              },
              {
                id: 2,
                title: 'Data Science & Machine Learning',
                slug: 'data-science',
                subtitle:
                  'Master data analysis, visualization, and ML algorithms.',
                duration: '48 hours',
                level: 'Advanced',
                has_certificate: true,
                price: 99.99,
                discount_price: null,
                rating: 4.9,
                reviews_count: 876,
                category: { name: 'Data Science' },
                is_new: true,
                bg_color: 'secondary-500',
                text_color: 'secondary-600',
                bg_light: 'orange-50',
              },
              {
                id: 3,
                title: 'Comprehensive Software Testing',
                slug: 'software-testing',
                subtitle:
                  'Master the art and science of testing software effectively.',
                duration: '40 hours',
                level: 'All Levels',
                has_certificate: true,
                price: 79.99,
                discount_price: null,
                rating: 4.9,
                reviews_count: 42,
                category: { name: 'Quality Assurance' },
                is_new: true,
                bg_color: 'blue-500',
                text_color: 'blue-600',
                bg_light: 'blue-50',
              },
            ].slice(0, limit)
          );
        }

        setLoading(false);
      } catch (err) {
        console.error('Failed to fetch courses:', err);
        setError('Failed to load courses');
        setLoading(false);
      }
    };

    fetchCourses();
  }, [limit, featured, category]);

  const renderCourseCard = (course, index) => {
    return (
      <div
        className="card-premium reveal w-full"
        style={{ animationDelay: `${(index + 1) * 100}ms` }}
        key={course.id || index}
      >
        <div className="relative">
          {course.thumbnail ? (
            <img
              src={course.thumbnail}
              alt={course.title}
              className="w-full h-52 object-cover"
              loading="lazy"
            />
          ) : (
            <div
              className={`w-full h-52 bg-${course.bg_color || 'primary-500'} flex items-center justify-center text-white text-xl font-bold`}
            >
              {course.title}
            </div>
          )}

          {course.is_bestseller && (
            <div className="absolute top-4 right-4 bg-secondary-500 text-white text-xs font-semibold px-3 py-1.5 rounded-full shadow-sm">
              BESTSELLER
            </div>
          )}

          {course.is_new && (
            <div className="absolute top-4 right-4 bg-green-500 text-white text-xs font-semibold px-3 py-1.5 rounded-full shadow-sm">
              NEW
            </div>
          )}
        </div>
        <div className="p-6">
          <div className="flex items-center mb-3">
            <span
              className={`bg-${course.bg_light || 'blue-50'} text-${course.text_color || 'primary-600'} text-xs font-semibold px-3 py-1 rounded-lg`}
            >
              {course.category?.name || 'Course'}
            </span>
            <div className="flex items-center ml-auto text-yellow-500">
              <i className="fas fa-star"></i>
              <span className="text-sm text-gray-700 ml-1.5 font-medium">
                {course.rating?.toFixed(1) || '4.5'}
              </span>
              <span className="text-sm text-gray-500 ml-1">
                ({course.reviews_count || 0})
              </span>
            </div>
          </div>
          <h3 className="text-xl font-bold mb-3 font-display text-gray-900">
            {course.title}
          </h3>
          <p className="text-gray-600 mb-4 line-clamp-2">{course.subtitle}</p>
          <div className="flex flex-wrap items-center text-sm text-gray-500 mb-5 gap-2 md:gap-4">
            <div className="flex items-center">
              <i className="fa-regular fa-clock mr-1.5"></i>{' '}
              {course.duration || 'Self-paced'}
            </div>
            <div className="flex items-center">
              <i className="fa-solid fa-signal mr-1.5"></i>{' '}
              {course.level || 'All Levels'}
            </div>
            {course.has_certificate && (
              <div className="flex items-center">
                <i className="fa-solid fa-certificate mr-1.5"></i> Certificate
              </div>
            )}
          </div>
          <div className="flex items-center justify-between pt-3 border-t border-gray-100">
            <span className="text-primary-600 font-bold text-lg">
              ${course.discount_price || course.price}
              {course.discount_price && (
                <span className="text-gray-400 line-through ml-2 text-sm">
                  ${course.price}
                </span>
              )}
            </span>
            <Link
              to={`/courses/${course.slug}`}
              className="px-4 py-2 bg-primary-500 text-white rounded-lg hover:bg-primary-600 transition-colors shadow-sm"
            >
              View Course
            </Link>
          </div>
        </div>
      </div>
    );
  };

  return (
    <section className="py-12 md:py-20 bg-white w-full">
      <div className="container mx-auto px-4 sm:px-6 lg:px-8">
        <div className="text-center mb-10 md:mb-16 reveal">
          <span className="bg-primary-50 text-primary-600 text-sm font-medium px-4 py-1.5 rounded-full inline-block mb-4">
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
            <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-primary-500"></div>
          </div>
        ) : error ? (
          <div className="bg-red-50 border-l-4 border-red-500 p-4 mb-8">
            <p className="text-red-700">{error}</p>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 md:gap-8">
            {courses.map((course, index) => renderCourseCard(course, index))}
          </div>
        )}

        {showViewAll && (
          <div className="text-center mt-10 md:mt-14 reveal">
            <Link
              to="/courses"
              className="btn-premium bg-white border-2 border-primary-500 text-primary-600 hover:bg-primary-50"
            >
              Explore All Courses <i className="fas fa-arrow-right ml-2"></i>
            </Link>
          </div>
        )}
      </div>
    </section>
  );
};

export default CourseList;
