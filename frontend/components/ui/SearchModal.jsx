import { useState, useEffect, useRef } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { FiSearch, FiX, FiFile, FiBox, FiZap } from 'react-icons/fi';
import { search } from '../../lib/api';
import Link from 'next/link';

const typeIcons = { article: FiFile, project: FiBox, tip: FiZap };
const typeLabels = { article: 'Article', project: 'Projet', tip: 'Astuce' };
const typePaths = { article: '/articles', project: '/projets', tip: '/astuces' };

export default function SearchModal({ isOpen, onClose }) {
  const [query, setQuery] = useState('');
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(false);
  const inputRef = useRef(null);

  useEffect(() => {
    if (isOpen) { setQuery(''); setResults([]); setTimeout(() => inputRef.current?.focus(), 100); }
  }, [isOpen]);

  useEffect(() => {
    if (query.length < 2) { setResults([]); return; }
    const timer = setTimeout(async () => {
      setLoading(true);
      try {
        const res = await search(query);
        setResults(res.data.results || []);
      } catch {} finally { setLoading(false); }
    }, 300);
    return () => clearTimeout(timer);
  }, [query]);

  useEffect(() => {
    const handleKey = (e) => { if (e.key === 'Escape') onClose(); };
    window.addEventListener('keydown', handleKey);
    return () => window.removeEventListener('keydown', handleKey);
  }, [onClose]);

  return (
    <AnimatePresence>
      {isOpen && (
        <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}
          className="fixed inset-0 z-[100] bg-black/50 backdrop-blur-sm flex items-start justify-center pt-20 px-4"
          onClick={(e) => e.target === e.currentTarget && onClose()}>
          <motion.div initial={{ scale: 0.95, y: -20 }} animate={{ scale: 1, y: 0 }} exit={{ scale: 0.95, y: -20 }}
            className="w-full max-w-2xl bg-white dark:bg-gray-900 rounded-2xl shadow-2xl overflow-hidden">
            <div className="flex items-center gap-3 p-4 border-b border-gray-100 dark:border-gray-800">
              <FiSearch className="text-gray-400" size={20} />
              <input ref={inputRef} type="text" value={query} onChange={e => setQuery(e.target.value)}
                placeholder="Rechercher articles, projets, astuces..."
                className="flex-1 bg-transparent text-gray-900 dark:text-white placeholder-gray-400 outline-none text-lg" />
              {query && <button onClick={() => setQuery('')} className="text-gray-400 hover:text-gray-600"><FiX size={18} /></button>}
              <button onClick={onClose} className="p-1.5 rounded-lg text-gray-400 hover:bg-gray-100 dark:hover:bg-gray-800"><FiX size={20} /></button>
            </div>
            <div className="max-h-96 overflow-y-auto">
              {loading && <div className="p-8 text-center text-gray-400">Recherche...</div>}
              {!loading && results.length === 0 && query.length >= 2 && (
                <div className="p-8 text-center text-gray-400">Aucun résultat pour "{query}"</div>
              )}
              {!loading && results.length === 0 && query.length < 2 && (
                <div className="p-8 text-center text-gray-400">Tapez au moins 2 caractères pour rechercher</div>
              )}
              {results.map((r, i) => {
                const Icon = typeIcons[r.type] || FiFile;
                return (
                  <Link key={i} href={`${typePaths[r.type]}/${r.slug}`} onClick={onClose}
                    className="flex items-start gap-4 p-4 hover:bg-gray-50 dark:hover:bg-gray-800 transition-colors border-b border-gray-50 dark:border-gray-800/50 last:border-0">
                    <div className="p-2 rounded-lg bg-primary-50 dark:bg-primary-950/30 text-primary-600 mt-0.5">
                      <Icon size={16} />
                    </div>
                    <div>
                      <div className="flex items-center gap-2">
                        <span className="font-medium text-gray-900 dark:text-white">{r.title}</span>
                        <span className="badge bg-gray-100 dark:bg-gray-800 text-gray-500 text-xs">{typeLabels[r.type]}</span>
                      </div>
                      {r.excerpt && <p className="text-sm text-gray-500 dark:text-gray-400 mt-0.5">{r.excerpt}</p>}
                    </div>
                  </Link>
                );
              })}
            </div>
          </motion.div>
        </motion.div>
      )}
    </AnimatePresence>
  );
}
