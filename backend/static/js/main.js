/* Landry Net — Main JS v4 */

const API_BASE = '/api';

/* ========= THEME ========= */
function initTheme() {
  const saved = localStorage.getItem('theme') || 'light';
  document.documentElement.setAttribute('data-theme', saved);
  updateThemeIcons(saved);
}

function toggleTheme() {
  const current = document.documentElement.getAttribute('data-theme') || 'light';
  const next = current === 'dark' ? 'light' : 'dark';
  document.documentElement.setAttribute('data-theme', next);
  localStorage.setItem('theme', next);
  updateThemeIcons(next);
}

function updateThemeIcons(theme) {
  document.querySelectorAll('.theme-icon-light').forEach(el => el.style.display = theme === 'dark' ? 'none' : 'block');
  document.querySelectorAll('.theme-icon-dark').forEach(el => el.style.display = theme === 'dark' ? 'block' : 'none');
}

/* ========= NAVBAR ========= */
function initNavbar() {
  const navbar = document.querySelector('.navbar');
  const hamburger = document.querySelector('.hamburger');
  const mobileMenu = document.querySelector('.mobile-menu');
  const hamburgerIcon = document.getElementById('hamburgerIcon');

  if (navbar) {
    const onScroll = () => navbar.classList.toggle('scrolled', window.scrollY > 10);
    window.addEventListener('scroll', onScroll, { passive: true });
    onScroll();
  }

  if (hamburger && mobileMenu) {
    hamburger.addEventListener('click', (e) => {
      e.stopPropagation();
      const isOpen = mobileMenu.classList.toggle('open');
      if (hamburgerIcon) {
        hamburgerIcon.className = isOpen ? 'bi bi-x-lg' : 'bi bi-list';
        hamburgerIcon.style.fontSize = isOpen ? '1.1rem' : '1.3rem';
      }
    });
    document.addEventListener('click', (e) => {
      if (!hamburger.contains(e.target) && !mobileMenu.contains(e.target)) {
        mobileMenu.classList.remove('open');
        if (hamburgerIcon) { hamburgerIcon.className = 'bi bi-list'; hamburgerIcon.style.fontSize = '1.3rem'; }
      }
    });
  }

  const currentPath = window.location.pathname;
  document.querySelectorAll('.nav-links a, .mobile-menu a').forEach(link => {
    const href = link.getAttribute('href');
    if (href === '/' && currentPath === '/') link.classList.add('active');
    else if (href !== '/' && currentPath.startsWith(href)) link.classList.add('active');
  });
}

/* ========= SCROLL TO TOP ========= */
function initScrollToTop() {
  const fab = document.querySelector('.fab-scroll');
  if (!fab) return;
  window.addEventListener('scroll', () => fab.classList.toggle('visible', window.scrollY > 400), { passive: true });
  fab.addEventListener('click', () => window.scrollTo({ top: 0, behavior: 'smooth' }));
}

/* ========= SEARCH MODAL ========= */
let searchDebounce = null;

function openSearch() {
  const overlay = document.getElementById('searchOverlay');
  if (overlay) { overlay.classList.add('open'); setTimeout(() => overlay.querySelector('input')?.focus(), 80); }
}

function closeSearch() {
  const overlay = document.getElementById('searchOverlay');
  if (overlay) overlay.classList.remove('open');
}

function initSearch() {
  const overlay = document.getElementById('searchOverlay');
  const input = document.getElementById('searchInput');
  const results = document.getElementById('searchResults');
  if (!overlay || !input || !results) return;

  overlay.addEventListener('click', (e) => { if (e.target === overlay) closeSearch(); });
  document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape') closeSearch();
    if ((e.ctrlKey || e.metaKey) && e.key === 'k') { e.preventDefault(); openSearch(); }
  });

  input.addEventListener('input', () => {
    const q = input.value.trim();
    clearTimeout(searchDebounce);
    if (q.length < 2) {
      results.innerHTML = '<div class="search-empty">Tapez au moins 2 caractères…</div>';
      return;
    }
    results.innerHTML = '<div class="search-empty">Recherche en cours…</div>';
    searchDebounce = setTimeout(async () => {
      try {
        const res = await fetch(`${API_BASE}/search/?q=${encodeURIComponent(q)}`);
        const data = await res.json();
        renderSearchResults(data.results || [], results);
      } catch { results.innerHTML = '<div class="search-empty">Une erreur est survenue.</div>'; }
    }, 280);
  });
}

function renderSearchResults(results, container) {
  const typeMap = {
    article: { icon: 'bi-journal-text', path: '/articles' },
    project: { icon: 'bi-code-square', path: '/projets' },
    tip: { icon: 'bi-lightbulb-fill', path: '/astuces' }
  };
  const typeLabel = { article: 'Article', project: 'Projet', tip: 'Astuce' };
  if (results.length === 0) { container.innerHTML = '<div class="search-empty">Aucun résultat trouvé.</div>'; return; }
  container.innerHTML = results.map(r => {
    const info = typeMap[r.type] || { icon: 'bi-file-text', path: '/' };
    return `<a href="${info.path}/${r.slug}/" class="search-result-item" onclick="closeSearch()">
      <div class="search-result-icon"><i class="bi ${info.icon}"></i></div>
      <div>
        <div class="search-result-title">${escapeHtml(r.title)}</div>
        <div class="search-result-type">${typeLabel[r.type] || r.type}</div>
      </div>
    </a>`;
  }).join('');
}

/* ========= REACTIONS — exclusives, 1 seule réaction à la fois ========= */
function initReactions() {
  const container = document.getElementById('reactionsContainer');
  if (!container) return;
  loadReactions(container.dataset.contentType, container.dataset.objectId, container);
}

async function loadReactions(contentType, objectId, container) {
  try {
    const res = await fetch(`${API_BASE}/reactions/?content_type=${contentType}&object_id=${objectId}`, {
      credentials: 'same-origin'
    });
    const data = await res.json();
    renderReactions(data, contentType, objectId, container);
  } catch (e) { console.error('Reactions error:', e); }
}

function renderReactions(data, contentType, objectId, container) {
  const reactions = [
    { type: 'like', icon: 'bi-hand-thumbs-up-fill', label: "J'aime" },
    { type: 'love', icon: 'bi-heart-fill', label: "J'adore" },
    { type: 'wow', icon: 'bi-emoji-astonished-fill', label: 'Wow' },
    { type: 'clap', icon: 'bi-hand-clapping-fill', label: 'Bravo' },
    { type: 'fire', icon: 'bi-fire', label: 'Feu' },
    { type: 'bookmark', icon: 'bi-bookmark-fill', label: 'Sauvegarder' }
  ];

  container.innerHTML = reactions.map(({ type, icon, label }) => {
    const info = (data && data[type]) ? data[type] : { count: 0, reacted: false };
    const count = info.count || 0;
    const reacted = info.reacted || false;
    return `<button class="reaction-btn ${reacted ? 'active' : ''}"
      onclick="toggleReaction('${contentType}',${objectId},'${type}',this)"
      title="${label}" data-type="${type}" aria-label="${label}">
      <i class="bi ${icon}"></i>
      <span class="reaction-count">${count > 0 ? count : ''}</span>
    </button>`;
  }).join('');
}

async function toggleReaction(contentType, objectId, reactionType, btn) {
  const container = btn.closest('.reactions-row') || btn.parentElement;
  const wasActive = btn.classList.contains('active');

  // Disable all buttons during request to prevent double-clicks
  const allBtns = container.querySelectorAll('.reaction-btn');
  allBtns.forEach(b => b.style.pointerEvents = 'none');

  // Optimistic update: exclusive — deactivate all others when activating one
  if (!wasActive) {
    allBtns.forEach(other => {
      if (other !== btn && other.classList.contains('active')) {
        other.classList.remove('active');
        const otherCount = other.querySelector('.reaction-count');
        if (otherCount) {
          const c = parseInt(otherCount.textContent) || 0;
          otherCount.textContent = c > 1 ? String(c - 1) : '';
        }
      }
    });
    btn.classList.add('active');
    const countEl = btn.querySelector('.reaction-count');
    const c = parseInt(countEl.textContent) || 0;
    countEl.textContent = String(c + 1);
  } else {
    btn.classList.remove('active');
    const countEl = btn.querySelector('.reaction-count');
    const c = parseInt(countEl.textContent) || 0;
    countEl.textContent = c > 1 ? String(c - 1) : '';
  }

  // Animate
  btn.style.transform = 'scale(1.18)';
  setTimeout(() => { btn.style.transform = ''; }, 180);

  try {
    const res = await fetch(`${API_BASE}/reactions/`, {
      method: 'POST',
      credentials: 'same-origin',
      headers: { 'Content-Type': 'application/json', 'X-CSRFToken': getCsrfToken() },
      body: JSON.stringify({ content_type: contentType, object_id: objectId, reaction_type: reactionType })
    });
    if (!res.ok) {
      // Revert on error: reload from server
      loadReactions(contentType, objectId, container);
    }
  } catch (e) {
    console.error('Reaction error:', e);
    loadReactions(contentType, objectId, container);
  } finally {
    allBtns.forEach(b => b.style.pointerEvents = '');
  }
}

/* ========= COMMENTS ========= */
const COMMENTS_INITIAL = 3;

function initComments() {
  const form = document.getElementById('commentForm');
  if (form) form.addEventListener('submit', submitComment);
  initCommentsShowMore();
}

function initCommentsShowMore() {
  const list = document.getElementById('commentsList');
  if (!list) return;
  const items = list.querySelectorAll('.comment-item-root');
  if (items.length <= COMMENTS_INITIAL) return;

  // Hide older comments (after the 3 most recent which are first)
  items.forEach((item, i) => {
    if (i >= COMMENTS_INITIAL) {
      item.style.display = 'none';
      item.dataset.hidden = '1';
    }
  });

  const hiddenCount = items.length - COMMENTS_INITIAL;
  const moreBtn = document.createElement('button');
  moreBtn.id = 'commentsMoreBtn';
  moreBtn.className = 'btn-voir-plus';
  moreBtn.innerHTML = `<i class="bi bi-chat-dots"></i> Voir plus (${hiddenCount} commentaire${hiddenCount > 1 ? 's' : ''})`;
  moreBtn.addEventListener('click', () => {
    items.forEach(item => { item.style.display = ''; delete item.dataset.hidden; });
    moreBtn.remove();
  });
  list.parentNode.insertBefore(moreBtn, list.nextSibling);
}

async function submitComment(e) {
  e.preventDefault();
  const form = e.target;
  const btn = form.querySelector('button[type="submit"]');
  const data = {
    content_type: form.dataset.contentType,
    object_id: parseInt(form.dataset.objectId),
    author_name: form.querySelector('[name="author_name"]').value.trim(),
    author_email: form.querySelector('[name="author_email"]').value.trim(),
    author_website: form.querySelector('[name="author_website"]')?.value || '',
    content: form.querySelector('[name="content"]').value.trim(),
  };
  const parentId = form.querySelector('[name="parent"]')?.value;
  if (parentId) data.parent = parseInt(parentId);

  if (!data.author_name || !data.content) return;

  const origText = btn.innerHTML;
  btn.disabled = true;
  btn.innerHTML = '<i class="bi bi-hourglass-split"></i> Envoi…';

  try {
    const res = await fetch(`${API_BASE}/comments/`, {
      method: 'POST',
      credentials: 'same-origin',
      headers: { 'Content-Type': 'application/json', 'X-CSRFToken': getCsrfToken() },
      body: JSON.stringify(data)
    });
    if (res.ok || res.status === 201) {
      form.reset();
      cancelReply();
      appendNewComment(data, parentId ? parseInt(parentId) : null);
      showToast('Commentaire envoyé ! Il sera visible après modération.', 'success');
    } else {
      throw new Error('Error');
    }
  } catch {
    showToast("Erreur lors de l'envoi. Réessayez.", 'error');
  } finally {
    btn.disabled = false;
    btn.innerHTML = origText;
  }
}

function appendNewComment(data, parentId) {
  const initial = (data.author_name || '?')[0].toUpperCase();
  const now = new Date();
  const dateStr = 'À l\'instant';

  const div = document.createElement('div');
  div.className = 'comment-item comment-item-root';
  div.innerHTML = `
    <div class="comment-avatar">${escapeHtml(initial)}</div>
    <div class="comment-body">
      <div class="comment-header">
        <span class="comment-author">${escapeHtml(data.author_name)}</span>
        <span class="comment-date">${dateStr}</span>
        <span style="font-size:0.72rem;background:#dcfce7;color:#16a34a;padding:2px 8px;border-radius:20px;font-weight:600;"><i class="bi bi-check-circle-fill"></i> Publié</span>
      </div>
      <p class="comment-text">${escapeHtml(data.content)}</p>
    </div>`;

  const list = document.getElementById('commentsList');
  if (list) {
    // Insert at top (most recent first)
    list.insertBefore(div, list.firstChild);
    // Update heading count
    const heading = document.querySelector('.comments-heading');
    if (heading) {
      const match = heading.textContent.match(/\((\d+)\)/);
      if (match) {
        heading.innerHTML = heading.innerHTML.replace(/\(\d+\)/, `(${parseInt(match[1]) + 1})`);
      } else {
        heading.innerHTML = heading.innerHTML.replace(/Commentaires/, 'Commentaires (1)');
      }
    }
    // If no comments message was showing, remove it
    const noComment = list.querySelector('.no-comments-msg');
    if (noComment) noComment.remove();
  }

  // Animate in
  div.style.opacity = '0';
  div.style.transform = 'translateY(-10px)';
  requestAnimationFrame(() => {
    div.style.transition = 'opacity 0.35s ease, transform 0.35s ease';
    div.style.opacity = '1';
    div.style.transform = 'translateY(0)';
  });
}

function setReplyTo(parentId, parentName) {
  const form = document.getElementById('commentForm');
  if (!form) return;
  const pi = form.querySelector('[name="parent"]');
  if (pi) pi.value = parentId;
  const ind = document.getElementById('replyIndicator');
  if (ind) { ind.querySelector('.reply-name').textContent = `Réponse à ${parentName}`; ind.style.display = 'inline-flex'; }
  form.querySelector('[name="content"]').focus();
  form.scrollIntoView({ behavior: 'smooth', block: 'start' });
}

function cancelReply() {
  const form = document.getElementById('commentForm');
  if (form) { const p = form.querySelector('[name="parent"]'); if (p) p.value = ''; }
  const ind = document.getElementById('replyIndicator');
  if (ind) ind.style.display = 'none';
}

/* ========= NEWSLETTER ========= */
function initNewsletter() {
  const form = document.getElementById('newsletterForm');
  if (!form) return;
  form.addEventListener('submit', async (e) => {
    e.preventDefault();
    const email = form.querySelector('[name="email"]').value;
    const btn = form.querySelector('button[type="submit"]');
    btn.disabled = true; btn.textContent = 'Inscription…';
    try {
      const res = await fetch(`${API_BASE}/newsletter/subscribe/`, {
        method: 'POST',
        credentials: 'same-origin',
        headers: { 'Content-Type': 'application/json', 'X-CSRFToken': getCsrfToken() },
        body: JSON.stringify({ email })
      });
      if (res.ok) { showToast('Inscription réussie ! Merci de votre abonnement.', 'success'); form.reset(); }
      else { const d = await res.json(); showToast(d.message || 'Erreur. Réessayez.', 'error'); }
    } catch { showToast('Erreur réseau. Réessayez.', 'error'); }
    finally { btn.disabled = false; btn.textContent = "S'abonner"; }
  });
}

/* ========= CONTACT FORM ========= */
function initContact() {
  const form = document.getElementById('contactForm');
  if (!form) return;
  form.addEventListener('submit', async (e) => {
    e.preventDefault();
    const btn = form.querySelector('button[type="submit"]');
    btn.disabled = true; const orig = btn.textContent; btn.textContent = 'Envoi…';
    const data = {
      name: form.querySelector('[name="name"]').value,
      email: form.querySelector('[name="email"]').value,
      subject: form.querySelector('[name="subject"]').value,
      message: form.querySelector('[name="message"]').value,
    };
    try {
      const res = await fetch(`${API_BASE}/contact/`, {
        method: 'POST',
        credentials: 'same-origin',
        headers: { 'Content-Type': 'application/json', 'X-CSRFToken': getCsrfToken() },
        body: JSON.stringify(data)
      });
      if (res.ok) {
        form.style.display = 'none';
        const s = document.getElementById('contactSuccess');
        if (s) s.style.display = 'block';
      } else { const d = await res.json(); showToast(d.message || 'Erreur. Réessayez.', 'error'); }
    } catch { showToast('Erreur réseau. Réessayez.', 'error'); }
    finally { btn.disabled = false; btn.textContent = orig; }
  });
}

/* ========= LIST FILTER ========= */
function initListFilter() {
  const searchInput = document.getElementById('listSearch');
  const form = document.getElementById('filterForm');
  if (!searchInput || !form) return;
  let debounce = null;
  searchInput.addEventListener('input', () => {
    clearTimeout(debounce);
    debounce = setTimeout(() => form.submit(), 500);
  });
}

/* ========= SKILL BARS ========= */
function initSkillBars() {
  const fills = document.querySelectorAll('.skill-fill');
  fills.forEach(el => { el.style.width = (el.dataset.level || '0') + '%'; });
}

/* ========= SHARE ========= */
function shareContent(title, url) {
  if (navigator.share) navigator.share({ title, url });
  else navigator.clipboard.writeText(url).then(() => showToast('Lien copié !', 'success'));
}

/* ========= STATS COUNTER ========= */
function initCounters() {
  const counters = document.querySelectorAll('.stat-number[data-count]');
  counters.forEach(el => { el.textContent = el.dataset.count || '0'; });
}

/* ========= UTILS ========= */
function getCsrfToken() {
  const meta = document.querySelector('meta[name="csrf-token"]');
  if (meta) return meta.getAttribute('content');
  const cookie = document.cookie.split(';').find(c => c.trim().startsWith('csrftoken='));
  return cookie ? cookie.trim().split('=')[1] : '';
}

function showToast(message, type = '') {
  let toast = document.getElementById('toast');
  if (!toast) { toast = document.createElement('div'); toast.id = 'toast'; toast.className = 'toast'; document.body.appendChild(toast); }
  toast.textContent = message;
  toast.className = `toast ${type} show`;
  clearTimeout(toast._timer);
  toast._timer = setTimeout(() => toast.classList.remove('show'), 3800);
}

function escapeHtml(text) {
  const div = document.createElement('div');
  div.appendChild(document.createTextNode(text || ''));
  return div.innerHTML;
}

/* ========= INIT ========= */
document.addEventListener('DOMContentLoaded', () => {
  initTheme();
  initNavbar();
  initScrollToTop();
  initSearch();
  initReactions();
  initComments();
  initNewsletter();
  initContact();
  initListFilter();
  initSkillBars();
  initCounters();
});
