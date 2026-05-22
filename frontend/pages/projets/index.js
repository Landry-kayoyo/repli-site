import { useState } from 'react';
import Layout from '../../components/layout/Layout';
import ContentCard from '../../components/ui/ContentCard';
import { getSiteSettings, getProjects, getProjectCategories } from '../../lib/api';
import { FiSearch } from 'react-icons/fi';
import { motion } from 'framer-motion';

export async function getServerSideProps() {
  try {
    const [settingsRes, projectsRes, categoriesRes] = await Promise.all([
      getSiteSettings(), getProjects({ page: 1 }), getProjectCategories()
    ]);
    return { props: { settings: settingsRes.data, initialProjects: projectsRes.data, categories: categoriesRes.data.results || categoriesRes.data || [] } };
  } catch { return { props: { settings: null, initialProjects: { results: [], count: 0 }, categories: [] } }; }
}

export default function ProjectsPage({ settings, initialProjects, categories }) {
  const [projects, setProjects] = useState(initialProjects?.results || []);
  const [selectedCategory, setSelectedCategory] = useState('');
  const [searchTerm, setSearchTerm] = useState('');
  const [loading, setLoading] = useState(false);
  const [total, setTotal] = useState(initialProjects?.count || 0);

  const fetchProjects = async (params = {}) => {
    setLoading(true);
    try {
      const res = await getProjects(params);
      setProjects(res.data.results || []);
      setTotal(res.data.count || 0);
    } catch {} finally { setLoading(false); }
  };

  return (
    <Layout settings={settings} title="Projets & Tutoriels" description="Découvrez mes projets avec tutoriels détaillés.">
      <div className="bg-gradient-to-br from-purple-600 to-pink-700 text-white py-20">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }}>
            <h1 className="text-4xl md:text-5xl font-black mb-4">Projets & Tutoriels</h1>
            <p className="text-purple-100 text-xl max-w-2xl">Des projets réels avec des tutoriels pas à pas pour apprendre en faisant.</p>
          </motion.div>
        </div>
      </div>
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <div className="flex flex-col md:flex-row gap-4 mb-10">
          <div className="relative flex-1 max-w-md">
            <FiSearch className="absolute left-4 top-1/2 -translate-y-1/2 text-gray-400" size={18} />
            <input type="text" value={searchTerm} onChange={e => { setSearchTerm(e.target.value); if (e.target.value.length === 0 || e.target.value.length >= 2) fetchProjects({ search: e.target.value || undefined, category__slug: selectedCategory || undefined }); }}
              placeholder="Rechercher un projet..." className="input-field pl-12" />
          </div>
          <div className="flex gap-2 flex-wrap">
            <button onClick={() => { setSelectedCategory(''); fetchProjects({ search: searchTerm || undefined }); }}
              className={`px-4 py-2 rounded-xl text-sm font-medium transition-all ${!selectedCategory ? 'bg-purple-600 text-white' : 'bg-gray-100 dark:bg-gray-800 text-gray-600 dark:text-gray-400'}`}>Tous</button>
            {categories.map(cat => (
              <button key={cat.slug} onClick={() => { setSelectedCategory(cat.slug); fetchProjects({ category__slug: cat.slug, search: searchTerm || undefined }); }}
                className={`px-4 py-2 rounded-xl text-sm font-medium transition-all ${selectedCategory === cat.slug ? 'bg-purple-600 text-white' : 'bg-gray-100 dark:bg-gray-800 text-gray-600 dark:text-gray-400'}`}>{cat.name}</button>
            ))}
          </div>
        </div>
        {loading ? <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">{[...Array(6)].map((_, i) => <div key={i} className="card h-80 animate-pulse bg-gray-100 dark:bg-gray-800" />)}</div>
          : projects.length > 0
          ? <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">{projects.map((p, i) => <ContentCard key={p.id} item={p} type="project" index={i} />)}</div>
          : <div className="text-center py-20"><p className="text-gray-400 text-lg">Aucun projet pour le moment.</p></div>}
      </div>
    </Layout>
  );
}
