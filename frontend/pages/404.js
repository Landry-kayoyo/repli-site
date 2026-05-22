import Layout from '../components/layout/Layout';
import Link from 'next/link';
import { motion } from 'framer-motion';
import { FiArrowLeft } from 'react-icons/fi';

export default function NotFound() {
  return (
    <Layout title="Page non trouvée">
      <div className="min-h-[80vh] flex items-center justify-center px-4">
        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} className="text-center">
          <div className="text-8xl mb-8">🔍</div>
          <h1 className="text-6xl font-black text-primary-600 mb-4">404</h1>
          <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-4">Page non trouvée</h2>
          <p className="text-gray-500 mb-8 max-w-md">La page que vous cherchez n'existe pas ou a été déplacée.</p>
          <Link href="/" className="btn-primary"><FiArrowLeft />Retour à l'accueil</Link>
        </motion.div>
      </div>
    </Layout>
  );
}
