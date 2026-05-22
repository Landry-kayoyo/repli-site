import Link from 'next/link';
import { motion } from 'framer-motion';
import { FiCalendar, FiEye, FiClock, FiTag } from 'react-icons/fi';
import { formatDateShort, truncate } from '../../lib/utils';

export default function ContentCard({ item, type = 'article', index = 0 }) {
  const paths = { article: '/articles', project: '/projets', tip: '/astuces', portfolio: '/portfolio' };
  const href = `${paths[type]}/${item.slug}`;

  return (
    <motion.article initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4, delay: index * 0.05 }}
      className="card-hover group flex flex-col overflow-hidden">
      {/* Cover Image */}
      {item.cover_image_url && (
        <Link href={href} className="block overflow-hidden aspect-[16/9]">
          <img src={item.cover_image_url} alt={item.title}
            className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-500" />
        </Link>
      )}
      {!item.cover_image_url && (
        <Link href={href} className="block bg-gradient-to-br from-primary-100 to-purple-100 dark:from-primary-950/50 dark:to-purple-950/50 aspect-[16/9] flex items-center justify-center">
          <span className="text-4xl opacity-30">📄</span>
        </Link>
      )}

      <div className="p-5 flex flex-col flex-1">
        {/* Category & Tags */}
        <div className="flex items-center gap-2 mb-3 flex-wrap">
          {item.category_name && (
            <span className="badge text-white text-xs" style={{ backgroundColor: item.category_color || '#4F46E5' }}>
              {item.category_name}
            </span>
          )}
          {item.difficulty && (
            <span className={`badge text-xs ${item.difficulty === 'beginner' ? 'bg-green-100 text-green-700' : item.difficulty === 'intermediate' ? 'bg-yellow-100 text-yellow-700' : 'bg-red-100 text-red-700'}`}>
              {item.difficulty === 'beginner' ? 'Débutant' : item.difficulty === 'intermediate' ? 'Intermédiaire' : 'Avancé'}
            </span>
          )}
          {item.is_featured && (
            <span className="badge bg-amber-100 text-amber-700 text-xs">⭐ À la une</span>
          )}
        </div>

        {/* Title */}
        <Link href={href}>
          <h3 className="font-bold text-gray-900 dark:text-white text-lg leading-tight mb-1 group-hover:text-primary-600 dark:group-hover:text-primary-400 transition-colors line-clamp-2">
            {item.title}
          </h3>
        </Link>

        {/* Subtitle */}
        {item.subtitle && (
          <p className="text-sm text-gray-500 dark:text-gray-400 mb-2">{truncate(item.subtitle, 80)}</p>
        )}

        {/* Excerpt */}
        <p className="text-gray-600 dark:text-gray-400 text-sm mb-4 flex-1 line-clamp-3">
          {item.excerpt || item.description || ''}
        </p>

        {/* Tags */}
        {item.tags && item.tags.length > 0 && (
          <div className="flex flex-wrap gap-1.5 mb-4">
            {item.tags.slice(0, 3).map(tag => (
              <span key={tag} className="flex items-center gap-1 text-xs text-gray-500 dark:text-gray-400 bg-gray-100 dark:bg-gray-800 px-2 py-0.5 rounded-full">
                <FiTag size={10} />{tag}
              </span>
            ))}
          </div>
        )}

        {/* Meta */}
        <div className="flex items-center gap-4 text-xs text-gray-400 pt-4 border-t border-gray-100 dark:border-gray-800">
          {item.published_at && (
            <span className="flex items-center gap-1"><FiCalendar size={12} />{formatDateShort(item.published_at)}</span>
          )}
          {item.views_count !== undefined && (
            <span className="flex items-center gap-1"><FiEye size={12} />{item.views_count}</span>
          )}
          {item.read_time && (
            <span className="flex items-center gap-1"><FiClock size={12} />{item.read_time} min</span>
          )}
        </div>
      </div>
    </motion.article>
  );
}
