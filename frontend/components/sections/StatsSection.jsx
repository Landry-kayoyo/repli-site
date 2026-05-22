import { motion } from 'framer-motion';
import { FiFileText, FiBox, FiZap, FiLayers } from 'react-icons/fi';

const icons = [FiFileText, FiBox, FiZap, FiLayers];
const labels = ['Articles publiés', 'Projets réalisés', 'Astuces partagées', 'Travaux de portfolio'];
const keys = ['articles_count', 'projects_count', 'tips_count', 'portfolio_count'];
const colors = ['from-blue-500 to-cyan-500', 'from-purple-500 to-pink-500', 'from-green-500 to-emerald-500', 'from-orange-500 to-yellow-500'];

export default function StatsSection({ stats }) {
  return (
    <section className="py-16 bg-white dark:bg-gray-900">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="grid grid-cols-2 md:grid-cols-4 gap-6">
          {keys.map((key, i) => {
            const Icon = icons[i];
            return (
              <motion.div key={key} initial={{ opacity: 0, y: 20 }} whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }} transition={{ delay: i * 0.1 }}
                className="card p-6 text-center group hover:shadow-xl transition-all duration-300">
                <div className={`w-12 h-12 rounded-2xl bg-gradient-to-br ${colors[i]} flex items-center justify-center mx-auto mb-4 group-hover:scale-110 transition-transform shadow-lg`}>
                  <Icon className="text-white" size={22} />
                </div>
                <p className="text-3xl font-black text-gray-900 dark:text-white mb-1">{stats?.[key] ?? 0}</p>
                <p className="text-sm text-gray-500 dark:text-gray-400">{labels[i]}</p>
              </motion.div>
            );
          })}
        </div>
      </div>
    </section>
  );
}
