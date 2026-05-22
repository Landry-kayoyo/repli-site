import Layout from '../../components/layout/Layout';
import Comments from '../../components/ui/Comments';
import Reactions from '../../components/ui/Reactions';
import { getSiteSettings, getPortfolioItem } from '../../lib/api';
import { FiExternalLink, FiGithub, FiArrowLeft } from 'react-icons/fi';
import Link from 'next/link';
import { motion } from 'framer-motion';

export async function getServerSideProps({ params }) {
  try {
    const [settingsRes, itemRes] = await Promise.all([getSiteSettings(), getPortfolioItem(params.slug)]);
    return { props: { settings: settingsRes.data, item: itemRes.data } };
  } catch { return { notFound: true }; }
}

export default function PortfolioDetailPage({ settings, item }) {
  return (
    <Layout settings={settings} title={item.meta_title || item.title} description={item.meta_description || item.description} image={item.cover_image_url}>
      {item.cover_image_url && (
        <div className="w-full aspect-[21/9] max-h-[500px] overflow-hidden">
          <img src={item.cover_image_url} alt={item.title} className="w-full h-full object-cover" />
        </div>
      )}
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <Link href="/portfolio" className="flex items-center gap-2 text-gray-500 hover:text-primary-600 mb-8 transition-colors"><FiArrowLeft size={16} /> Retour au portfolio</Link>
        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }}>
          {item.category_name && <span className="badge bg-orange-100 text-orange-700 mb-4 inline-block">{item.category_name}</span>}
          <h1 className="text-3xl md:text-5xl font-black text-gray-900 dark:text-white mb-3">{item.title}</h1>
          {item.subtitle && <p className="text-xl text-gray-600 dark:text-gray-400 mb-6">{item.subtitle}</p>}
          <div className="flex flex-wrap gap-4 mb-8">
            {item.url && <a href={item.url} target="_blank" rel="noopener noreferrer" className="btn-primary"><FiExternalLink />Voir le projet</a>}
            {item.github_url && <a href={item.github_url} target="_blank" rel="noopener noreferrer" className="btn-secondary"><FiGithub />Code source</a>}
          </div>
          {item.client && <div className="mb-6 p-4 bg-gray-50 dark:bg-gray-900/50 rounded-xl"><span className="text-sm text-gray-500">Client :</span><span className="ml-2 font-semibold">{item.client}</span></div>}
          <p className="text-lg text-gray-600 dark:text-gray-400 mb-8">{item.description}</p>
          {item.content && <div className="prose-custom" dangerouslySetInnerHTML={{ __html: item.content }} />}
          {item.images_detail && item.images_detail.length > 0 && (
            <div className="mt-10 grid grid-cols-2 gap-4">
              {item.images_detail.map(img => (
                <div key={img.id} className="overflow-hidden rounded-xl aspect-video">
                  <img src={img.image_url} alt={img.caption} className="w-full h-full object-cover" />
                </div>
              ))}
            </div>
          )}
          <div className="mt-8 pt-8 border-t border-gray-100 dark:border-gray-800">
            <h4 className="font-semibold text-gray-700 dark:text-gray-300 mb-3">Votre réaction :</h4>
            <Reactions contentType="portfolio.portfolioitem" objectId={item.id} />
          </div>
          <Comments contentType="portfolio.portfolioitem" objectId={item.id} />
        </motion.div>
      </div>
    </Layout>
  );
}
