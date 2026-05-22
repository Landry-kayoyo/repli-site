import Link from 'next/link';
import { FiGithub, FiLinkedin, FiTwitter, FiYoutube, FiFacebook, FiInstagram, FiRss } from 'react-icons/fi';

const socialIcons = { github_url: FiGithub, linkedin_url: FiLinkedin, twitter_url: FiTwitter, youtube_url: FiYoutube, facebook_url: FiFacebook, instagram_url: FiInstagram };

export default function Footer({ settings }) {
  const siteName = settings?.logo_text || 'Landry Net';
  const tagline = settings?.tagline || 'Partager, Apprendre, Innover';
  const year = new Date().getFullYear();

  return (
    <footer className="bg-gray-950 text-gray-400 mt-20">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-12">
          {/* Brand */}
          <div className="md:col-span-2">
            <div className="flex items-center gap-2 mb-4">
              <div className="w-9 h-9 rounded-xl bg-gradient-to-br from-primary-600 to-purple-600 flex items-center justify-center">
                <span className="text-white font-bold text-sm">LN</span>
              </div>
              <span className="font-bold text-xl text-white">{siteName}</span>
            </div>
            <p className="text-gray-400 mb-6 max-w-md">{tagline}</p>
            <div className="flex items-center gap-3">
              {Object.entries(socialIcons).map(([key, Icon]) =>
                settings?.[key] ? (
                  <a key={key} href={settings[key]} target="_blank" rel="noopener noreferrer"
                    className="p-2.5 rounded-xl bg-gray-800 hover:bg-primary-600 text-gray-400 hover:text-white transition-all duration-200">
                    <Icon size={16} />
                  </a>
                ) : null
              )}
              <Link href="/rss/articles/" target="_blank"
                className="p-2.5 rounded-xl bg-gray-800 hover:bg-orange-600 text-orange-400 hover:text-white transition-all duration-200">
                <FiRss size={16} />
              </Link>
            </div>
          </div>
          {/* Navigation */}
          <div>
            <h3 className="text-white font-semibold mb-4">Navigation</h3>
            <ul className="space-y-3">
              {[['/', 'Accueil'], ['/articles', 'Articles'], ['/projets', 'Projets'], ['/astuces', 'Astuces'], ['/portfolio', 'Portfolio']].map(([href, label]) => (
                <li key={href}><Link href={href} className="hover:text-white hover:translate-x-1 transition-all inline-block">{label}</Link></li>
              ))}
            </ul>
          </div>
          <div>
            <h3 className="text-white font-semibold mb-4">Autres</h3>
            <ul className="space-y-3">
              {[['/a-propos', 'À propos'], ['/contact', 'Contact'], ['/sitemap.xml', 'Sitemap'], ['/rss/articles/', 'Flux RSS']].map(([href, label]) => (
                <li key={href}><Link href={href} className="hover:text-white transition-colors">{label}</Link></li>
              ))}
            </ul>
          </div>
        </div>
        <div className="border-t border-gray-800 mt-12 pt-8 flex flex-col md:flex-row items-center justify-between gap-4">
          <p className="text-sm">© {year} <span className="text-primary-400">{siteName}</span>. Tous droits réservés.</p>
          <p className="text-sm">Fait avec ❤️ par {settings?.author_name || 'Landry'}</p>
        </div>
      </div>
    </footer>
  );
}
