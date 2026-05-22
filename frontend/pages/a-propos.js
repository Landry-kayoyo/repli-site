import Layout from '../components/layout/Layout';
import { getSiteSettings, getSkills, getExperiences, getEducations } from '../lib/api';
import { formatDate } from '../lib/utils';
import { FiGithub, FiLinkedin, FiTwitter, FiYoutube, FiFacebook, FiInstagram, FiDownload, FiMapPin, FiMail, FiBriefcase, FiBook } from 'react-icons/fi';
import { motion } from 'framer-motion';
import Link from 'next/link';

const socialIcons = { github_url: FiGithub, linkedin_url: FiLinkedin, twitter_url: FiTwitter, youtube_url: FiYoutube, facebook_url: FiFacebook, instagram_url: FiInstagram };
const socialLabels = { github_url: 'GitHub', linkedin_url: 'LinkedIn', twitter_url: 'Twitter', youtube_url: 'YouTube', facebook_url: 'Facebook', instagram_url: 'Instagram' };

export async function getServerSideProps() {
  try {
    const [settingsRes, skillsRes, experiencesRes, educationsRes] = await Promise.all([
      getSiteSettings(), getSkills(), getExperiences(), getEducations()
    ]);
    return {
      props: {
        settings: settingsRes.data,
        skills: skillsRes.data.results || skillsRes.data || [],
        experiences: experiencesRes.data.results || experiencesRes.data || [],
        educations: educationsRes.data.results || educationsRes.data || [],
      }
    };
  } catch { return { props: { settings: null, skills: [], experiences: [], educations: [] } }; }
}

function SkillBar({ skill, index }) {
  return (
    <motion.div initial={{ opacity: 0, x: -20 }} whileInView={{ opacity: 1, x: 0 }} viewport={{ once: true }} transition={{ delay: index * 0.05 }}>
      <div className="flex items-center justify-between mb-2">
        <span className="font-medium text-gray-700 dark:text-gray-300 text-sm">{skill.icon && `${skill.icon} `}{skill.name}</span>
        <span className="text-primary-600 font-bold text-sm">{skill.level}%</span>
      </div>
      <div className="h-2.5 bg-gray-100 dark:bg-gray-800 rounded-full overflow-hidden">
        <motion.div initial={{ width: 0 }} whileInView={{ width: `${skill.level}%` }} viewport={{ once: true }} transition={{ duration: 1, delay: index * 0.05 }}
          className="h-full rounded-full bg-gradient-to-r from-primary-500 to-purple-500" />
      </div>
    </motion.div>
  );
}

export default function AboutPage({ settings, skills, experiences, educations }) {
  const skillsByCategory = skills.reduce((acc, skill) => {
    const cat = skill.category || 'Général';
    if (!acc[cat]) acc[cat] = [];
    acc[cat].push(skill);
    return acc;
  }, {});

  return (
    <Layout settings={settings} title={settings?.about_title || 'À propos'} description={settings?.author_bio || 'En savoir plus sur moi.'}>
      {/* Hero */}
      <section className="relative py-24 bg-gradient-to-br from-primary-50 via-white to-purple-50 dark:from-gray-950 dark:via-gray-900 dark:to-gray-950 overflow-hidden">
        <div className="absolute top-0 right-0 w-96 h-96 bg-primary-100 dark:bg-primary-950/20 rounded-full blur-3xl opacity-50" />
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-16 items-center">
            <motion.div initial={{ opacity: 0, y: 30 }} animate={{ opacity: 1, y: 0 }}>
              <h1 className="text-4xl md:text-5xl font-black text-gray-900 dark:text-white mb-4">
                {settings?.about_title || 'À propos de moi'}
              </h1>
              <p className="text-primary-600 dark:text-primary-400 font-semibold text-xl mb-6">{settings?.author_job_title}</p>
              {settings?.author_location && (
                <div className="flex items-center gap-2 text-gray-500 mb-4"><FiMapPin /><span>{settings.author_location}</span></div>
              )}
              {settings?.author_email && (
                <div className="flex items-center gap-2 text-gray-500 mb-6"><FiMail /><a href={`mailto:${settings.author_email}`} className="hover:text-primary-600 transition-colors">{settings.author_email}</a></div>
              )}
              <p className="text-gray-600 dark:text-gray-400 text-lg leading-relaxed mb-8">{settings?.author_bio}</p>
              <div className="flex flex-wrap gap-3 mb-8">
                {Object.entries(socialIcons).map(([key, Icon]) =>
                  settings?.[key] ? (
                    <a key={key} href={settings[key]} target="_blank" rel="noopener noreferrer"
                      className="flex items-center gap-2 px-4 py-2 bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-xl text-sm font-medium text-gray-600 dark:text-gray-400 hover:text-primary-600 hover:border-primary-300 transition-all shadow-sm">
                      <Icon size={16} />{socialLabels[key]}
                    </a>
                  ) : null
                )}
              </div>
              {settings?.cv_file && (
                <a href={settings.cv_file} download className="btn-primary"><FiDownload />Télécharger mon CV</a>
              )}
            </motion.div>
            <motion.div initial={{ opacity: 0, scale: 0.9 }} animate={{ opacity: 1, scale: 1 }} transition={{ delay: 0.2 }} className="flex justify-center">
              {settings?.author_photo_url ? (
                <img src={settings.author_photo_url} alt={settings.author_name}
                  className="w-80 h-80 object-cover rounded-3xl shadow-2xl ring-4 ring-white dark:ring-gray-800" />
              ) : (
                <div className="w-80 h-80 bg-gradient-to-br from-primary-400 to-purple-600 rounded-3xl flex items-center justify-center shadow-2xl">
                  <span className="text-7xl text-white font-black">{(settings?.author_name || 'L')[0]}</span>
                </div>
              )}
            </motion.div>
          </div>
        </div>
      </section>

      {/* About content */}
      {settings?.about_content && (
        <section className="py-16 max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="prose-custom" dangerouslySetInnerHTML={{ __html: settings.about_content }} />
        </section>
      )}

      {/* Skills */}
      {skills.length > 0 && (
        <section className="py-16 bg-gray-50 dark:bg-gray-900/50">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <h2 className="section-title mb-10 text-center">Compétences</h2>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-10">
              {Object.entries(skillsByCategory).map(([category, catSkills]) => (
                <div key={category} className="card p-6">
                  <h3 className="font-bold text-gray-900 dark:text-white text-lg mb-6">{category}</h3>
                  <div className="space-y-5">
                    {catSkills.map((skill, i) => <SkillBar key={skill.id} skill={skill} index={i} />)}
                  </div>
                </div>
              ))}
            </div>
          </div>
        </section>
      )}

      {/* Experience */}
      {experiences.length > 0 && (
        <section className="py-16 max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
          <h2 className="section-title mb-10 flex items-center gap-3"><FiBriefcase className="text-primary-600" />Expériences</h2>
          <div className="space-y-6">
            {experiences.map((exp, i) => (
              <motion.div key={exp.id} initial={{ opacity: 0, x: -20 }} whileInView={{ opacity: 1, x: 0 }} viewport={{ once: true }} transition={{ delay: i * 0.1 }}
                className="card p-6 flex gap-6">
                <div className="w-12 h-12 rounded-xl bg-primary-100 dark:bg-primary-950/30 flex items-center justify-center flex-shrink-0">
                  <FiBriefcase className="text-primary-600" size={20} />
                </div>
                <div>
                  <h3 className="font-bold text-gray-900 dark:text-white text-lg">{exp.title}</h3>
                  <p className="text-primary-600 font-medium">{exp.company}{exp.location && ` • ${exp.location}`}</p>
                  <p className="text-sm text-gray-400 mb-3">{formatDate(exp.start_date)} — {exp.is_current ? 'Présent' : formatDate(exp.end_date)}</p>
                  <p className="text-gray-600 dark:text-gray-400">{exp.description}</p>
                </div>
              </motion.div>
            ))}
          </div>
        </section>
      )}

      {/* Education */}
      {educations.length > 0 && (
        <section className="py-16 bg-gray-50 dark:bg-gray-900/50">
          <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
            <h2 className="section-title mb-10 flex items-center gap-3"><FiBook className="text-primary-600" />Formation</h2>
            <div className="space-y-6">
              {educations.map((edu, i) => (
                <motion.div key={edu.id} initial={{ opacity: 0, x: -20 }} whileInView={{ opacity: 1, x: 0 }} viewport={{ once: true }} transition={{ delay: i * 0.1 }}
                  className="card p-6 flex gap-6">
                  <div className="w-12 h-12 rounded-xl bg-green-100 dark:bg-green-950/30 flex items-center justify-center flex-shrink-0">
                    <FiBook className="text-green-600" size={20} />
                  </div>
                  <div>
                    <h3 className="font-bold text-gray-900 dark:text-white text-lg">{edu.degree}</h3>
                    <p className="text-green-600 font-medium">{edu.institution}{edu.location && ` • ${edu.location}`}</p>
                    <p className="text-sm text-gray-400">{formatDate(edu.start_date)} — {edu.is_current ? 'Présent' : formatDate(edu.end_date)}</p>
                    {edu.description && <p className="text-gray-600 dark:text-gray-400 mt-2">{edu.description}</p>}
                  </div>
                </motion.div>
              ))}
            </div>
          </div>
        </section>
      )}
    </Layout>
  );
}
