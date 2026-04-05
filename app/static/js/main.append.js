/* ============================================================
   main.append.js
   이 내용을 기존 main.js 맨 아래에 붙여넣으세요.
   ============================================================ */

// ── 비밀번호 보기/숨기기 토글 ─────────────────────────────────
function initPasswordToggle() {
  document.querySelectorAll('.pw-toggle').forEach(btn => {
    btn.addEventListener('click', () => {
      const target = document.getElementById(btn.dataset.target);
      if (!target) return;
      const isText = target.type === 'text';
      target.type = isText ? 'password' : 'text';
      btn.style.opacity = isText ? '1' : '.5';
    });
  });
}

// ── 로그인 폼 유효성 ─────────────────────────────────────────
function initLoginValidation() {
  const form = document.getElementById('login-form');
  if (!form) return;

  form.addEventListener('submit', e => {
    let ok = true;

    const id  = document.getElementById('username');
    const pw  = document.getElementById('password');

    setError('err-id', '');
    setError('err-pw', '');

    if (!id?.value.trim()) {
      setError('err-id', '아이디를 입력하세요.'); ok = false;
    }
    if (!pw?.value) {
      setError('err-pw', '비밀번호를 입력하세요.'); ok = false;
    }

    if (!ok) { e.preventDefault(); return; }

    // 로딩 상태
    const btn = document.getElementById('btn-login');
    if (btn) {
      btn.querySelector('.btn-auth-text').style.display = 'none';
      btn.querySelector('.btn-auth-loader').style.display = 'inline-flex';
      btn.disabled = true;
    }
  });
}

// ── 회원가입 폼 유효성 ────────────────────────────────────────
function initSignupValidation() {
  const form = document.getElementById('signup-form');
  if (!form) return;

  // 비밀번호 강도 실시간
  const pwInput = document.getElementById('password');
  pwInput?.addEventListener('input', () => {
    const bar = document.getElementById('pw-strength-bar');
    if (!bar) return;
    const val = pwInput.value;
    let score = 0;
    if (val.length >= 8) score++;
    if (/[A-Z]/.test(val)) score++;
    if (/[0-9]/.test(val)) score++;
    if (/[^A-Za-z0-9]/.test(val)) score++;
    bar.className = 'pw-strength-bar s' + Math.max(score, val.length ? 1 : 0);
  });

  // 비밀번호 확인 실시간
  const pw2Input = document.getElementById('password2');
  pw2Input?.addEventListener('input', () => {
    const status = document.getElementById('pw2-status');
    if (!status) return;
    if (!pw2Input.value) { status.textContent = ''; return; }
    if (pw2Input.value === pwInput?.value) {
      status.textContent = '✓'; status.className = 'input-status ok';
      pw2Input.classList.add('input-ok');
      pw2Input.classList.remove('input-error');
    } else {
      status.textContent = '✗'; status.className = 'input-status err';
      pw2Input.classList.add('input-error');
      pw2Input.classList.remove('input-ok');
    }
  });

  form.addEventListener('submit', e => {
    let ok = true;
    ['err-uname','err-id','err-pw','err-pw2'].forEach(id => setError(id, ''));

    const uname = document.getElementById('username_display');
    const uid   = document.getElementById('username');
    const pw    = document.getElementById('password');
    const pw2   = document.getElementById('password2');

    if (!uname?.value.trim()) {
      setError('err-uname', '사용자 이름을 입력하세요.'); ok = false;
    }
    if (!uid?.value.trim() || !/^[a-zA-Z0-9_]{4,20}$/.test(uid.value)) {
      setError('err-id', '영문, 숫자, _ 4~20자로 입력하세요.'); ok = false;
    }
    if (!pw?.value || pw.value.length < 8) {
      setError('err-pw', '8자 이상 입력하세요.'); ok = false;
    }
    if (pw?.value !== pw2?.value) {
      setError('err-pw2', '비밀번호가 일치하지 않습니다.'); ok = false;
    }

    if (!ok) { e.preventDefault(); return; }

    const btn = document.getElementById('btn-signup');
    if (btn) {
      btn.querySelector('.btn-auth-text').style.display = 'none';
      btn.querySelector('.btn-auth-loader').style.display = 'inline-flex';
      btn.disabled = true;
    }
  });
}

// ── 아바타 업로드 ─────────────────────────────────────────────
function initAvatarUpload() {
  const zone    = document.getElementById('avatar-upload');
  const input   = document.getElementById('profile-image');
  const preview = document.getElementById('avatar-preview');
  if (!zone || !input || !preview) return;

  zone.addEventListener('click', () => input.click());

  input.addEventListener('change', () => {
    const file = input.files?.[0];
    if (file) handleAvatarFile(file, preview);
  });

  zone.addEventListener('dragover', e => {
    e.preventDefault();
    zone.classList.add('drag-over');
  });
  zone.addEventListener('dragleave', () => zone.classList.remove('drag-over'));
  zone.addEventListener('drop', e => {
    e.preventDefault();
    zone.classList.remove('drag-over');
    const file = e.dataTransfer.files?.[0];
    if (file && file.type.startsWith('image/')) {
      handleAvatarFile(file, preview);
    }
  });
}

function handleAvatarFile(file, preview) {
  if (file.size > 2 * 1024 * 1024) {
    setError('err-img', '파일 크기는 2MB 이하여야 합니다.');
    return;
  }
  setError('err-img', '');
  const reader = new FileReader();
  reader.onload = e => {
    preview.innerHTML = `<img src="${e.target.result}" alt="미리보기" style="width:100%;height:100%;object-fit:cover;border-radius:8px;"/>`;
  };
  reader.readAsDataURL(file);
}

// ── 포스트 폼 ─────────────────────────────────────────────────
function initPostForm() {
  // 제목 글자 수
  const titleInput = document.getElementById('pf-title');
  const titleCount = document.getElementById('title-count');
  titleInput?.addEventListener('input', () => {
    if (titleCount) titleCount.textContent = `${titleInput.value.length} / 120`;
    // 미리보기 업데이트
    const prev = document.getElementById('preview-title');
    if (prev) prev.textContent = titleInput.value || '제목 미리보기';
  });
  if (titleInput && titleCount) {
    titleCount.textContent = `${titleInput.value.length} / 120`;
  }

  // 본문 글자 수
  const textarea  = document.getElementById('pf-content');
  const wordCount = document.getElementById('word-count');
  textarea?.addEventListener('input', () => {
    if (wordCount) wordCount.textContent = `${textarea.value.length}자`;
    updatePreview(textarea.value);
  });
  if (textarea && wordCount) wordCount.textContent = `${textarea.value.length}자`;

  // 미리보기 토글
  const previewBtn   = document.getElementById('preview-toggle');
  const editorPanel  = document.getElementById('editor-panel');
  const previewPanel = document.getElementById('preview-panel');
  let previewOn = false;

  previewBtn?.addEventListener('click', () => {
    previewOn = !previewOn;
    if (previewPanel) previewPanel.style.display = previewOn ? 'flex' : 'none';
    previewBtn.style.color = previewOn ? 'var(--accent)' : '';
    if (previewOn) updatePreview(textarea?.value || '');
  });

  // 공개 토글 라벨
  const visToggle = document.querySelector('[name="is_public"]');
  const visLabel  = document.getElementById('visibility-label');
  visToggle?.addEventListener('change', () => {
    if (visLabel) visLabel.textContent = visToggle.checked ? '공개' : '비공개';
  });

  // Markdown 툴바 버튼
  document.querySelectorAll('.tb-fmt').forEach(btn => {
    btn.addEventListener('click', () => {
      if (!textarea) return;
      const fmt      = btn.dataset.fmt;
      const fmtBlock = btn.dataset.fmtBlock;
      const start    = textarea.selectionStart;
      const end      = textarea.selectionEnd;
      const sel      = textarea.value.substring(start, end);

      let insert = '';
      if (fmt) {
        insert = sel ? `${fmt}${sel}${fmt}` : `${fmt}텍스트${fmt}`;
      } else if (fmtBlock) {
        insert = fmtBlock === '```\n'
          ? `\`\`\`\n${sel || '코드를 입력하세요'}\n\`\`\``
          : `${fmtBlock}${sel || '내용'}`;
      }

      textarea.value = textarea.value.substring(0, start) + insert + textarea.value.substring(end);
      textarea.focus();
      textarea.selectionStart = start + insert.length;
      textarea.selectionEnd   = start + insert.length;
      if (wordCount) wordCount.textContent = `${textarea.value.length}자`;
    });
  });

  // Ctrl+S 저장
  document.addEventListener('keydown', e => {
    if ((e.ctrlKey || e.metaKey) && e.key === 's') {
      e.preventDefault();
      document.getElementById('post-form')?.requestSubmit();
    }
  });
}

// 간단 Markdown → HTML (미리보기용 — 실 서비스는 서버사이드 파서 사용 권장)
function updatePreview(md) {
  const el = document.getElementById('preview-body');
  if (!el) return;
  let html = md
    .replace(/^### (.+)$/gm, '<h3>$1</h3>')
    .replace(/^## (.+)$/gm,  '<h2>$1</h2>')
    .replace(/^# (.+)$/gm,   '<h1>$1</h1>')
    .replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>')
    .replace(/\*(.+?)\*/g,     '<em>$1</em>')
    .replace(/`(.+?)`/g,       '<code style="background:var(--surface2);padding:.1em .35em;border-radius:3px;font-size:.85em">$1</code>')
    .replace(/^- (.+)$/gm,    '<li>$1</li>')
    .replace(/(<li>.*<\/li>)/gs, '<ul>$1</ul>')
    .replace(/\n\n/g, '</p><p>')
    .replace(/\n/g, '<br/>');
  el.innerHTML = `<p>${html}</p>`;
}

// ── 썸네일 업로드 ─────────────────────────────────────────────
function initThumbnailUpload() {
  const btn     = document.getElementById('thumb-btn');
  const input   = document.getElementById('thumb-file');
  const preview = document.getElementById('thumb-preview');
  const remove  = document.getElementById('thumb-remove');
  if (!btn || !input) return;

  btn.addEventListener('click', () => input.click());

  input.addEventListener('change', () => {
    const file = input.files?.[0];
    if (!file) return;
    const reader = new FileReader();
    reader.onload = e => {
      if (preview) {
        preview.innerHTML = `<img id="thumb-img" src="${e.target.result}" alt="썸네일" style="width:100%;height:100%;object-fit:cover;"/>`;
        btn.textContent = '이미지 변경';
      }
    };
    reader.readAsDataURL(file);
  });

  remove?.addEventListener('click', () => {
    if (preview) {
      preview.innerHTML = `
        <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.2" opacity=".3"><rect x="3" y="3" width="18" height="18" rx="2"/><circle cx="8.5" cy="8.5" r="1.5"/><path d="M21 15l-5-5L5 21"/></svg>
        <span class="pf-thumb-hint">썸네일 이미지 업로드</span>`;
    }
    input.value = '';
    btn.textContent = '이미지 추가';
    remove.style.display = 'none';
  });
}

// ── 대시보드 삭제 확인 모달 ───────────────────────────────────
function confirmDelete(btn) {
  const id    = btn.dataset.id;
  const title = btn.dataset.title;
  const overlay = document.getElementById('modal-overlay');
  const body    = document.getElementById('modal-body');
  const confirm = document.getElementById('modal-confirm');
  if (!overlay) return;

  if (body) body.textContent = `"${title}"을(를) 삭제하면 복구할 수 없습니다.`;
  overlay.style.display = 'flex';

  // 확인 버튼 — 실제로는 DELETE fetch 또는 form submit
  if (confirm) {
    confirm.onclick = () => {
      // FastAPI 연동 예시:
      // fetch(`/post/${id}`, { method: 'DELETE' }).then(() => location.reload());
      alert(`ID ${id} 삭제 (FastAPI 연동 필요)`);
      closeModal();
    };
  }
}

function closeModal() {
  const overlay = document.getElementById('modal-overlay');
  if (overlay) overlay.style.display = 'none';
}

// 모달 외부 클릭 시 닫기
document.addEventListener('click', e => {
  const overlay = document.getElementById('modal-overlay');
  if (e.target === overlay) closeModal();
});

// ── 공통 에러 표시 헬퍼 ──────────────────────────────────────
function setError(id, msg) {
  const el = document.getElementById(id);
  if (!el) return;
  el.textContent = msg;
  el.style.opacity = msg ? '1' : '0';

  // 부모 input에도 클래스 적용
  const wrap = el.closest('.form-group');
  const input = wrap?.querySelector('.form-input');
  if (input) {
    input.classList.toggle('input-error', !!msg);
    if (!msg) input.classList.remove('input-error');
  }
}
