import Layout from '../../components/layout/Layout';
import Comments from '../../components/ui/Comments';
import Reactions from '../../components/ui/Reactions';
import { getSiteSettings, getProject } from '../../lib/api';
import { formatDate } from '../../lib/utils';
import { FiCalendar, FiEye, FiGithub, FiExternalLink, FiArrowLeft, FiTag, FiShare2 } from 'react-icons/fi';
import Link from 'next/link';
import { motion } from 'framer-motion';

export async function getServerSideProps({ params }) {
  try {
    const [settingsRes, projectRes] = await Promise.all([getSiteSettings(), getProject(params.slug)]);
    return { props: { settings: settingsRes.data, project: projectRes.data } };
  } catch { return { notFound: true }; }
}

export default function ProjectDetailPage({ settings, project }) {
  const technologies = project.technologies ? project.technologies.split(',').map(t => t.trim()).filter(Boolean) : [];

  return (
    <Layout settings={settings} title={project.meta_title || project.title} description={project.meta_description || project.description} image={project.cover_image_url}>
      {project.cover_image_url && (
        <div className="w-full aspect-[21/9] max-h-[500px] overflow-hidden">
          <img src={project.cover_image_url} alt={project.title} className="w-full h-full object-cover" />
        </div>
      )}
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <Link href="/projets" className="flex items-center gap-2 text-gray-500 hover:text-primary-600 mb-8 transition-colors">
          <FiArrowLeft size={16} /> Retour aux projets
        </Link>
        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }}>
          {project.category_name && (
            <span className="badge bg-purple-100 text-purple-700 mb-4 inline-block">{project.category_name}</span>
          )}
          <h1 className="text-3xl md:text-5xl font-black text-gray-900 dark:text-white mb-3">{project.title}</h1>
          {project.subtitle && <p className="text-xl text-gray-600 dark:text-gray-400 mb-6">{project.subtitle}</p>}

          <div className="flex flex-wrap items-center gap-4 text-sm text-gray-500 mb-6 pb-6 border-b border-gray-100 dark:border-gray-800">
            {project.published_at && <span className="flex items-center gap-1"><FiCalendar size={14} />{formatDate(project.published_at)}</span>}
            {project.views_count !== undefined && <span className="flex items-center gap-1"><FiEye size={14} />{project.views_count} vues</span>}
            {project.github_url && <a href={project.github_url} target="_blank" rel="noopener noreferrer" className="flex items-center gap-1 text-gray-700 dark:text-gray-300 hover:text-primary-600"><FiGithub size={14} />GitHub</a>}
            {project.demo_url && <a href={project.demo_url} target="_blank" rel="noopener noreferrer" className="flex items-center gap-1 text-primary-600 hover:text-primary-700"><FiExternalLink size={14} />Demo</a>}
          </div>

          {technologies.length > 0 && (
            <div className="flex flex-wrap gap-2 mb-8">
              {technologies.map(tech => (
                <span key={tech} className="px-3 py-1 bg-gray-100 dark:bg-gray-800 text-gray-700 dark:text-gray-300 rounded-full text-sm font-medium">{tech}</span>
              ))}
            </div>
          )}

          <p className="text-lg text-gray-600 dark:text-gray-400 italic border-l-4 border-purple-400 pl-4 mb-8">{project.description}</p>

          <div className="prose-custom" dangerouslySetInnerHTML={{ __html: project.content }} />

          {project.tutorial_steps && (
            <div className="mt-10">
              <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-6">📋 Étapes du tutoriel</h2>
              <div className="prose-custom bg-gray-50 dark:bg-gray-900/50 rounded-2xl p-6" dangerouslySetInnerHTML={{ __html: project.tutorial_steps }} />
            </div>
          )}

          {project.tags && project.tags.length > 0 && (
            <div className="flex flex-wrap gap-2 mt-8 pt-8 border-t border-gray-100 dark:border-gray-800">
              <FiTag className="text-gray-400 mt-0.5" />
              {project.tags.map(tag => <Link key={tag} href={`/projets?tag=${tag}`} className="px-3 py-1 bg-gray-100 dark:bg-gray-800 text-gray-600 rounded-full text-sm hover:text-primary-600 transition-colors">{tag}</Link>)}
            </div>
          )}

          <div className="mt-8 pt-8 border-t border-gray-100 dark:border-gray-800">
            <h4 className="font-semibold text-gray-700 dark:text-gray-300 mb-3">Votre réaction :</h4>
            <Reactions contentType="projects.project" objectId={project.id} />
          </div>

          <script type="application/ld+json" dangerouslySetInnerHTML={{ __html: JSON.stringify({ '@context': 'https://schema.org', '@type': 'SoftwareApplication', name: project.title, description: project.description, url: project.demo_url || '', author: { '@type': 'Person', name: project.author_name } })}} />

          <Comments contentType="projects.project" objectId={project.id} />
        </motion.div>
      </div>
    </Layout>
  );
}
