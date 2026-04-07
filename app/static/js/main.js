/* ============================================================
   main.js  —  DevLog 인터랙션 & 데이터 렌더링
   FastAPI 연동 시: DATA 객체 값들을 Jinja2 context로 교체하면 됩니다.
   예) const posts = {{ posts | tojson }};
   ============================================================ */

// ── 샘플 데이터 (FastAPI에서 Jinja2로 교체 예정) ─────────────


// ── 유틸 ─────────────────────────────────────────────────────
function qs(sel) { return document.querySelector(sel); }
function qsa(sel) { return document.querySelectorAll(sel); }

// ── 포스트 카드 렌더 ─────────────────────────────────────────
function renderPostCards(posts) {
  const grid = qs('#posts-grid');
  if (!grid) return;
  grid.innerHTML = posts.map(p => `
    <div class="card-item" onclick="window.location.href='${p.url}'">
      <div class="card-cat cat-${p.cat}">${p.catLabel}</div>
      <div class="card-title">${p.title}</div>
      <div class="card-body">${p.body}</div>
      <div class="card-date">${p.date}</div>
    </div>
  `).join('');
}

// ── 프로젝트 카드 렌더 ───────────────────────────────────────
function renderProjectCards(projects) {
  const grid = qs('#projects-grid');
  if (!grid) return;
  grid.innerHTML = projects.map(p => `
    <div class="project-card" onclick="window.location.href='${p.url}'">
      <div class="project-thumb" style="background:${p.bg}">
        <span style="font-size:2.2rem;position:relative;z-index:1">${p.emoji}</span>
      </div>
      <div class="project-info">
        <div class="project-name">
          ${p.name} <span class="project-star">★</span>
        </div>
        <div class="project-genre">
          ${p.tags.map(t => `<span class="genre-tag">${t}</span>`).join('')}
          <span class="platform-icons">${p.platforms.join('')}</span>
        </div>
      </div>
    </div>
  `).join('');
}

// ── 전체 포스트 리스트 렌더 ──────────────────────────────────
function renderAllPosts(posts) {
  const existing = qs('#posts-full-list');
  if (existing) return; // 이미 있으면 패스

  const section = qs('#section-home');
  const view = document.createElement('div');
  view.id = 'posts-full-list';
  view.innerHTML = `
    <div class="page-heading">모든 포스트</div>
    <div class="post-list-full">
      ${posts.map(p => `
        <a href="${p.url}" class="post-list-item">
          <span class="pli-date">${p.date}</span>
          <span class="pli-title">${p.title}</span>
          <span class="pli-tag">${p.tag}</span>
        </a>
      `).join('')}
    </div>
  `;
  section.after(view);
}

// ── 페이지 전환 ──────────────────────────────────────────────
const HOME_SECTIONS = ['#hero', '#section-home', '.section-title-bar', '#section-projects-preview'];
const PAGE_SUBTITLE_MAP = { home: '홈', posts: '포스트', projects: '프로젝트' };

let currentPage = 'home';
let postsExpanded = false;

function showPage(page) {
  currentPage = page;
  qs('#page-subtitle').textContent = PAGE_SUBTITLE_MAP[page] || page;

  // 사이드바 active
  qsa('.snav-item').forEach(btn => {
    btn.classList.toggle('active', btn.dataset.page === page);
  });

  const content = qs('.content-area');

  // 홈 요소 표시/숨김
  HOME_SECTIONS.forEach(sel => {
    const el = qs(sel);
    if (el) el.style.display = page === 'home' ? '' : 'none';
  });

  // 포스트 페이지
  let postsView = qs('#page-posts');
  if (!postsView && page === 'posts') {
    postsView = document.createElement('div');
    postsView.id = 'page-posts';
    postsView.className = 'page-view';
    postsView.innerHTML = `
    <div style="display:flex; align-items:center; justify-content:space-between; gap:1rem; margin-bottom:1.2rem;">
      <div class="page-heading" style="margin-bottom:0; border-bottom:none; padding-bottom:0;">포스트</div>
      ${window.IS_MGR ? `<a href="/post/new" class="btn-login" style="text-decoration:none;">+ 글쓰기</a>` : ``}
    </div>
    <div class="post-list-full">
      ${(window.ALL_POSTS_DATA || []).map(p => `
        <a href="${p.url}" class="post-list-item">
          <span class="pli-date">${p.date}</span>
          <span class="pli-title">${p.title}</span>
          <span class="pli-tag">${p.tag}</span>
        </a>
      `).join('')}
    </div>
  `;
    content.appendChild(postsView);
  }
  if (postsView) postsView.classList.toggle('active', page === 'posts');

  // 프로젝트 페이지
  let projView = qs('#page-projects');
  if (!projView && page === 'projects') {
    projView = document.createElement('div');
    projView.id = 'page-projects';
    projView.className = 'page-view';
    projView.innerHTML = `
  <div style="display:flex; align-items:center; justify-content:space-between; gap:1rem; margin-bottom:1.2rem;">
    <div class="page-heading" style="margin-bottom:0; border-bottom:none; padding-bottom:0;">프로젝트</div>
    ${window.IS_MGR ? `<a href="/project/new" class="btn-login" style="text-decoration:none;">+ 새 프로젝트</a>` : ``}
  </div>
  <div class="project-grid">
    ${(window.PROJECTS_DATA || []).map(p => `
      <div class="project-card" onclick="window.location.href='${p.url}'">
        <div class="project-thumb" style="background:${p.bg}">
          <span style="font-size:2.2rem;position:relative;z-index:1">${p.emoji}</span>
        </div>
        <div class="project-info">
          <div class="project-name">${p.name} <span class="project-star">★</span></div>
          <div class="project-genre">
            ${p.tags.map(t => `<span class="genre-tag">${t}</span>`).join('')}
            <span class="platform-icons">${p.platforms.join('')}</span>
          </div>
        </div>
      </div>
    `).join('')}
  </div>
`;
    content.appendChild(projView);
  }
  if (projView) projView.classList.toggle('active', page === 'projects');

  // 스크롤 맨 위로
  content.scrollTop = 0;
}

// ── 사이드바 메뉴 클릭 ───────────────────────────────────────
function initSidebarNav() {
  qsa('.snav-item').forEach(btn => {
    btn.addEventListener('click', () => showPage(btn.dataset.page));
  });
}

// ── "더 보기" 버튼 ───────────────────────────────────────────
function initMoreBtn() {
  const btn = qs('#more-posts');
  if (!btn) return;
  btn.addEventListener('click', () => {
    if (!postsExpanded) {
      renderAllPosts(DATA.allPosts);
      btn.textContent = '접기 ↑';
      postsExpanded = true;
    } else {
      const el = qs('#posts-full-list');
      if (el) el.remove();
      btn.textContent = '더 보기 →';
      postsExpanded = false;
    }
  });
}

// ── macOS 신호등 버튼 ────────────────────────────────────────
function initTrafficLights() {
  qs('.tl-close')?.addEventListener('click', () => {
    const win = qs('.macos-window');
    win.style.transition = 'opacity .2s, transform .2s';
    win.style.opacity = '0';
    win.style.transform = 'scale(.96)';
    setTimeout(() => {
      win.style.opacity = '1';
      win.style.transform = 'scale(1)';
    }, 500);
  });

  qs('.tl-min')?.addEventListener('click', () => {
    const win = qs('.macos-window');
    win.style.transition = 'transform .25s, opacity .25s';
    win.style.transform = 'scaleY(0.02) translateY(100px)';
    win.style.opacity = '0';
    setTimeout(() => {
      win.style.transform = '';
      win.style.opacity = '';
    }, 600);
  });

  qs('.tl-max')?.addEventListener('click', () => {
    const win = qs('.macos-window');
    win.classList.toggle('fullscreen');
    if (win.classList.contains('fullscreen')) {
      win.style.cssText = 'max-width:100%;border-radius:0;position:fixed;inset:0;z-index:9999;';
      qs('.app-shell').style.height = '100vh';
    } else {
      win.style.cssText = '';
      qs('.app-shell').style.height = '';
    }
  });
}

// ── 로그인 버튼 토글 ─────────────────────────────────────────
function initLoginBtn() {
  const btn = qs('#login-btn');
  let loggedIn = false;
  btn?.addEventListener('click', () => {
    loggedIn = !loggedIn;
    btn.innerHTML = loggedIn
      ? `<svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="8" r="4"/><path d="M4 20c0-4 3.6-7 8-7s8 3 8 7"/></svg> YN`
      : `<svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="8" r="4"/><path d="M4 20c0-4 3.6-7 8-7s8 3 8 7"/></svg> 로그인`;
    btn.style.color = loggedIn ? 'var(--accent)' : '';
  });
}

// ── 카드 호버 인터랙션 (이벤트 위임) ─────────────────────────
function initCardHover() {
  document.addEventListener('mousemove', e => {
    const card = e.target.closest('.project-card');
    if (!card) return;
    const rect = card.getBoundingClientRect();
    const x = ((e.clientX - rect.left) / rect.width  - .5) * 8;
    const y = ((e.clientY - rect.top)  / rect.height - .5) * 8;
    card.style.transform = `translateY(-2px) perspective(600px) rotateX(${-y}deg) rotateY(${x}deg)`;
  });
  document.addEventListener('mouseleave', e => {
    const card = e.target.closest?.('.project-card');
    if (card) card.style.transform = '';
  }, true);
}

// ── 스크롤 reveal (간단) ─────────────────────────────────────
function initScrollReveal() {
  const targets = qsa('.card-item, .project-card');
  const obs = new IntersectionObserver(entries => {
    entries.forEach((e, i) => {
      if (e.isIntersecting) {
        setTimeout(() => {
          e.target.style.opacity = '1';
          e.target.style.transform = 'translateY(0)';
        }, i * 40);
        obs.unobserve(e.target);
      }
    });
  }, { threshold: .05 });

  targets.forEach(el => {
    el.style.opacity = '0';
    el.style.transform = 'translateY(12px)';
    el.style.transition = 'opacity .35s ease, transform .35s ease';
    obs.observe(el);
  });
}

// ── 초기화 ───────────────────────────────────────────────────
document.addEventListener('DOMContentLoaded', () => {
  renderPostCards(window.POSTS_DATA);
  renderProjectCards(window.PROJECTS_DATA || []);

  initSidebarNav();
  initMoreBtn();
  initTrafficLights();
  initLoginBtn();
  initCardHover();

  // 살짝 딜레이 후 scroll reveal 초기화 (렌더 완료 후)
  setTimeout(initScrollReveal, 80);
});
