import { useState } from 'react';
import Layout from '../../components/layout/Layout';
import { getSiteSettings, getPortfolio } from '../../lib/api';
import Link from 'next/link';
import { FiExternalLink, FiGithub } from 'react-icons/fi';
import { motion } from 'framer-motion';

export async function getServerSideProps() {
  try {
    const [settingsRes, portfolioRes] = await Promise.all([getSiteSettings(), getPortfolio()]);
    return { props: { settings: settingsRes.data, items: portfolioRes.data.results || portfolioRes.data || [] } };
  } catch { return { props: { settings: null, items: [] } }; }
}

export default function PortfolioPage({ settings, items }) {
  const [selected, setSelected] = useState(null);

  return (
    <Layout settings={settings} title="Portfolio" description="Découvrez mes réalisations et travaux.">
      <div className="bg-gradient-to-br from-orange-500 to-amber-600 text-white py-20">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }}>
            <h1 className="text-4xl md:text-5xl font-black mb-4">Portfolio</h1>
            <p className="text-orange-100 text-xl max-w-2xl">Mes réalisations, designs et travaux créatifs.</p>
          </motion.div>
        </div>
      </div>
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        {items.length > 0 ? (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
            {items.map((item, i) => (
              <motion.div key={item.id} initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }}
                transition={{ delay: i * 0.05 }} className="card-hover group overflow-hidden">
                <Link href={`/portfolio/${item.slug}`} className="block overflow-hidden aspect-video">
                  {item.cover_image_url ? (
                    <img src={item.cover_image_url} alt={item.title} className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-500" />
                  ) : (
                    <div className="w-full h-full bg-gradient-to-br from-orange-100 to-amber-100 dark:from-orange-950/30 dark:to-amber-950/30 flex items-center justify-center">
                      <span className="text-4xl opacity-30">🎨</span>
                    </div>
                  )}
                </Link>
                <div className="p-5">
                  <h3 className="font-bold text-gray-900 dark:text-white text-lg mb-2 group-hover:text-orange-600 transition-colors">
                    <Link href={`/portfolio/${item.slug}`}>{item.title}</Link>
                  </h3>
                  {item.subtitle && <p className="text-sm text-gray-500 mb-2">{item.subtitle}</p>}
                  <p className="text-gray-600 dark:text-gray-400 text-sm mb-4 line-clamp-2">{item.description}</p>
                  <div className="flex items-center gap-3">
                    {item.url && <a href={item.url} target="_blank" rel="noopener noreferrer" className="flex items-center gap-1 text-sm text-orange-600 hover:text-orange-700"><FiExternalLink size={14} />Voir</a>}
                    {item.github_url && <a href={item.github_url} target="_blank" rel="noopener noreferrer" className="flex items-center gap-1 text-sm text-gray-500 hover:text-gray-700"><FiGithub size={14} />Code</a>}
                  </div>
                </div>
              </motion.div>
            ))}
          </div>
        ) : (
          <div className="text-center py-20"><p className="text-gray-400 text-lg">Aucune réalisation pour le moment.</p></div>
        )}
      </div>
    </Layout>
  );
}
