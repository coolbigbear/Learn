import { useState, useEffect } from 'react';
import { useAuth } from '../hooks/useAuth.jsx';
import LessonCard from '../components/LessonCard.jsx';
import * as api from '../api/client.js';

export default function Lessons() {
  const { isAuthenticated } = useAuth();
  const [lessons, setLessons] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    async function fetchLessons() {
      try {
        const data = await api.getLessons();
        setLessons(data.lessons);
      } catch (err) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    }
    fetchLessons();
  }, []);

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-gray-500 text-lg">Loading lessons...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-red-50 border border-red-200 text-red-700 p-4 rounded-lg">
        Failed to load lessons: {error}
      </div>
    );
  }

  return (
    <div>
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900">Python Tutorials</h1>
        <p className="mt-2 text-gray-500">
          {isAuthenticated
            ? 'Continue your learning journey through these interactive lessons.'
            : 'Sign in to track your progress as you work through the lessons.'}
        </p>
      </div>
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
        {lessons.map((lesson) => (
          <LessonCard key={lesson.id} lesson={lesson} />
        ))}
      </div>
      {lessons.length === 0 && (
        <div className="text-center py-12 text-gray-400">
          No lessons available yet. Check back soon!
        </div>
      )}
    </div>
  );
}