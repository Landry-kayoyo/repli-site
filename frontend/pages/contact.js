import { useState } from 'react';
import Layout from '../components/layout/Layout';
import { getSiteSettings } from '../lib/api';
import { sendContact } from '../lib/api';
import { FiSend, FiMail, FiMapPin, FiGithub, FiLinkedin, FiTwitter, FiCheck } from 'react-icons/fi';
import { motion } from 'framer-motion';

export async function getServerSideProps() {
  try {
    const settingsRes = await getSiteSettings();
    return { props: { settings: settingsRes.data } };
  } catch { return { props: { settings: null } }; }
}

export default function ContactPage({ settings }) {
  const [form, setForm] = useState({ name: '', email: '', subject: '', message: '' });
  const [loading, setLoading] = useState(false);
  const [success, setSuccess] = useState(false);
  const [error, setError] = useState('');

  const handleChange = e => setForm(p => ({ ...p, [e.target.name]: e.target.value }));

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true); setError('');
    try {
      await sendContact(form);
      setSuccess(true); setForm({ name: '', email: '', subject: '', message: '' });
    } catch (err) {
      setError(err.response?.data?.message || 'Une erreur est survenue. Veuillez réessayer.');
    } finally { setLoading(false); }
  };

  return (
    <Layout settings={settings} title="Contact" description="Contactez-moi pour toute question ou collaboration.">
      {/* Hero */}
      <div className="bg-gradient-to-br from-primary-600 to-purple-700 text-white py-20">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }}>
            <h1 className="text-4xl md:text-5xl font-black mb-4">Contactez-moi</h1>
            <p className="text-primary-100 text-xl max-w-2xl">Une question, un projet ou juste envie d'échanger ? Je suis là.</p>
          </motion.div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16">
        <div className="grid grid-cols-1 lg:grid-cols-5 gap-12">
          {/* Info */}
          <motion.div initial={{ opacity: 0, x: -20 }} animate={{ opacity: 1, x: 0 }} className="lg:col-span-2 space-y-6">
            <div>
              <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-4">Informations de contact</h2>
              <p className="text-gray-600 dark:text-gray-400 leading-relaxed">
                N'hésitez pas à me contacter pour toute question, collaboration ou opportunité professionnelle.
              </p>
            </div>
            <div className="space-y-4">
              {settings?.author_email && (
                <div className="flex items-center gap-4 p-4 card rounded-2xl">
                  <div className="w-10 h-10 bg-primary-100 dark:bg-primary-950/30 rounded-xl flex items-center justify-center">
                    <FiMail className="text-primary-600" />
                  </div>
                  <div>
                    <p className="text-xs text-gray-500">Email</p>
                    <a href={`mailto:${settings.author_email}`} className="font-medium text-gray-900 dark:text-white hover:text-primary-600 transition-colors">{settings.author_email}</a>
                  </div>
                </div>
              )}
              {settings?.author_location && (
                <div className="flex items-center gap-4 p-4 card rounded-2xl">
                  <div className="w-10 h-10 bg-green-100 dark:bg-green-950/30 rounded-xl flex items-center justify-center">
                    <FiMapPin className="text-green-600" />
                  </div>
                  <div>
                    <p className="text-xs text-gray-500">Localisation</p>
                    <p className="font-medium text-gray-900 dark:text-white">{settings.author_location}</p>
                  </div>
                </div>
              )}
            </div>
            {/* Social links */}
            <div>
              <p className="text-sm font-semibold text-gray-500 dark:text-gray-400 mb-3 uppercase tracking-wider">Réseaux sociaux</p>
              <div className="flex flex-wrap gap-3">
                {[['github_url', FiGithub, 'GitHub'], ['linkedin_url', FiLinkedin, 'LinkedIn'], ['twitter_url', FiTwitter, 'Twitter']].map(([key, Icon, label]) =>
                  settings?.[key] ? (
                    <a key={key} href={settings[key]} target="_blank" rel="noopener noreferrer"
                      className="flex items-center gap-2 px-4 py-2 bg-gray-100 dark:bg-gray-800 rounded-xl text-sm font-medium text-gray-600 dark:text-gray-400 hover:text-primary-600 hover:bg-primary-50 dark:hover:bg-primary-950/30 transition-all">
                      <Icon size={16} />{label}
                    </a>
                  ) : null
                )}
              </div>
            </div>
          </motion.div>

          {/* Form */}
          <motion.div initial={{ opacity: 0, x: 20 }} animate={{ opacity: 1, x: 0 }} className="lg:col-span-3">
            <div className="card p-8">
              {success ? (
                <div className="text-center py-12">
                  <div className="w-20 h-20 bg-green-100 dark:bg-green-950/30 rounded-full flex items-center justify-center mx-auto mb-4">
                    <FiCheck className="text-green-600" size={32} />
                  </div>
                  <h3 className="text-2xl font-bold text-gray-900 dark:text-white mb-2">Message envoyé !</h3>
                  <p className="text-gray-500">Je vous répondrai dans les plus brefs délais.</p>
                  <button onClick={() => setSuccess(false)} className="btn-primary mt-6">Envoyer un autre message</button>
                </div>
              ) : (
                <form onSubmit={handleSubmit} className="space-y-5">
                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-5">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1.5">Nom *</label>
                      <input name="name" value={form.name} onChange={handleChange} required placeholder="Votre nom" className="input-field" />
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1.5">Email *</label>
                      <input name="email" type="email" value={form.email} onChange={handleChange} required placeholder="votre@email.com" className="input-field" />
                    </div>
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1.5">Sujet *</label>
                    <input name="subject" value={form.subject} onChange={handleChange} required placeholder="Sujet de votre message" className="input-field" />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1.5">Message *</label>
                    <textarea name="message" value={form.message} onChange={handleChange} required rows={6}
                      placeholder="Votre message..." className="input-field resize-none" />
                  </div>
                  {error && <p className="text-red-600 dark:text-red-400 text-sm bg-red-50 dark:bg-red-950/30 p-3 rounded-xl">{error}</p>}
                  <button type="submit" disabled={loading} className="btn-primary w-full justify-center py-4 text-base">
                    <FiSend size={18} />{loading ? 'Envoi en cours...' : 'Envoyer le message'}
                  </button>
                </form>
              )}
            </div>
          </motion.div>
        </div>
      </div>
    </Layout>
  );
}
