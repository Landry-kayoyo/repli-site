import Layout from '../../components/layout/Layout';
import Comments from '../../components/ui/Comments';
import Reactions from '../../components/ui/Reactions';
import { getSiteSettings, getArticle, getArticles } from '../../lib/api';
import { formatDate } from '../../lib/utils';
import { FiCalendar, FiEye, FiClock, FiTag, FiShare2, FiArrowLeft } from 'react-icons/fi';
import Link from 'next/link';
import { motion } from 'framer-motion';

export async function getServerSideProps({ params }) {
  try {
    const [settingsRes, articleRes] = await Promise.all([getSiteSettings(), getArticle(params.slug)]);
    return { props: { settings: settingsRes.data, article: articleRes.data } };
  } catch {
    return { notFound: true };
  }
}

export default function ArticleDetailPage({ settings, article }) {
  const handleShare = () => {
    if (navigator.share) {
      navigator.share({ title: article.title, url: window.location.href });
    } else {
      navigator.clipboard.writeText(window.location.href);
      alert('Lien copié !');
    }
  };

  return (
    <Layout settings={settings} title={article.meta_title || article.title} description={article.meta_description || article.excerpt} image={article.cover_image_url}>
      {/* Cover */}
      {article.cover_image_url && (
        <div className="w-full aspect-[21/9] max-h-[500px] overflow-hidden">
          <img src={article.cover_image_url} alt={article.title} className="w-full h-full object-cover" />
        </div>
      )}

      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        {/* Back */}
        <Link href="/articles" className="flex items-center gap-2 text-gray-500 hover:text-primary-600 mb-8 transition-colors">
          <FiArrowLeft size={16} /> Retour aux articles
        </Link>

        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }}>
          {/* Category */}
          {article.category_name && (
            <span className="badge text-white mb-4 inline-block" style={{ backgroundColor: article.category_color || '#4F46E5' }}>
              {article.category_name}
            </span>
          )}

          {/* Title */}
          <h1 className="text-3xl md:text-5xl font-black text-gray-900 dark:text-white mb-3 leading-tight">{article.title}</h1>
          {article.subtitle && <p className="text-xl text-gray-600 dark:text-gray-400 mb-6">{article.subtitle}</p>}

          {/* Meta */}
          <div className="flex flex-wrap items-center gap-4 text-sm text-gray-500 dark:text-gray-400 mb-6 pb-6 border-b border-gray-100 dark:border-gray-800">
            {article.author_name && <span className="font-semibold text-gray-700 dark:text-gray-300">{article.author_name}</span>}
            {article.published_at && <span className="flex items-center gap-1"><FiCalendar size={14} />{formatDate(article.published_at)}</span>}
            {article.read_time && <span className="flex items-center gap-1"><FiClock size={14} />{article.read_time} min de lecture</span>}
            {article.views_count !== undefined && <span className="flex items-center gap-1"><FiEye size={14} />{article.views_count} vues</span>}
            <button onClick={handleShare} className="flex items-center gap-1 ml-auto text-primary-600 hover:text-primary-700 font-medium">
              <FiShare2 size={14} /> Partager
            </button>
          </div>

          {/* Excerpt */}
          {article.excerpt && (
            <p className="text-lg text-gray-600 dark:text-gray-400 italic border-l-4 border-primary-400 pl-4 mb-8">{article.excerpt}</p>
          )}

          {/* Content */}
          <div className="prose-custom" dangerouslySetInnerHTML={{ __html: article.content }} />

          {/* Tags */}
          {article.tags && article.tags.length > 0 && (
            <div className="flex flex-wrap gap-2 mt-8 pt-8 border-t border-gray-100 dark:border-gray-800">
              <FiTag className="text-gray-400 mt-0.5" />
              {article.tags.map(tag => (
                <Link key={tag} href={`/articles?tag=${tag}`}
                  className="px-3 py-1 bg-gray-100 dark:bg-gray-800 text-gray-600 dark:text-gray-400 rounded-full text-sm hover:bg-primary-50 dark:hover:bg-primary-950/30 hover:text-primary-600 transition-colors">
                  {tag}
                </Link>
              ))}
            </div>
          )}

          {/* Reactions */}
          <div className="mt-8 pt-8 border-t border-gray-100 dark:border-gray-800">
            <h4 className="font-semibold text-gray-700 dark:text-gray-300 mb-3">Votre réaction :</h4>
            <Reactions contentType="articles.article" objectId={article.id} />
          </div>

          {/* Schema.org Article */}
          <script type="application/ld+json" dangerouslySetInnerHTML={{ __html: JSON.stringify({
            '@context': 'https://schema.org', '@type': 'Article',
            headline: article.title, description: article.excerpt,
            image: article.cover_image_url,
            datePublished: article.published_at, dateModified: article.updated_at,
            author: { '@type': 'Person', name: article.author_name },
          })}} />

          {/* Comments */}
          <Comments contentType="articles.article" objectId={article.id} />
        </motion.div>
      </div>
    </Layout>
  );
}
