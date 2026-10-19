// YousefTube front-end: newsletter forms and the Yousef Wall.
(function () {
  function toast(msg) {
    var t = document.getElementById('toast');
    if (!t) { t = document.createElement('div'); t.id = 'toast'; t.className = 'toast'; document.body.appendChild(t); }
    t.textContent = msg; t.hidden = false; clearTimeout(t._h); t._h = setTimeout(function () { t.hidden = true; }, 3200);
  }
  window.ytToast = toast;
  function post(url, data) {
    return fetch(url, { method: 'POST', headers: { 'content-type': 'application/json' }, body: JSON.stringify(data) })
      .then(function (r) { return r.json().catch(function () { return {}; }).then(function (j) { j._ok = r.ok; return j; }); });
  }
  var esc = function (t) { return String(t == null ? '' : t).replace(/[&<>"]/g, function (c) { return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]; }); };

  // Newsletter: any form with class "signup"
  document.querySelectorAll('form.signup').forEach(function (f) {
    f.addEventListener('submit', function (e) {
      e.preventDefault();
      var input = f.querySelector('input[type=email]'), hp = f.querySelector('input[name=website]');
      var btn = f.querySelector('button[type=submit]'); var email = input.value.trim();
      if (!/^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/.test(email)) { toast('Enter an email address like you@example.com'); input.focus(); return; }
      btn.disabled = true;
      post('/api/subscribe', { email: email, website: hp ? hp.value : '', source: f.dataset.source || location.pathname })
        .then(function (j) { if (j._ok) { f.reset(); toast("You're in. The Yousef Report lands Fridays."); } else toast(j.error || 'Something went wrong. Please try again.'); })
        .catch(function () { toast('Network hiccup. Please try again.'); })
        .finally(function () { btn.disabled = false; });
    });
  });

  // Wall
  var KIND = { checkin: ['Check-in', '👋'], appreciation: ['Appreciation', '💛'], message: ['To a Yousef', '✉️'] };
  function ago(iso) {
    var s = (Date.now() - new Date(iso).getTime()) / 1000;
    if (s < 60) return 'just now'; if (s < 3600) return Math.floor(s / 60) + 'm ago';
    if (s < 86400) return Math.floor(s / 3600) + 'h ago'; if (s < 2592000) return Math.floor(s / 86400) + 'd ago';
    return new Date(iso).toLocaleDateString(undefined, { month: 'short', day: 'numeric', year: 'numeric' });
  }
  var saluted = {};
  try { saluted = JSON.parse(localStorage.getItem('yt-saluted') || '{}'); } catch (e) {}
  function card(m) {
    var k = KIND[m.kind] || KIND.checkin;
    return '<article class="note-card k-' + esc(m.kind) + '" data-id="' + m.id + '">' +
      '<div class="note-top"><span class="pill">' + k[1] + ' ' + k[0] + '</span><span class="note-when">' + ago(m.created) + '</span></div>' +
      '<p class="note-body">' + esc(m.body) + '</p>' +
      '<div class="note-foot"><span class="note-who">— ' + esc(m.name) + (m.place ? ', ' + esc(m.place) : '') + '</span>' +
      '<button type="button" class="salute' + (saluted[m.id] ? ' on' : '') + '" aria-label="Salute this post">🙌 <span>' + (m.salutes || 0) + '</span></button></div></article>';
  }
  var list = document.getElementById('wall-list');
  if (list) {
    var limit = parseInt(list.dataset.limit) || 50;
    fetch('/api/wall?limit=' + limit, { cache: 'no-store' }).then(function (r) { return r.json(); }).then(function (d) {
      var c = document.getElementById('wall-count'); if (c && d.total != null) c.textContent = d.total.toLocaleString();
      if (!d.messages || !d.messages.length) return; // keep the designed empty state
      list.innerHTML = d.messages.map(card).join('');
    }).catch(function () {});
    list.addEventListener('click', function (e) {
      var b = e.target.closest('.salute'); if (!b) return;
      var id = b.closest('.note-card').dataset.id; if (saluted[id]) { toast('Already saluted. Your enthusiasm is noted.'); return; }
      saluted[id] = 1; try { localStorage.setItem('yt-saluted', JSON.stringify(saluted)); } catch (e2) {}
      b.classList.add('on'); var n = b.querySelector('span'); n.textContent = (parseInt(n.textContent) || 0) + 1;
      post('/api/salute', { id: id }).then(function (j) { if (j._ok && j.salutes != null) n.textContent = j.salutes; });
    });
  }
  var wf = document.getElementById('wall-form');
  if (wf) {
    var body = wf.querySelector('#wall-body'), cnt = wf.querySelector('#wall-chars');
    if (body && cnt) body.addEventListener('input', function () { cnt.textContent = body.value.length + ' / 280'; });
    wf.addEventListener('submit', function (e) {
      e.preventDefault();
      var btn = wf.querySelector('button[type=submit]');
      var data = { name: wf.querySelector('#wall-name').value, place: wf.querySelector('#wall-place').value,
        kind: (wf.querySelector('input[name=kind]:checked') || {}).value || 'checkin', body: body.value,
        website: wf.querySelector('input[name=website]').value };
      if (!data.name.trim()) { toast('Add a name (first name is fine).'); return; }
      if (data.body.trim().length < 3) { toast('Write a few words for the wall.'); return; }
      btn.disabled = true;
      post('/api/wall', data).then(function (j) {
        if (!j._ok) { toast(j.error || 'Something went wrong. Please try again.'); return; }
        if (j.message && list) { var empty = list.querySelector('.wall-empty'); if (empty) list.innerHTML = ''; list.insertAdjacentHTML('afterbegin', card(j.message)); }
        var c = document.getElementById('wall-count'); if (c) c.textContent = ((parseInt(c.textContent.replace(/\D/g, '')) || 0) + 1).toLocaleString();
        body.value = ''; if (cnt) cnt.textContent = '0 / 280'; toast('Posted to the Yousef Wall.');
      }).catch(function () { toast('Network hiccup. Please try again.'); }).finally(function () { btn.disabled = false; });
    });
  }
})();
