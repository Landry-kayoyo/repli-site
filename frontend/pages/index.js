import Layout from '../components/layout/Layout';
import HeroSection from '../components/sections/HeroSection';
import StatsSection from '../components/sections/StatsSection';
import ContentCard from '../components/ui/ContentCard';
import Newsletter from '../components/ui/Newsletter';
import Link from 'next/link';
import { FiArrowRight } from 'react-icons/fi';
import { motion } from 'framer-motion';
import { getSiteSettings, getStats, getFeaturedArticles, getProjects, getTips, getPortfolio } from '../lib/api';

export async function getServerSideProps() {
  try {
    const [settingsRes, statsRes, articlesRes, projectsRes, tipsRes, portfolioRes] = await Promise.all([
      getSiteSettings(), getStats(), getFeaturedArticles(),
      getProjects({ page_size: 3, is_featured: true }),
      getTips({ page_size: 3, is_featured: true }),
      getPortfolio({ page_size: 3, is_featured: true }),
    ]);
    return {
      props: {
        settings: settingsRes.data,
        stats: statsRes.data,
        featuredArticles: articlesRes.data.results || articlesRes.data || [],
        featuredProjects: projectsRes.data.results || projectsRes.data || [],
        featuredTips: tipsRes.data.results || tipsRes.data || [],
        featuredPortfolio: portfolioRes.data.results || portfolioRes.data || [],
      }
    };
  } catch {
    return { props: { settings: null, stats: null, featuredArticles: [], featuredProjects: [], featuredTips: [], featuredPortfolio: [] } };
  }
}

function SectionHeader({ title, subtitle, href, linkLabel }) {
  return (
    <div className="flex items-end justify-between mb-10">
      <div>
        <h2 className="section-title">{title}</h2>
        {subtitle && <p className="text-gray-500 dark:text-gray-400 mt-2">{subtitle}</p>}
      </div>
      {href && (
        <Link href={href} className="flex items-center gap-2 text-primary-600 dark:text-primary-400 font-semibold hover:gap-3 transition-all">
          {linkLabel} <FiArrowRight />
        </Link>
      )}
    </div>
  );
}

export default function Home({ settings, stats, featuredArticles, featuredProjects, featuredTips, featuredPortfolio }) {
  return (
    <Layout settings={settings}>
      <HeroSection settings={settings} />
      <StatsSection stats={stats} />

      {/* Featured Articles */}
      {featuredArticles.length > 0 && (
        <section className="py-20 max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <SectionHeader title="Articles récents" subtitle="Découvrez mes derniers articles" href="/articles" linkLabel="Tous les articles" />
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
            {featuredArticles.slice(0, 3).map((a, i) => <ContentCard key={a.id} item={a} type="article" index={i} />)}
          </div>
        </section>
      )}

      {/* Featured Projects */}
      {featuredProjects.length > 0 && (
        <section className="py-20 bg-gray-50 dark:bg-gray-900/50">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <SectionHeader title="Projets & Tutoriels" subtitle="Mes derniers projets avec tutoriels détaillés" href="/projets" linkLabel="Tous les projets" />
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
              {featuredProjects.slice(0, 3).map((p, i) => <ContentCard key={p.id} item={p} type="project" index={i} />)}
            </div>
          </div>
        </section>
      )}

      {/* Tips */}
      {featuredTips.length > 0 && (
        <section className="py-20 max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <SectionHeader title="Astuces & Conseils" subtitle="Des astuces pratiques pour améliorer vos compétences" href="/astuces" linkLabel="Toutes les astuces" />
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
            {featuredTips.slice(0, 3).map((t, i) => <ContentCard key={t.id} item={t} type="tip" index={i} />)}
          </div>
        </section>
      )}

      {/* Portfolio */}
      {featuredPortfolio.length > 0 && (
        <section className="py-20 bg-gray-50 dark:bg-gray-900/50">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <SectionHeader title="Portfolio" subtitle="Mes réalisations et travaux" href="/portfolio" linkLabel="Voir tout" />
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
              {featuredPortfolio.slice(0, 3).map((p, i) => <ContentCard key={p.id} item={p} type="portfolio" index={i} />)}
            </div>
          </div>
        </section>
      )}

      {/* Empty state when no content */}
      {featuredArticles.length === 0 && featuredProjects.length === 0 && (
        <section className="py-20 max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }}>
            <div className="w-24 h-24 bg-primary-50 dark:bg-primary-950/30 rounded-3xl flex items-center justify-center mx-auto mb-6">
              <span className="text-4xl">✍️</span>
            </div>
            <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-3">Le site est prêt !</h2>
            <p className="text-gray-500 mb-6">Connectez-vous à l'admin Django pour commencer à publier du contenu.</p>
            <a href="/admin/" className="btn-primary">Accéder à l'admin</a>
          </motion.div>
        </section>
      )}

      <Newsletter />
    </Layout>
  );
}
