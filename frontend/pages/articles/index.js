import { useState } from 'react';
import Layout from '../../components/layout/Layout';
import ContentCard from '../../components/ui/ContentCard';
import { getSiteSettings, getArticles, getArticleCategories } from '../../lib/api';
import { FiSearch, FiFilter } from 'react-icons/fi';
import { motion } from 'framer-motion';

export async function getServerSideProps() {
  try {
    const [settingsRes, articlesRes, categoriesRes] = await Promise.all([
      getSiteSettings(), getArticles({ page: 1 }), getArticleCategories()
    ]);
    return {
      props: {
        settings: settingsRes.data,
        initialArticles: articlesRes.data,
        categories: categoriesRes.data.results || categoriesRes.data || [],
      }
    };
  } catch {
    return { props: { settings: null, initialArticles: { results: [], count: 0 }, categories: [] } };
  }
}

export default function ArticlesPage({ settings, initialArticles, categories }) {
  const [articles, setArticles] = useState(initialArticles?.results || []);
  const [selectedCategory, setSelectedCategory] = useState('');
  const [searchTerm, setSearchTerm] = useState('');
  const [loading, setLoading] = useState(false);
  const [page, setPage] = useState(1);
  const [total, setTotal] = useState(initialArticles?.count || 0);

  const fetchArticles = async (params = {}) => {
    setLoading(true);
    try {
      const res = await getArticles(params);
      setArticles(res.data.results || []);
      setTotal(res.data.count || 0);
    } catch {} finally { setLoading(false); }
  };

  const handleCategory = (slug) => {
    setSelectedCategory(slug);
    setPage(1);
    fetchArticles({ category__slug: slug || undefined, search: searchTerm || undefined });
  };

  const handleSearch = (e) => {
    const v = e.target.value;
    setSearchTerm(v);
    if (v.length === 0 || v.length >= 2) {
      fetchArticles({ category__slug: selectedCategory || undefined, search: v || undefined });
    }
  };

  return (
    <Layout settings={settings} title="Articles" description="Découvrez tous mes articles sur la technologie, le développement et plus encore.">
      {/* Hero */}
      <div className="bg-gradient-to-br from-primary-600 to-purple-700 text-white py-20">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }}>
            <h1 className="text-4xl md:text-5xl font-black mb-4">Articles & Blog</h1>
            <p className="text-primary-100 text-xl max-w-2xl">Explorez mes articles sur la technologie, le développement, et le partage de connaissances.</p>
          </motion.div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        {/* Filters */}
        <div className="flex flex-col md:flex-row gap-4 mb-10">
          <div className="relative flex-1 max-w-md">
            <FiSearch className="absolute left-4 top-1/2 -translate-y-1/2 text-gray-400" size={18} />
            <input type="text" value={searchTerm} onChange={handleSearch}
              placeholder="Rechercher un article..." className="input-field pl-12" />
          </div>
          <div className="flex gap-2 flex-wrap">
            <button onClick={() => handleCategory('')}
              className={`px-4 py-2 rounded-xl text-sm font-medium transition-all ${!selectedCategory ? 'bg-primary-600 text-white shadow-lg' : 'bg-gray-100 dark:bg-gray-800 text-gray-600 dark:text-gray-400 hover:bg-gray-200'}`}>
              Tous
            </button>
            {categories.map(cat => (
              <button key={cat.slug} onClick={() => handleCategory(cat.slug)}
                className={`px-4 py-2 rounded-xl text-sm font-medium transition-all ${selectedCategory === cat.slug ? 'text-white shadow-lg' : 'bg-gray-100 dark:bg-gray-800 text-gray-600 dark:text-gray-400 hover:bg-gray-200'}`}
                style={selectedCategory === cat.slug ? { backgroundColor: cat.color } : {}}>
                {cat.name}
              </button>
            ))}
          </div>
        </div>

        {/* Count */}
        <p className="text-gray-500 mb-6">{total} article{total !== 1 ? 's' : ''} trouvé{total !== 1 ? 's' : ''}</p>

        {/* Grid */}
        {loading ? (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
            {[...Array(6)].map((_, i) => <div key={i} className="card h-80 animate-pulse bg-gray-100 dark:bg-gray-800" />)}
          </div>
        ) : articles.length > 0 ? (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
            {articles.map((a, i) => <ContentCard key={a.id} item={a} type="article" index={i} />)}
          </div>
        ) : (
          <div className="text-center py-20">
            <p className="text-gray-400 text-lg">Aucun article pour le moment.</p>
          </div>
        )}
      </div>
    </Layout>
  );
}
