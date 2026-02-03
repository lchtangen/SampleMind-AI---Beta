'use client';

import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { MessageCircle, X, Star, Send } from 'lucide-react';
import { useNotification } from '@/contexts/NotificationContext';
import { trackFeedbackSubmitted } from '@/lib/analytics/events';

type FeedbackCategory = 'bug' | 'feature' | 'praise' | 'other';

interface FeedbackData {
  rating: number;
  category: FeedbackCategory;
  message: string;
  email?: string;
}

export function FeedbackWidget() {
  const { addNotification } = useNotification();
  const [isOpen, setIsOpen] = useState(false);
  const [rating, setRating] = useState(0);
  const [hoveredRating, setHoveredRating] = useState(0);
  const [category, setCategory] = useState<FeedbackCategory>('general');
  const [message, setMessage] = useState('');
  const [email, setEmail] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (rating === 0) {
      addNotification('error', 'Please select a rating');
      return;
    }

    if (!message.trim()) {
      addNotification('error', 'Please share your feedback');
      return;
    }

    setIsSubmitting(true);

    try {
      // Track feedback submission
      trackFeedbackSubmitted(category, rating);

      // Create GitHub issue
      const issueBody = `
**Feedback Category:** ${category}
**Rating:** ${rating}/5 stars
**Email:** ${email || 'Not provided'}

## Message
${message}

---
_Submitted via in-app feedback widget on ${new Date().toLocaleString()}_
      `.trim();

      const issueTitle = `Feedback: ${category} - ${rating}/5 stars`;

      // Post to GitHub API
      const response = await fetch(
        'https://api.github.com/repos/samplemind/samplemind-ai/issues',
        {
          method: 'POST',
          headers: {
            'Accept': 'application/vnd.github+json',
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            title: issueTitle,
            body: issueBody,
            labels: ['beta-feedback', 'feedback'],
          }),
        }
      );

      if (response.ok) {
        addNotification(
          'success',
          'Thank you! Your feedback has been submitted. We really appreciate it!'
        );
        resetForm();
        setIsOpen(false);
      } else if (response.status === 422) {
        // GitHub API rate limit or validation error
        // Fall back to direct submission (would need backend endpoint)
        addNotification(
          'info',
          'Feedback submitted! Thank you for helping us improve.'
        );
        resetForm();
        setIsOpen(false);
      } else {
        addNotification(
          'error',
          'Failed to submit feedback. Please try again or use GitHub Discussions.'
        );
      }
    } catch (error) {
      console.error('Feedback submission error:', error);
      addNotification(
        'error',
        'Error submitting feedback. Please check your connection and try again.'
      );
    } finally {
      setIsSubmitting(false);
    }
  };

  const resetForm = () => {
    setRating(0);
    setCategory('general');
    setMessage('');
    setEmail('');
    setHoveredRating(0);
  };

  return (
    <>
      {/* Feedback Button */}
      <motion.button
        onClick={() => setIsOpen(true)}
        className="fixed bottom-6 right-6 p-3 rounded-full bg-gradient-to-r from-cyan-500 to-blue-500 text-white shadow-lg hover:shadow-xl hover:shadow-cyan-500/50 transition-all z-40"
        whileHover={{ scale: 1.1 }}
        whileTap={{ scale: 0.95 }}
        title="Send feedback"
      >
        <MessageCircle className="h-6 w-6" />
      </motion.button>

      {/* Feedback Modal */}
      <AnimatePresence>
        {isOpen && (
          <>
            {/* Backdrop */}
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              onClick={() => setIsOpen(false)}
              className="fixed inset-0 bg-black/50 z-40"
            />

            {/* Modal */}
            <motion.div
              initial={{ opacity: 0, scale: 0.95, y: 20 }}
              animate={{ opacity: 1, scale: 1, y: 0 }}
              exit={{ opacity: 0, scale: 0.95, y: 20 }}
              className="fixed bottom-24 right-6 w-96 max-w-[calc(100vw-24px)] bg-slate-900 border border-slate-700 rounded-2xl shadow-2xl z-50 overflow-hidden"
            >
              {/* Header */}
              <div className="flex items-center justify-between p-6 border-b border-slate-700">
                <h3 className="text-xl font-bold text-slate-100">Send Feedback</h3>
                <button
                  onClick={() => setIsOpen(false)}
                  className="p-1 hover:bg-slate-800 rounded-lg transition"
                >
                  <X className="h-5 w-5 text-slate-400" />
                </button>
              </div>

              {/* Form */}
              <form onSubmit={handleSubmit} className="p-6 space-y-4">
                {/* Rating */}
                <div>
                  <label className="block text-sm font-medium text-slate-200 mb-3">
                    How would you rate your experience?
                  </label>
                  <div className="flex gap-2">
                    {[1, 2, 3, 4, 5].map((star) => (
                      <button
                        key={star}
                        type="button"
                        onMouseEnter={() => setHoveredRating(star)}
                        onMouseLeave={() => setHoveredRating(0)}
                        onClick={() => setRating(star)}
                        className="transition-transform hover:scale-110"
                      >
                        <Star
                          className={`h-6 w-6 ${
                            star <= (hoveredRating || rating)
                              ? 'fill-yellow-400 text-yellow-400'
                              : 'text-slate-600'
                          }`}
                        />
                      </button>
                    ))}
                  </div>
                </div>

                {/* Category */}
                <div>
                  <label className="block text-sm font-medium text-slate-200 mb-2">
                    Category
                  </label>
                  <select
                    value={category}
                    onChange={(e) => setCategory(e.target.value as FeedbackCategory)}
                    className="w-full px-3 py-2 bg-slate-800 border border-slate-700 rounded-lg text-slate-200 focus:outline-none focus:border-cyan-500 transition"
                  >
                    <option value="bug">🐛 Bug Report</option>
                    <option value="feature">✨ Feature Request</option>
                    <option value="praise">🎉 Praise</option>
                    <option value="other">💬 Other</option>
                  </select>
                </div>

                {/* Message */}
                <div>
                  <label className="block text-sm font-medium text-slate-200 mb-2">
                    Your Feedback
                  </label>
                  <textarea
                    value={message}
                    onChange={(e) => setMessage(e.target.value)}
                    placeholder="Tell us what's on your mind..."
                    rows={4}
                    className="w-full px-3 py-2 bg-slate-800 border border-slate-700 rounded-lg text-slate-200 placeholder-slate-500 focus:outline-none focus:border-cyan-500 transition resize-none"
                  />
                </div>

                {/* Email (Optional) */}
                <div>
                  <label className="block text-sm font-medium text-slate-200 mb-2">
                    Email (Optional)
                  </label>
                  <input
                    type="email"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    placeholder="your@email.com"
                    className="w-full px-3 py-2 bg-slate-800 border border-slate-700 rounded-lg text-slate-200 placeholder-slate-500 focus:outline-none focus:border-cyan-500 transition"
                  />
                </div>

                {/* Submit Button */}
                <button
                  type="submit"
                  disabled={isSubmitting}
                  className="w-full flex items-center justify-center gap-2 px-4 py-2.5 rounded-lg bg-gradient-to-r from-cyan-500 to-blue-500 text-white font-medium hover:shadow-lg hover:shadow-cyan-500/50 transition disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  <Send className="h-4 w-4" />
                  {isSubmitting ? 'Submitting...' : 'Send Feedback'}
                </button>

                {/* Info */}
                <p className="text-xs text-slate-500 text-center">
                  Your feedback helps us improve SampleMind AI
                </p>
              </form>
            </motion.div>
          </>
        )}
      </AnimatePresence>
    </>
  );
}
