const COLORS = ['#4fffb0','#ff6b6b','#ffd166','#a78bfa','#38bdf8','#fb923c','#f472b6'];
let me = 'You';
let friends = [];
let activeFriend = null;
let colorMap = {};
let profilePics = {};
let msgCount = 0;

// ── Helpers ──────────────────────────────────────────────
function col(name) {
  if (!colorMap[name]) {
    colorMap[name] = COLORS[Object.keys(colorMap).length % COLORS.length];
  }
  return colorMap[name];
}

function init(name) {
  return name.split(' ').map(w => w[0]).join('').toUpperCase().slice(0, 2);
}

function esc(s) {
  return s.replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;');
}

function box() {
  return document.getElementById('messages');
}

function getProfilePicUrl(name) {
  // For now, we'll use initials in colored circles
  // To use actual profile pictures, we'd need to integrate with the backend database
  return null;
}

// ── Friends ───────────────────────────────────────────────
function renderFriends() {
  const list = document.getElementById('friend-list');
  list.innerHTML = '';
  friends.forEach((f, i) => {
    const d = document.createElement('div');
    d.className = 'friend' + (activeFriend === i ? ' active' : '');
    d.onclick = () => { activeFriend = i; renderFriends(); };
    d.innerHTML = `<div class="av" style="background:${col(f)}">${init(f)}</div>${f}`;
    list.appendChild(d);
  });
}

function openModal() {
  document.getElementById('add-modal').classList.add('open');
  document.getElementById('fn').focus();
}

function closeModal() {
  document.getElementById('add-modal').classList.remove('open');
  document.getElementById('fn').value = '';
}

function addFriend() {
  const v = document.getElementById('fn').value.trim();
  if (!v) return;
  friends.push(v);
  col(v);
  closeModal();
  renderFriends();
  sys(v + ' added');
  console.log("Friends list:", friends);
  console.log("Rendered friends HTML:", document.getElementById('friend-list').innerHTML);
}

document.getElementById('fn').addEventListener('keydown', e => {
  if (e.key === 'Enter') addFriend();
});

// ── Messages ──────────────────────────────────────────────
function sys(text) {
  const d = document.createElement('div');
  d.className = 'sys';
  d.textContent = '— ' + text + ' —';
  box().appendChild(d);
  box().scrollTop = box().scrollHeight;
}

function bubble(sender, text, isMe) {
  const row = document.createElement('div');
  row.className = 'row ' + (isMe ? 'me' : 'them');
  row.innerHTML = `
    <div class="msg-av" style="background:${col(sender)}">${init(sender)}</div>
    <div class="bubble ${isMe ? 'me' : 'them'}">
      ${!isMe ? `<div class="who">${sender}</div>` : ''}
      ${esc(text)}
    </div>`;
  box().appendChild(row);
  box().scrollTop = box().scrollHeight;
}

function send() {
  const inp = document.getElementById('msg-input');
  const txt = inp.value.trim();
  if (!txt) return;

  bubble(me, txt, true);
  inp.value = '';
  inp.style.height = 'auto';

  if (activeFriend !== null) {
    const f = friends[activeFriend];
    const replies = [
      'Got it!', '👍', 'Sure!', 'Interesting…',
      'Tell me more!', 'haha 😄', 'On it!', '💯', 'Noted!', 'Makes sense'
    ];
    const reply = replies[Math.floor(Math.random() * replies.length)];
    setTimeout(() => bubble(f, reply, false), 700 + Math.random() * 600);
  }
}

// ── Input events ──────────────────────────────────────────
document.getElementById('msg-input').addEventListener('keydown', e => {
  if (e.key === 'Enter' && !e.shiftKey) {
    e.preventDefault();
    send();
  }
});

document.getElementById('msg-input').addEventListener('input', function() {
  this.style.height = 'auto';
  this.style.height = Math.min(this.scrollHeight, 90) + 'px';
});
