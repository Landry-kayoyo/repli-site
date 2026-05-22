import Head from 'next/head';
import Navbar from './Navbar';
import Footer from './Footer';
import { useEffect, useState } from 'react';
import { getSiteSettings } from '../../lib/api';

export default function Layout({ children, title, description, image, settings: propSettings }) {
  const [settings, setSettings] = useState(propSettings || null);

  useEffect(() => {
    if (!propSettings) {
      getSiteSettings().then(r => setSettings(r.data)).catch(() => {});
    }
  }, [propSettings]);

  const siteName = settings?.site_name || 'Landry Net';
  const metaTitle = title ? `${title} | ${siteName}` : siteName;
  const metaDesc = description || settings?.description || 'Site personnel et professionnel de Landry';
  const metaImage = image || settings?.author_photo_url;

  return (
    <>
      <Head>
        <title>{metaTitle}</title>
        <meta name="description" content={metaDesc} />
        <meta name="keywords" content={settings?.meta_keywords || ''} />
        <meta name="viewport" content="width=device-width, initial-scale=1" />
        <link rel="icon" href={settings?.favicon_url || '/favicon.ico'} />

        {/* Open Graph */}
        <meta property="og:title" content={metaTitle} />
        <meta property="og:description" content={metaDesc} />
        <meta property="og:type" content="website" />
        {metaImage && <meta property="og:image" content={metaImage} />}

        {/* Twitter */}
        <meta name="twitter:card" content="summary_large_image" />
        <meta name="twitter:title" content={metaTitle} />
        <meta name="twitter:description" content={metaDesc} />
        {metaImage && <meta name="twitter:image" content={metaImage} />}

        {/* RSS */}
        <link rel="alternate" type="application/rss+xml" title={`${siteName} - Articles`} href="/rss/articles/" />

        {/* PWA */}
        <meta name="theme-color" content={settings?.pwa_theme_color || '#4F46E5'} />
        <link rel="manifest" href="/manifest.json" />

        {/* Schema.org */}
        <script type="application/ld+json" dangerouslySetInnerHTML={{ __html: JSON.stringify({
          '@context': 'https://schema.org',
          '@type': 'Person',
          name: settings?.author_name || 'Landry',
          url: typeof window !== 'undefined' ? window.location.origin : '',
          sameAs: [settings?.github_url, settings?.linkedin_url, settings?.twitter_url].filter(Boolean),
        })}} />

        {/* Google Analytics */}
        {settings?.google_analytics_id && (
          <script key="ga-src" async src={`https://www.googletagmanager.com/gtag/js?id=${settings.google_analytics_id}`} />
        )}
        {settings?.google_analytics_id && (
          <script key="ga-inline" dangerouslySetInnerHTML={{ __html: `window.dataLayer=window.dataLayer||[];function gtag(){dataLayer.push(arguments)}gtag('js',new Date());gtag('config','${settings.google_analytics_id}');` }} />
        )}
      </Head>

      <div className="min-h-screen flex flex-col">
        <Navbar settings={settings} />
        <main className="flex-1 pt-16">{children}</main>
        <Footer settings={settings} />
      </div>
    </>
  );
}
