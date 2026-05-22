export function formatDate(dateString, locale = 'fr-FR') {
  if (!dateString) return '';
  return new Date(dateString).toLocaleDateString(locale, {
    year: 'numeric', month: 'long', day: 'numeric'
  });
}

export function formatDateShort(dateString) {
  if (!dateString) return '';
  return new Date(dateString).toLocaleDateString('fr-FR', {
    year: 'numeric', month: 'short', day: 'numeric'
  });
}

export function truncate(str, n) {
  return str && str.length > n ? str.substr(0, n - 1) + '...' : str;
}

export function getImageUrl(path) {
  if (!path) return null;
  if (path.startsWith('http')) return path;
  const base = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
  return `${base}${path}`;
}

export function difficultyLabel(d) {
  const map = { beginner: 'Débutant', intermediate: 'Intermédiaire', advanced: 'Avancé' };
  return map[d] || d;
}

export function difficultyColor(d) {
  const map = { beginner: 'bg-green-100 text-green-700', intermediate: 'bg-yellow-100 text-yellow-700', advanced: 'bg-red-100 text-red-700' };
  return map[d] || 'bg-gray-100 text-gray-700';
}

export function slugify(text) {
  return text.toString().toLowerCase().normalize('NFD').replace(/[\u0300-\u036f]/g, '').replace(/\s+/g, '-').replace(/[^\w-]+/g, '');
}
