import { useState, useEffect } from 'react';
import Link from 'next/link';
import { useRouter } from 'next/router';
import { FiSearch, FiMenu, FiX, FiMoon, FiSun, FiRss } from 'react-icons/fi';
import { motion, AnimatePresence } from 'framer-motion';
import { useTheme } from 'next-themes';
import SearchModal from '../ui/SearchModal';

const navLinks = [
  { href: '/', label: 'Accueil' },
  { href: '/articles', label: 'Articles' },
  { href: '/projets', label: 'Projets' },
  { href: '/astuces', label: 'Astuces' },
  { href: '/portfolio', label: 'Portfolio' },
  { href: '/a-propos', label: 'À propos' },
  { href: '/contact', label: 'Contact' },
];

export default function Navbar({ settings }) {
  const [isOpen, setIsOpen] = useState(false);
  const [scrolled, setScrolled] = useState(false);
  const [searchOpen, setSearchOpen] = useState(false);
  const { theme, setTheme } = useTheme();
  const [mounted, setMounted] = useState(false);
  const router = useRouter();

  useEffect(() => {
    setMounted(true);
    const handleScroll = () => setScrolled(window.scrollY > 20);
    window.addEventListener('scroll', handleScroll);
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  useEffect(() => { setIsOpen(false); }, [router.pathname]);

  const siteName = settings?.logo_text || 'Landry Net';
  const logoUrl = settings?.logo_url;

  return (
    <>
      <nav className={`fixed top-0 left-0 right-0 z-50 transition-all duration-300 ${scrolled ? 'bg-white/90 dark:bg-gray-950/90 backdrop-blur-md shadow-sm border-b border-gray-100 dark:border-gray-800' : 'bg-transparent'}`}>
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            {/* Logo */}
            <Link href="/" className="flex items-center gap-2 group">
              {logoUrl ? (
                <img src={logoUrl} alt={siteName} className="h-9 w-auto" />
              ) : (
                <div className="w-9 h-9 rounded-xl bg-gradient-to-br from-primary-600 to-purple-600 flex items-center justify-center shadow-lg group-hover:shadow-primary-500/40 transition-shadow">
                  <span className="text-white font-bold text-sm">LN</span>
                </div>
              )}
              <span className="font-bold text-xl text-gray-900 dark:text-white group-hover:text-primary-600 transition-colors">
                {siteName}
              </span>
            </Link>

            {/* Desktop Nav */}
            <div className="hidden md:flex items-center gap-1">
              {navLinks.map(link => (
                <Link key={link.href} href={link.href}
                  className={`px-4 py-2 rounded-lg text-sm font-medium transition-all duration-200 ${
                    router.pathname === link.href || router.pathname.startsWith(link.href + '/')
                      ? 'text-primary-600 dark:text-primary-400 bg-primary-50 dark:bg-primary-950/50'
                      : 'text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-white hover:bg-gray-100 dark:hover:bg-gray-800'
                  }`}>
                  {link.label}
                </Link>
              ))}
            </div>

            {/* Actions */}
            <div className="flex items-center gap-2">
              <button onClick={() => setSearchOpen(true)}
                className="p-2 rounded-lg text-gray-500 dark:text-gray-400 hover:text-gray-900 dark:hover:text-white hover:bg-gray-100 dark:hover:bg-gray-800 transition-all">
                <FiSearch size={18} />
              </button>
              {mounted && (
                <button onClick={() => setTheme(theme === 'dark' ? 'light' : 'dark')}
                  className="p-2 rounded-lg text-gray-500 dark:text-gray-400 hover:text-gray-900 dark:hover:text-white hover:bg-gray-100 dark:hover:bg-gray-800 transition-all">
                  {theme === 'dark' ? <FiSun size={18} /> : <FiMoon size={18} />}
                </button>
              )}
              <Link href="/rss/articles/" target="_blank"
                className="hidden sm:block p-2 rounded-lg text-orange-500 hover:bg-orange-50 dark:hover:bg-orange-950/30 transition-all">
                <FiRss size={18} />
              </Link>
              <button onClick={() => setIsOpen(!isOpen)}
                className="md:hidden p-2 rounded-lg text-gray-500 hover:bg-gray-100 dark:hover:bg-gray-800 transition-all">
                {isOpen ? <FiX size={20} /> : <FiMenu size={20} />}
              </button>
            </div>
          </div>
        </div>

        {/* Mobile Menu */}
        <AnimatePresence>
          {isOpen && (
            <motion.div initial={{ opacity: 0, height: 0 }} animate={{ opacity: 1, height: 'auto' }}
              exit={{ opacity: 0, height: 0 }} className="md:hidden bg-white dark:bg-gray-950 border-t border-gray-100 dark:border-gray-800">
              <div className="px-4 py-3 flex flex-col gap-1">
                {navLinks.map(link => (
                  <Link key={link.href} href={link.href}
                    className={`px-4 py-3 rounded-xl text-sm font-medium transition-all ${
                      router.pathname === link.href
                        ? 'text-primary-600 bg-primary-50 dark:bg-primary-950/50'
                        : 'text-gray-600 dark:text-gray-400 hover:bg-gray-50 dark:hover:bg-gray-900'
                    }`}>
                    {link.label}
                  </Link>
                ))}
              </div>
            </motion.div>
          )}
        </AnimatePresence>
      </nav>
      <SearchModal isOpen={searchOpen} onClose={() => setSearchOpen(false)} />
    </>
  );
}
