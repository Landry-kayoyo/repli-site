import { useState } from 'react';
import Layout from '../../components/layout/Layout';
import ContentCard from '../../components/ui/ContentCard';
import { getSiteSettings, getTips } from '../../lib/api';
import { FiSearch } from 'react-icons/fi';
import { motion } from 'framer-motion';

export async function getServerSideProps() {
  try {
    const [settingsRes, tipsRes] = await Promise.all([getSiteSettings(), getTips({ page: 1 })]);
    return { props: { settings: settingsRes.data, initialTips: tipsRes.data } };
  } catch { return { props: { settings: null, initialTips: { results: [], count: 0 } } }; }
}

export default function TipsPage({ settings, initialTips }) {
  const [tips, setTips] = useState(initialTips?.results || []);
  const [searchTerm, setSearchTerm] = useState('');
  const [difficulty, setDifficulty] = useState('');
  const [loading, setLoading] = useState(false);

  const fetchTips = async (params = {}) => {
    setLoading(true);
    try { const res = await getTips(params); setTips(res.data.results || []); } catch {} finally { setLoading(false); }
  };

  return (
    <Layout settings={settings} title="Astuces & Conseils" description="Découvrez mes astuces pratiques.">
      <div className="bg-gradient-to-br from-green-600 to-emerald-700 text-white py-20">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }}>
            <h1 className="text-4xl md:text-5xl font-black mb-4">Astuces & Conseils</h1>
            <p className="text-green-100 text-xl max-w-2xl">Des astuces pratiques et conseils utiles pour améliorer vos compétences.</p>
          </motion.div>
        </div>
      </div>
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <div className="flex flex-col md:flex-row gap-4 mb-10">
          <div className="relative flex-1 max-w-md">
            <FiSearch className="absolute left-4 top-1/2 -translate-y-1/2 text-gray-400" size={18} />
            <input type="text" value={searchTerm} onChange={e => { setSearchTerm(e.target.value); if (e.target.value.length === 0 || e.target.value.length >= 2) fetchTips({ search: e.target.value || undefined, difficulty: difficulty || undefined }); }} placeholder="Rechercher une astuce..." className="input-field pl-12" />
          </div>
          <div className="flex gap-2">
            {[['', 'Tous niveaux'], ['beginner', 'Débutant'], ['intermediate', 'Intermédiaire'], ['advanced', 'Avancé']].map(([val, label]) => (
              <button key={val} onClick={() => { setDifficulty(val); fetchTips({ difficulty: val || undefined, search: searchTerm || undefined }); }}
                className={`px-4 py-2 rounded-xl text-sm font-medium transition-all ${difficulty === val ? 'bg-green-600 text-white' : 'bg-gray-100 dark:bg-gray-800 text-gray-600 dark:text-gray-400'}`}>{label}</button>
            ))}
          </div>
        </div>
        {loading ? <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">{[...Array(6)].map((_, i) => <div key={i} className="card h-72 animate-pulse bg-gray-100 dark:bg-gray-800" />)}</div>
          : tips.length > 0
          ? <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">{tips.map((t, i) => <ContentCard key={t.id} item={t} type="tip" index={i} />)}</div>
          : <div className="text-center py-20"><p className="text-gray-400 text-lg">Aucune astuce pour le moment.</p></div>}
      </div>
    </Layout>
  );
}
