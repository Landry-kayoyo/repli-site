import { useState, useEffect } from 'react';
import { getComments, postComment } from '../../lib/api';
import { formatDate } from '../../lib/utils';
import { FiMessageCircle, FiSend, FiCornerDownRight } from 'react-icons/fi';
import { motion } from 'framer-motion';

function CommentForm({ onSubmit, loading, parentId = null, onCancel = null }) {
  const [form, setForm] = useState({ author_name: '', author_email: '', author_website: '', content: '', parent: parentId });
  const handleChange = e => setForm(p => ({ ...p, [e.target.name]: e.target.value }));
  const handleSubmit = e => { e.preventDefault(); onSubmit(form); };

  return (
    <form onSubmit={handleSubmit} className="space-y-3">
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
        <input name="author_name" value={form.author_name} onChange={handleChange} required placeholder="Votre nom *" className="input-field" />
        <input name="author_email" type="email" value={form.author_email} onChange={handleChange} required placeholder="Votre email *" className="input-field" />
      </div>
      <input name="author_website" value={form.author_website} onChange={handleChange} placeholder="Votre site web (optionnel)" className="input-field" />
      <textarea name="content" value={form.content} onChange={handleChange} required rows={4} placeholder="Votre commentaire *" className="input-field resize-none" />
      <div className="flex gap-3">
        <button type="submit" disabled={loading} className="btn-primary">
          <FiSend size={16} />{loading ? 'Envoi...' : 'Publier'}
        </button>
        {onCancel && <button type="button" onClick={onCancel} className="btn-secondary">Annuler</button>}
      </div>
    </form>
  );
}

function CommentItem({ comment, onReply, depth = 0 }) {
  const [showReply, setShowReply] = useState(false);
  const [loading, setLoading] = useState(false);
  const [success, setSuccess] = useState(false);

  const handleReply = async (form) => {
    setLoading(true);
    await onReply({ ...form, parent: comment.id });
    setLoading(false); setSuccess(true); setShowReply(false);
  };

  return (
    <div className={`${depth > 0 ? 'ml-8 border-l-2 border-gray-100 dark:border-gray-800 pl-6' : ''}`}>
      <div className="flex gap-4">
        <div className="w-10 h-10 rounded-full bg-gradient-to-br from-primary-400 to-purple-500 flex items-center justify-center text-white font-bold text-sm flex-shrink-0">
          {comment.author_name[0].toUpperCase()}
        </div>
        <div className="flex-1">
          <div className="flex items-center gap-2 mb-1">
            <span className="font-semibold text-gray-900 dark:text-white text-sm">{comment.author_name}</span>
            <span className="text-gray-400 text-xs">{formatDate(comment.created_at)}</span>
          </div>
          <p className="text-gray-700 dark:text-gray-300 text-sm leading-relaxed whitespace-pre-wrap">{comment.content}</p>
          {depth === 0 && (
            <button onClick={() => setShowReply(!showReply)} className="flex items-center gap-1.5 text-xs text-gray-400 hover:text-primary-600 mt-2 transition-colors">
              <FiCornerDownRight size={12} />Répondre
            </button>
          )}
          {showReply && (
            <div className="mt-4">
              <CommentForm onSubmit={handleReply} loading={loading} parentId={comment.id} onCancel={() => setShowReply(false)} />
            </div>
          )}
        </div>
      </div>
      {comment.replies?.map(reply => (
        <div key={reply.id} className="mt-4"><CommentItem comment={reply} onReply={onReply} depth={depth + 1} /></div>
      ))}
    </div>
  );
}

export default function Comments({ contentType, objectId }) {
  const [comments, setComments] = useState([]);
  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [success, setSuccess] = useState(false);

  const loadComments = async () => {
    try {
      const res = await getComments(contentType, objectId);
      setComments(res.data);
    } catch {} finally { setLoading(false); }
  };

  useEffect(() => { if (contentType && objectId) loadComments(); }, [contentType, objectId]);

  const handleSubmit = async (form) => {
    setSubmitting(true);
    try {
      await postComment({ ...form, content_type: contentType, object_id: objectId });
      setSuccess(true);
    } catch {} finally { setSubmitting(false); }
  };

  return (
    <section className="mt-12">
      <h3 className="text-2xl font-bold text-gray-900 dark:text-white mb-8 flex items-center gap-2">
        <FiMessageCircle className="text-primary-500" />{comments.length} Commentaire{comments.length !== 1 ? 's' : ''}
      </h3>

      {loading ? <p className="text-gray-400">Chargement...</p> : (
        <div className="space-y-6 mb-10">
          {comments.map(c => (
            <CommentItem key={c.id} comment={c} onReply={handleSubmit} />
          ))}
          {comments.length === 0 && <p className="text-gray-400 text-center py-8">Soyez le premier à commenter !</p>}
        </div>
      )}

      <div className="card p-6">
        <h4 className="font-bold text-gray-900 dark:text-white text-lg mb-6">Laisser un commentaire</h4>
        {success ? (
          <div className="text-green-600 dark:text-green-400 bg-green-50 dark:bg-green-950/30 rounded-xl p-4 text-center">
            ✓ Votre commentaire a été soumis et est en attente de modération.
          </div>
        ) : (
          <CommentForm onSubmit={handleSubmit} loading={submitting} />
        )}
      </div>
    </section>
  );
}
