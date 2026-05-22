import Layout from '../../components/layout/Layout';
import Comments from '../../components/ui/Comments';
import Reactions from '../../components/ui/Reactions';
import { getSiteSettings, getTip } from '../../lib/api';
import { formatDate, difficultyLabel, difficultyColor } from '../../lib/utils';
import { FiCalendar, FiEye, FiArrowLeft, FiTag } from 'react-icons/fi';
import Link from 'next/link';
import { motion } from 'framer-motion';

export async function getServerSideProps({ params }) {
  try {
    const [settingsRes, tipRes] = await Promise.all([getSiteSettings(), getTip(params.slug)]);
    return { props: { settings: settingsRes.data, tip: tipRes.data } };
  } catch { return { notFound: true }; }
}

export default function TipDetailPage({ settings, tip }) {
  return (
    <Layout settings={settings} title={tip.meta_title || tip.title} description={tip.meta_description || tip.excerpt} image={tip.cover_image_url}>
      {tip.cover_image_url && (
        <div className="w-full aspect-[21/9] max-h-[500px] overflow-hidden">
          <img src={tip.cover_image_url} alt={tip.title} className="w-full h-full object-cover" />
        </div>
      )}
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <Link href="/astuces" className="flex items-center gap-2 text-gray-500 hover:text-primary-600 mb-8 transition-colors">
          <FiArrowLeft size={16} /> Retour aux astuces
        </Link>
        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }}>
          <div className="flex gap-2 mb-4">
            {tip.category_name && <span className="badge bg-green-100 text-green-700">{tip.category_name}</span>}
            <span className={`badge ${difficultyColor(tip.difficulty)}`}>{difficultyLabel(tip.difficulty)}</span>
          </div>
          <h1 className="text-3xl md:text-5xl font-black text-gray-900 dark:text-white mb-3">{tip.title}</h1>
          {tip.subtitle && <p className="text-xl text-gray-600 dark:text-gray-400 mb-6">{tip.subtitle}</p>}
          <div className="flex flex-wrap items-center gap-4 text-sm text-gray-500 mb-6 pb-6 border-b border-gray-100 dark:border-gray-800">
            {tip.published_at && <span className="flex items-center gap-1"><FiCalendar size={14} />{formatDate(tip.published_at)}</span>}
            {tip.views_count !== undefined && <span className="flex items-center gap-1"><FiEye size={14} />{tip.views_count} vues</span>}
          </div>
          {tip.excerpt && <p className="text-lg text-gray-600 dark:text-gray-400 italic border-l-4 border-green-400 pl-4 mb-8">{tip.excerpt}</p>}
          <div className="prose-custom" dangerouslySetInnerHTML={{ __html: tip.content }} />
          {tip.tags && tip.tags.length > 0 && (
            <div className="flex flex-wrap gap-2 mt-8 pt-8 border-t border-gray-100 dark:border-gray-800">
              <FiTag className="text-gray-400 mt-0.5" />
              {tip.tags.map(tag => <Link key={tag} href={`/astuces?tag=${tag}`} className="px-3 py-1 bg-gray-100 dark:bg-gray-800 text-gray-600 rounded-full text-sm hover:text-primary-600 transition-colors">{tag}</Link>)}
            </div>
          )}
          <div className="mt-8 pt-8 border-t border-gray-100 dark:border-gray-800">
            <h4 className="font-semibold text-gray-700 dark:text-gray-300 mb-3">Votre réaction :</h4>
            <Reactions contentType="tips.tip" objectId={tip.id} />
          </div>
          <Comments contentType="tips.tip" objectId={tip.id} />
        </motion.div>
      </div>
    </Layout>
  );
}
