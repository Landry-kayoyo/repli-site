import { useState } from 'react';
import { subscribe } from '../../lib/api';
import { FiMail, FiCheck, FiArrowRight } from 'react-icons/fi';
import { motion } from 'framer-motion';

export default function Newsletter() {
  const [email, setEmail] = useState('');
  const [name, setName] = useState('');
  const [loading, setLoading] = useState(false);
  const [success, setSuccess] = useState(false);
  const [error, setError] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true); setError('');
    try {
      await subscribe({ email, name });
      setSuccess(true); setEmail(''); setName('');
    } catch (err) {
      setError(err.response?.data?.message || 'Une erreur est survenue.');
    } finally { setLoading(false); }
  };

  return (
    <section className="py-20 bg-gradient-to-br from-primary-600 via-primary-700 to-purple-700 relative overflow-hidden">
      <div className="absolute inset-0 opacity-10">
        <div className="absolute top-0 left-1/4 w-96 h-96 bg-white rounded-full -translate-y-1/2 blur-3xl" />
        <div className="absolute bottom-0 right-1/4 w-96 h-96 bg-purple-300 rounded-full translate-y-1/2 blur-3xl" />
      </div>
      <div className="relative max-w-2xl mx-auto px-4 sm:px-6 text-center">
        <motion.div initial={{ opacity: 0, y: 20 }} whileInView={{ opacity: 1, y: 0 }} viewport={{ once: true }}>
          <div className="w-16 h-16 bg-white/20 rounded-2xl flex items-center justify-center mx-auto mb-6">
            <FiMail className="text-white" size={28} />
          </div>
          <h2 className="text-3xl md:text-4xl font-bold text-white mb-4">Restez informé</h2>
          <p className="text-primary-100 text-lg mb-8">Recevez les derniers articles, projets et astuces directement dans votre boîte mail.</p>

          {success ? (
            <div className="flex items-center justify-center gap-3 bg-white/20 text-white rounded-2xl p-6">
              <FiCheck size={24} /><span className="text-lg font-medium">Inscription réussie ! Merci.</span>
            </div>
          ) : (
            <form onSubmit={handleSubmit} className="flex flex-col sm:flex-row gap-3">
              <input type="text" value={name} onChange={e => setName(e.target.value)}
                placeholder="Votre prénom" className="flex-1 px-4 py-3 rounded-xl bg-white/10 border border-white/20 text-white placeholder-white/60 focus:outline-none focus:bg-white/20 transition-all" />
              <input type="email" value={email} onChange={e => setEmail(e.target.value)} required
                placeholder="Votre email *" className="flex-1 px-4 py-3 rounded-xl bg-white/10 border border-white/20 text-white placeholder-white/60 focus:outline-none focus:bg-white/20 transition-all" />
              <button type="submit" disabled={loading}
                className="px-6 py-3 bg-white text-primary-700 font-semibold rounded-xl hover:bg-gray-100 transition-all flex items-center gap-2 justify-center shadow-lg whitespace-nowrap">
                {loading ? 'Envoi...' : <><span>S'abonner</span><FiArrowRight /></>}
              </button>
            </form>
          )}
          {error && <p className="text-red-200 mt-3 text-sm">{error}</p>}
        </motion.div>
      </div>
    </section>
  );
}
