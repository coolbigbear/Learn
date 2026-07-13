import { useState, useEffect, useCallback } from 'react';
import * as api from '../api/client.js';
import { useAuth } from './useAuth.jsx';

export function useProgress() {
  const { isAuthenticated } = useAuth();
  const [progress, setProgress] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchProgress = useCallback(async () => {
    if (!isAuthenticated) {
      setLoading(false);
      setProgress(null);
      return;
    }

    try {
      setLoading(true);
      setError(null);
      const data = await api.getProgress();
      setProgress(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }, [isAuthenticated]);

  useEffect(() => {
    fetchProgress();
  }, [fetchProgress]);

  const fetchLessonProgress = useCallback(async (lessonSlug) => {
    try {
      const data = await api.getLessonProgress(lessonSlug);
      return data;
    } catch (err) {
      throw err;
    }
  }, []);

  return {
    progress,
    loading,
    error,
    refetch: fetchProgress,
    fetchLessonProgress,
  };
}

export default useProgress;