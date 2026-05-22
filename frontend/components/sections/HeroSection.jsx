import { motion } from 'framer-motion';
import Link from 'next/link';
import { FiArrowRight, FiGithub, FiLinkedin, FiDownload } from 'react-icons/fi';

export default function HeroSection({ settings }) {
  const name = settings?.author_name || 'Landry';
  const jobTitle = settings?.author_job_title || 'Développeur & Créateur de contenu';
  const bio = settings?.author_bio || 'Passionné par la technologie, je partage mes connaissances à travers des articles, projets et astuces.';
  const photo = settings?.author_photo_url;
  const siteName = settings?.site_name || 'Landry Net';

  return (
    <section className="relative min-h-[92vh] flex items-center overflow-hidden">
      {/* Background */}
      <div className="absolute inset-0 bg-gradient-to-br from-primary-50 via-white to-purple-50 dark:from-gray-950 dark:via-gray-900 dark:to-gray-950" />
      <div className="absolute top-20 right-0 w-[600px] h-[600px] bg-primary-100 dark:bg-primary-950/20 rounded-full blur-3xl opacity-60 -z-0" />
      <div className="absolute bottom-0 left-0 w-[400px] h-[400px] bg-purple-100 dark:bg-purple-950/20 rounded-full blur-3xl opacity-40 -z-0" />

      <div className="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-20 w-full">
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-16 items-center">
          {/* Text */}
          <div>
            <motion.div initial={{ opacity: 0, y: 30 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.6 }}>
              <span className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-primary-100 dark:bg-primary-950/50 text-primary-700 dark:text-primary-300 text-sm font-medium mb-6">
                <span className="w-2 h-2 bg-green-400 rounded-full animate-pulse" />
                Bienvenue sur {siteName}
              </span>
              <h1 className="text-5xl md:text-6xl lg:text-7xl font-black text-gray-900 dark:text-white mb-4 leading-tight">
                Bonjour, je suis<br />
                <span className="gradient-text">{name}</span>
              </h1>
              <p className="text-xl text-primary-600 dark:text-primary-400 font-semibold mb-6">{jobTitle}</p>
              <p className="text-gray-600 dark:text-gray-400 text-lg leading-relaxed mb-10 max-w-xl">{bio}</p>

              <div className="flex flex-wrap gap-4">
                <Link href="/articles" className="btn-primary text-base px-8 py-4">
                  Explorer le blog <FiArrowRight />
                </Link>
                <Link href="/a-propos" className="btn-secondary text-base px-8 py-4">
                  À propos
                </Link>
                {settings?.cv_file && (
                  <a href={settings.cv_file} download className="btn-secondary text-base px-8 py-4">
                    <FiDownload /> CV
                  </a>
                )}
              </div>

              <div className="flex items-center gap-4 mt-8">
                {settings?.github_url && (
                  <a href={settings.github_url} target="_blank" rel="noopener noreferrer" className="text-gray-500 hover:text-gray-900 dark:hover:text-white transition-colors">
                    <FiGithub size={24} />
                  </a>
                )}
                {settings?.linkedin_url && (
                  <a href={settings.linkedin_url} target="_blank" rel="noopener noreferrer" className="text-gray-500 hover:text-primary-600 transition-colors">
                    <FiLinkedin size={24} />
                  </a>
                )}
              </div>
            </motion.div>
          </div>

          {/* Photo */}
          <motion.div initial={{ opacity: 0, scale: 0.9 }} animate={{ opacity: 1, scale: 1 }}
            transition={{ duration: 0.6, delay: 0.2 }} className="flex justify-center lg:justify-end">
            <div className="relative">
              <div className="absolute inset-0 bg-gradient-to-br from-primary-400 to-purple-600 rounded-3xl blur-2xl opacity-30 scale-105" />
              {photo ? (
                <img src={photo} alt={name}
                  className="relative w-80 h-80 lg:w-96 lg:h-96 object-cover rounded-3xl shadow-2xl ring-4 ring-white dark:ring-gray-800" />
              ) : (
                <div className="relative w-80 h-80 lg:w-96 lg:h-96 rounded-3xl bg-gradient-to-br from-primary-400 to-purple-600 flex items-center justify-center shadow-2xl">
                  <span className="text-8xl text-white font-black">{name[0]}</span>
                </div>
              )}
              {/* Floating badge */}
              <div className="absolute -bottom-4 -right-4 bg-white dark:bg-gray-900 rounded-2xl shadow-xl px-4 py-3 flex items-center gap-2">
                <span className="text-2xl">✨</span>
                <div>
                  <p className="text-xs text-gray-500">Contenus créés</p>
                  <p className="font-bold text-gray-900 dark:text-white">Articles & Projets</p>
                </div>
              </div>
            </div>
          </motion.div>
        </div>
      </div>

      {/* Scroll indicator */}
      <motion.div animate={{ y: [0, 10, 0] }} transition={{ repeat: Infinity, duration: 2 }}
        className="absolute bottom-8 left-1/2 -translate-x-1/2">
        <div className="w-6 h-10 border-2 border-gray-300 dark:border-gray-600 rounded-full flex items-start justify-center p-1">
          <div className="w-1.5 h-3 bg-gray-400 rounded-full" />
        </div>
      </motion.div>
    </section>
  );
}
