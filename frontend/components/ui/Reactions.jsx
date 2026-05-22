import { useState, useEffect } from 'react';
import { getReactions, toggleReaction } from '../../lib/api';
import { motion, AnimatePresence } from 'framer-motion';

const REACTIONS = [
  { type: 'like', emoji: '👍', label: "J'aime" },
  { type: 'love', emoji: '❤️', label: "J'adore" },
  { type: 'wow', emoji: '😮', label: 'Wow' },
  { type: 'clap', emoji: '👏', label: 'Bravo' },
  { type: 'fire', emoji: '🔥', label: 'Incroyable' },
  { type: 'bookmark', emoji: '🔖', label: 'Sauvegarder' },
];

export default function Reactions({ contentType, objectId }) {
  const [reactions, setReactions] = useState({});
  const [loading, setLoading] = useState({});

  useEffect(() => {
    if (contentType && objectId) {
      getReactions(contentType, objectId).then(r => setReactions(r.data)).catch(() => {});
    }
  }, [contentType, objectId]);

  const handleReact = async (reactionType) => {
    setLoading(p => ({ ...p, [reactionType]: true }));
    try {
      const res = await toggleReaction({ content_type: contentType, object_id: objectId, reaction_type: reactionType });
      const { action } = res.data;
      setReactions(prev => {
        const curr = prev[reactionType] || { count: 0, reacted: false };
        return {
          ...prev,
          [reactionType]: {
            count: action === 'added' ? curr.count + 1 : Math.max(0, curr.count - 1),
            reacted: action === 'added',
          }
        };
      });
    } catch {} finally { setLoading(p => ({ ...p, [reactionType]: false })); }
  };

  return (
    <div className="flex flex-wrap gap-2 py-4">
      {REACTIONS.map(({ type, emoji, label }) => {
        const data = reactions[type] || { count: 0, reacted: false };
        return (
          <motion.button key={type} whileTap={{ scale: 0.85 }} onClick={() => handleReact(type)} disabled={loading[type]}
            className={`flex items-center gap-1.5 px-3 py-2 rounded-xl border transition-all text-sm font-medium ${
              data.reacted
                ? 'bg-primary-50 dark:bg-primary-950/30 border-primary-200 dark:border-primary-800 text-primary-700 dark:text-primary-300'
                : 'bg-gray-50 dark:bg-gray-800 border-gray-200 dark:border-gray-700 text-gray-600 dark:text-gray-400 hover:border-primary-200 dark:hover:border-primary-700'
            }`}>
            <span>{emoji}</span>
            {data.count > 0 && <span>{data.count}</span>}
            <span className="hidden sm:inline text-xs">{label}</span>
          </motion.button>
        );
      })}
    </div>
  );
}
