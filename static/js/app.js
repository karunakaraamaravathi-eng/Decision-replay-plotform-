const API_BASE = '/api';

// State management
let state = {
  token: localStorage.getItem('token') || null,
  user: JSON.parse(localStorage.getItem('user')) || null,
  roles: ['Employee', 'Reviewer', 'Manager', 'Administrator'],
  activeTab: 'decisions-tab',
  activeDecisionId: null,
  allDecisions: []
};

// Initialize App
document.addEventListener('DOMContentLoaded', () => {
  setupEventListeners();
  checkAuth();
  loadWireframeSpecs();
  loadDecisions();
});

// Setup DOM Event Listeners
function setupEventListeners() {
  // Navigation Tabs
  document.querySelectorAll('.tab-btn').forEach(btn => {
    btn.addEventListener('click', (e) => {
      document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
      document.querySelectorAll('.tab-content').forEach(c => c.style.display = 'none');

      const tabId = e.target.getAttribute('data-tab');
      e.target.classList.add('active');
      const contentEl = document.getElementById(tabId);
      if (contentEl) contentEl.style.display = 'block';

      if (tabId === 'decisions-tab') loadDecisions();
      if (tabId === 'users-tab') loadUsers();
      if (tabId === 'audit-tab') loadAuditLogs();
      if (tabId === 'dashboard-tab') loadDashboardStats();
      if (tabId === 'db-tab') loadLiveDatabase();
    });
  });

  // Auth Modal Buttons
  document.getElementById('open-login-btn')?.addEventListener('click', () => showAuthModal('login'));
  document.getElementById('open-register-btn')?.addEventListener('click', () => showAuthModal('register'));
  document.getElementById('close-modal-btn')?.addEventListener('click', hideAuthModal);
  document.getElementById('logout-btn')?.addEventListener('click', handleLogout);

  // Forms
  document.getElementById('auth-form')?.addEventListener('submit', handleAuthSubmit);
  document.getElementById('create-decision-form')?.addEventListener('submit', handleCreateDecisionSubmit);
  document.getElementById('add-alternative-form')?.addEventListener('submit', handleAddAlternativeSubmit);
  document.getElementById('post-comment-form')?.addEventListener('submit', handlePostCommentSubmit);
  document.getElementById('upload-file-form')?.addEventListener('submit', handleUploadFileSubmit);
}


// Check Authentication state
function checkAuth() {
  if (state.token && state.user) {
    document.getElementById('guest-controls').style.display = 'none';
    document.getElementById('user-controls').style.display = 'flex';
    document.getElementById('user-name-display').innerText = state.user.full_name;

    const roleBadge = document.getElementById('user-role-badge');
    roleBadge.innerText = state.user.role;
    roleBadge.className = `role-pill role-${state.user.role}`;

    // Show role-specific tabs
    if (['Administrator', 'Manager'].includes(state.user.role)) {
      document.getElementById('nav-users-btn').style.display = 'inline-block';
    }
    if (state.user.role === 'Administrator') {
      document.getElementById('nav-audit-btn').style.display = 'inline-block';
    }
  } else {
    document.getElementById('guest-controls').style.display = 'flex';
    document.getElementById('user-controls').style.display = 'none';
    document.getElementById('nav-users-btn').style.display = 'none';
    document.getElementById('nav-audit-btn').style.display = 'none';
  }
}

// Quick Demo Login for instant testing
async function quickLogin(role) {
  const credentialsMap = {
    'Administrator': { email: 'admin@expert.org', password: 'admin123' },
    'Manager': { email: 'manager@expert.org', password: 'manager123' },
    'Reviewer': { email: 'reviewer@expert.org', password: 'reviewer123' },
    'Employee': { email: 'employee@expert.org', password: 'emp123' }
  };

  const creds = credentialsMap[role];
  if (!creds) return;

  try {
    const res = await fetch(`${API_BASE}/auth/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(creds)
    });

    const data = await res.json();
    if (!res.ok) throw new Error(data.detail || 'Login failed');

    state.token = data.access_token;
    state.user = {
      id: data.user_id,
      email: data.email,
      full_name: data.full_name,
      role: data.role
    };

    localStorage.setItem('token', state.token);
    localStorage.setItem('user', JSON.stringify(state.user));

    checkAuth();
    showToast(`Logged in as ${data.full_name} (${data.role})`);

    // Switch to Dashboard Tab
    document.querySelector('[data-tab="dashboard-tab"]')?.click();

  } catch (err) {
    alert(`Error logging in: ${err.message}`);
  }
}

// Show/Hide Auth Modal
function showAuthModal(mode) {
  const modal = document.getElementById('auth-modal');
  const title = document.getElementById('modal-title');
  const submitBtn = document.getElementById('auth-submit-btn');
  const regFields = document.getElementById('register-extra-fields');

  modal.setAttribute('data-mode', mode);
  modal.classList.add('active');

  if (mode === 'login') {
    title.innerText = 'Sign In to Decision Replay';
    submitBtn.innerText = 'Sign In';
    regFields.style.display = 'none';
  } else {
    title.innerText = 'Create Account';
    submitBtn.innerText = 'Register Account';
    regFields.style.display = 'block';
  }
}

function hideAuthModal() {
  document.getElementById('auth-modal').classList.remove('active');
}

// Handle Login / Register Submit
async function handleAuthSubmit(e) {
  e.preventDefault();
  const modal = document.getElementById('auth-modal');
  const mode = modal.getAttribute('data-mode');

  const email = document.getElementById('auth-email').value;
  const password = document.getElementById('auth-password').value;

  if (mode === 'login') {
    try {
      const res = await fetch(`${API_BASE}/auth/login`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, password })
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.detail || 'Authentication failed');

      state.token = data.access_token;
      state.user = {
        id: data.user_id,
        email: data.email,
        full_name: data.full_name,
        role: data.role
      };

      localStorage.setItem('token', state.token);
      localStorage.setItem('user', JSON.stringify(state.user));

      hideAuthModal();
      checkAuth();
      showToast(`Welcome back, ${data.full_name}!`);
      document.querySelector('[data-tab="dashboard-tab"]')?.click();
    } catch (err) {
      alert(`Login error: ${err.message}`);
    }
  } else {
    // Register
    const full_name = document.getElementById('auth-fullname').value;
    const role = document.getElementById('auth-role-select').value;

    try {
      const res = await fetch(`${API_BASE}/auth/register`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, password, full_name, role })
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.detail || 'Registration failed');

      hideAuthModal();
      showToast('Registration successful! Please sign in with your credentials.');
      showAuthModal('login');
    } catch (err) {
      alert(`Registration error: ${err.message}`);
    }
  }
}

// Handle Logout
function handleLogout() {
  localStorage.removeItem('token');
  localStorage.removeItem('user');
  state.token = null;
  state.user = null;
  checkAuth();
  showToast('Logged out successfully');
  document.querySelector('[data-tab="wireframe-tab"]')?.click();
}

// Load System & Dashboard Stats
async function loadDashboardStats() {
  if (!state.token) return;
  try {
    const res = await fetch(`${API_BASE}/users/system-stats`, {
      headers: { 'Authorization': `Bearer ${state.token}` }
    });
    if (!res.ok) return;
    const stats = await res.json();

    document.getElementById('stat-total-users').innerText = stats.total_users;
    document.getElementById('stat-total-teams').innerText = stats.total_teams;
    document.getElementById('stat-active-sessions').innerText = stats.active_sessions;
    document.getElementById('stat-status').innerText = stats.system_status;

    // Render Role Breakdown Badges
    const breakdownEl = document.getElementById('role-breakdown-list');
    if (breakdownEl && stats.roles_breakdown) {
      breakdownEl.innerHTML = Object.entries(stats.roles_breakdown)
        .map(([role, count]) => `<span class="role-pill role-${role}">${role}: ${count}</span>`)
        .join(' ');
    }
  } catch (err) {
    console.error('Failed to load stats', err);
  }
}

// Load Users Table (User Management)
async function loadUsers() {
  if (!state.token) return;
  try {
    const res = await fetch(`${API_BASE}/users`, {
      headers: { 'Authorization': `Bearer ${state.token}` }
    });
    const users = await res.json();
    if (!res.ok) throw new Error(users.detail || 'Failed to load users');

    const tbody = document.getElementById('users-tbody');
    tbody.innerHTML = users.map(u => `
      <tr>
        <td>#${u.id}</td>
        <td><strong>${u.full_name}</strong><br><small style="color: var(--text-muted);">${u.email}</small></td>
        <td>${u.department || 'Engineering'}</td>
        <td><span class="role-pill role-${u.role}">${u.role}</span></td>
        <td><span class="badge badge-success">Active</span></td>
        <td>
          ${state.user.role === 'Administrator' ? `
            <select class="form-control" style="padding:0.25rem 0.5rem; font-size:0.8rem;" onchange="updateRole(${u.id}, this.value)">
              ${state.roles.map(r => `<option value="${r}" ${r === u.role ? 'selected' : ''}>${r}</option>`).join('')}
            </select>
          ` : '<span style="color:var(--text-muted)">Read-only</span>'}
        </td>
      </tr>
    `).join('');
  } catch (err) {
    console.error('User list error', err);
  }
}

// Update User Role (Admin action)
async function updateRole(userId, newRole) {
  if (!state.token) return;
  try {
    const res = await fetch(`${API_BASE}/users/${userId}/role`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${state.token}`
      },
      body: JSON.stringify({ role: newRole })
    });
    const data = await res.json();
    if (!res.ok) throw new Error(data.detail || 'Failed to update role');

    showToast(`Updated user role to ${newRole}`);
    loadUsers();
  } catch (err) {
    alert(`Role update error: ${err.message}`);
  }
}

// Load Audit Logs
async function loadAuditLogs() {
  if (!state.token) return;
  try {
    const res = await fetch(`${API_BASE}/users/audit-logs`, {
      headers: { 'Authorization': `Bearer ${state.token}` }
    });
    const logs = await res.json();
    if (!res.ok) return;

    const tbody = document.getElementById('audit-tbody');
    tbody.innerHTML = logs.map(l => `
      <tr>
        <td>#${l.id}</td>
        <td><span class="badge badge-info">${l.action}</span></td>
        <td>${l.entity_type} #${l.entity_id || ''}</td>
        <td>${l.details || ''}</td>
        <td><small style="color:var(--text-muted)">${new Date(l.timestamp).toLocaleString()}</small></td>
      </tr>
    `).join('');
  } catch (err) {
    console.error('Audit logs error', err);
  }
}

// Load Milestone 1 Wireframe & Requirement Explorer data
async function loadWireframeSpecs() {
  try {
    const [reqRes, dbRes, uiRes] = await Promise.all([
      fetch(`${API_BASE}/wireframes/requirements`),
      fetch(`${API_BASE}/wireframes/db-schema`),
      fetch(`${API_BASE}/wireframes/ui-specs`)
    ]);

    const reqs = await reqRes.json();
    const dbSchema = await dbRes.json();
    const uiSpecs = await uiRes.json();

    // Render Requirements
    const reqContainer = document.getElementById('requirements-container');
    if (reqContainer) {
      reqContainer.innerHTML = `
        <div class="glass wireframe-card">
          <h3>🎯 ${reqs.title}</h3>
          <p style="margin: 0.75rem 0; color: var(--text-muted);">${reqs.objective}</p>
          <h4 style="margin-top:1rem; margin-bottom:0.5rem;">Key Platform Outcomes:</h4>
          <div style="display:grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 0.5rem;">
            ${reqs.outcomes.map(o => `<div style="padding:0.5rem; background:rgba(255,255,255,0.03); border-radius:6px; font-size:0.85rem;">✅ ${o}</div>`).join('')}
          </div>
        </div>
      `;
    }

    // Render DB ER Diagram visualizer
    const dbContainer = document.getElementById('db-schema-container');
    if (dbContainer) {
      dbContainer.innerHTML = `
        <div class="glass wireframe-card">
          <h3>🗄️ Database ER Schema Specification</h3>
          <p style="color:var(--text-muted); margin-bottom:1rem;">SQLAlchemy ORM models initialized with relational constraints and cascade deletes.</p>
          <div style="display:grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 1rem;">
            ${dbSchema.tables.map(t => `
              <div style="background: rgba(15,23,42,0.8); border:1px solid var(--border-color); border-radius:8px; padding:1rem;">
                <div style="display:flex; justify-content:space-between; align-items:center; border-bottom:1px solid var(--border-color); padding-bottom:0.5rem; margin-bottom:0.5rem;">
                  <strong style="color:var(--primary)">${t.name}</strong>
                  <span class="badge badge-info">${t.columns.length} columns</span>
                </div>
                <ul style="list-style:none; font-size:0.8rem; line-height:1.6; color:var(--text-muted)">
                  ${t.columns.map(c => `<li>🔹 ${c}</li>`).join('')}
                </ul>
              </div>
            `).join('')}
          </div>
        </div>
      `;
    }

    // Render UI Specs
    const uiContainer = document.getElementById('ui-specs-container');
    if (uiContainer) {
      uiContainer.innerHTML = `
        <div class="glass wireframe-card">
          <h3>🖥️ UI Wireframes & Workflow Layouts</h3>
          <div style="display:grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 1rem; margin-top:1rem;">
            ${uiSpecs.screens.map(s => `
              <div style="background: rgba(15,23,42,0.8); border:1px solid var(--border-color); border-radius:8px; padding:1rem;">
                <strong style="color:var(--accent)">${s.name}</strong>
                <p style="font-size:0.85rem; color:var(--text-muted); margin-top:0.5rem;">${s.description}</p>
              </div>
            `).join('')}
          </div>
        </div>
      `;
    }

  } catch (err) {
    console.error('Wireframe load error', err);
  }
}

// Load Live SQLite Database Data
async function loadLiveDatabase() {
  const container = document.getElementById('db-tables-view-container');
  if (!container) return;
  
  container.innerHTML = '<p style="color:var(--text-muted);"><span class="loading-spinner"></span> Loading real-time database records from decision_replay.db...</p>';
  
  try {
    const res = await fetch(`${API_BASE}/wireframes/db-data`);
    const data = await res.json();
    
    if (!res.ok || data.status !== 'online') {
      container.innerHTML = `<p style="color:var(--danger)">Failed to load database: ${data.message || 'Unknown error'}</p>`;
      return;
    }
    
    const tables = data.tables || {};
    const tableKeys = Object.keys(tables);
    
    if (tableKeys.length === 0) {
      container.innerHTML = '<p style="color:var(--text-muted);">No tables found in database.</p>';
      return;
    }
    
    let html = `
      <div style="display:flex; gap:0.5rem; flex-wrap:wrap; margin-bottom:1.5rem;">
        ${tableKeys.map(name => `
          <button class="btn btn-sm ${name === 'users' ? 'btn-primary' : 'btn-secondary'}" 
                  id="tab-btn-db-${name}"
                  onclick="selectDbTable('${name}')">
            📊 ${name.toUpperCase()} <span style="opacity:0.75; font-size:0.75rem;">(${tables[name].total_rows} rows)</span>
          </button>
        `).join('')}
      </div>
      
      <div id="db-active-table-view"></div>
    `;
    
    container.innerHTML = html;
    window._cachedDbTables = tables;
    selectDbTable(tableKeys[0]);
    
  } catch (err) {
    container.innerHTML = `<p style="color:var(--danger)">Error querying database: ${err.message}</p>`;
  }
}

// Render active table view
function selectDbTable(tableName) {
  const tables = window._cachedDbTables;
  if (!tables || !tables[tableName]) return;
  
  // Update button highlights
  Object.keys(tables).forEach(t => {
    const btn = document.getElementById(`tab-btn-db-${t}`);
    if (btn) {
      btn.className = `btn btn-sm ${t === tableName ? 'btn-primary' : 'btn-secondary'}`;
    }
  });
  
  const target = document.getElementById('db-active-table-view');
  if (!target) return;
  
  const tableData = tables[tableName];
  const cols = tableData.columns || [];
  const records = tableData.records || [];
  
  let viewHtml = `
    <div style="background:rgba(255,255,255,0.02); border:1px solid var(--border-color); border-radius:8px; padding:1rem;">
      <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:0.75rem;">
        <h4 style="color:var(--accent); margin:0;">Table: <code>${tableName}</code> (${records.length} records)</h4>
        <span style="font-size:0.8rem; color:var(--text-muted);">Columns: ${cols.join(', ')}</span>
      </div>
  `;
  
  if (records.length === 0) {
    viewHtml += `<p style="color:var(--text-muted); font-size:0.85rem; padding:1rem; text-align:center;">No records currently in table <code>${tableName}</code>.</p>`;
  } else {
    viewHtml += `
      <div class="table-container" style="max-height:400px; overflow-y:auto;">
        <table>
          <thead>
            <tr>
              ${cols.map(c => `<th>${c}</th>`).join('')}
            </tr>
          </thead>
          <tbody>
            ${records.map(row => `
              <tr>
                ${cols.map(c => {
                  let val = row[c];
                  if (val === null || val === undefined) return '<td style="color:var(--text-muted); font-style:italic;">NULL</td>';
                  if (c === 'role') return `<td><span class="role-pill role-${val}">${val}</span></td>`;
                  if (typeof val === 'string' && val.length > 50) return `<td title="${val}">${val.substring(0, 47)}...</td>`;
                  return `<td>${val}</td>`;
                }).join('')}
              </tr>
            `).join('')}
          </tbody>
        </table>
      </div>
    `;
  }
  
  viewHtml += `</div>`;
  target.innerHTML = viewHtml;
}

// Simple Toast Notification
function showToast(message) {
  const toast = document.createElement('div');
  toast.style.cssText = `
    position: fixed;
    bottom: 20px;
    right: 20px;
    background: linear-gradient(135deg, var(--primary), var(--accent));
    color: white;
    padding: 0.75rem 1.5rem;
    border-radius: 8px;
    box-shadow: var(--glass-shadow);
    z-index: 2000;
    font-weight: 600;
    font-size: 0.9rem;
    animation: fadeIn 0.3s ease;
  `;
  toast.innerText = message;
  document.body.appendChild(toast);
  setTimeout(() => toast.remove(), 3000);
}

/* ==========================================================================
   MILESTONE 2 DECISION MANAGEMENT & COLLABORATION FUNCTIONS
   ========================================================================== */

// Load Decisions List
async function loadDecisions() {
  const container = document.getElementById('decisions-container');
  if (!container) return;

  try {
    const res = await fetch(`${API_BASE}/v1/decisions`);
    if (!res.ok) throw new Error('Failed to load decisions');
    const decisions = await res.json();
    state.allDecisions = decisions;
    renderDecisionCards(decisions);
  } catch (err) {
    console.error('Error loading decisions:', err);
    container.innerHTML = `<p style="color:var(--danger)">Error loading decisions: ${err.message}</p>`;
  }
}

// Render Decision Cards
function renderDecisionCards(decisions) {
  const container = document.getElementById('decisions-container');
  if (!container) return;

  if (decisions.length === 0) {
    container.innerHTML = `<div class="glass wireframe-card" style="grid-column: 1/-1; text-align:center; padding:2rem;"><p style="color:var(--text-muted)">No decisions found matching filter criteria.</p></div>`;
    return;
  }

  const statusColors = {
    'Draft': 'background:rgba(148,163,184,0.2); color:#94a3b8;',
    'Under Review': 'background:rgba(251,191,36,0.2); color:#fbbf24;',
    'Approved': 'background:rgba(34,197,94,0.2); color:#22c55e;',
    'Rejected': 'background:rgba(239,68,68,0.2); color:#ef4444;',
    'Archived': 'background:rgba(100,116,139,0.2); color:#64748b;'
  };

  container.innerHTML = decisions.map(d => `
    <div class="glass wireframe-card" style="display:flex; flex-direction:column; justify-content:space-between; cursor:pointer;" onclick="openDecisionDetailModal(${d.id})">
      <div>
        <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:0.75rem;">
          <span class="badge" style="background:rgba(56,189,248,0.2); color:#38bdf8; font-size:0.75rem; padding:2px 8px; border-radius:4px;">${d.category}</span>
          <div style="display:flex; gap:0.4rem; align-items:center;">
            <span class="badge" style="${statusColors[d.status] || ''} font-size:0.75rem; padding:2px 8px; border-radius:4px;">${d.status}</span>
            <span class="badge" style="background:rgba(255,255,255,0.1); color:#fff; font-size:0.75rem; padding:2px 8px; border-radius:4px;">v${d.version}</span>
          </div>
        </div>

        <h3 style="font-size:1.1rem; color:var(--text); margin-bottom:0.5rem; line-height:1.3;">${d.title}</h3>
        <p style="font-size:0.85rem; color:var(--text-muted); line-height:1.5; margin-bottom:1rem; display:-webkit-box; -webkit-line-clamp:3; -webkit-box-orient:vertical; overflow:hidden;">
          ${d.problem_statement}
        </p>
      </div>

      <div style="border-top:1px solid var(--border-color); pt:0.75rem; margin-top:0.75rem; display:flex; justify-content:space-between; align-items:center; font-size:0.8rem; color:var(--text-muted);">
        <div>👤 ${d.creator_name || 'System'}</div>
        <div style="display:flex; gap:0.75rem;">
          <span>⚖️ ${d.alternatives ? d.alternatives.length : 0} options</span>
          <span>💬 ${d.comments_count || 0}</span>
          <span>📎 ${d.attachments_count || 0}</span>
        </div>
      </div>
    </div>
  `).join('');
}

// Filter Decisions locally
function filterDecisions() {
  const search = document.getElementById('decision-search-input')?.value.toLowerCase() || '';
  const category = document.getElementById('decision-category-filter')?.value || 'All';
  const status = document.getElementById('decision-status-filter')?.value || 'All';

  let filtered = state.allDecisions.filter(d => {
    const matchSearch = d.title.toLowerCase().includes(search) || d.problem_statement.toLowerCase().includes(search);
    const matchCategory = category === 'All' || d.category === category;
    const matchStatus = status === 'All' || d.status === status;
    return matchSearch && matchCategory && matchStatus;
  });

  renderDecisionCards(filtered);
}

// Open / Close Create Decision Modal
function openCreateDecisionModal(decisionToEdit = null) {
  if (!state.token) {
    alert('Please sign in to create or edit decisions.');
    showAuthModal('login');
    return;
  }

  const modal = document.getElementById('create-decision-modal');
  const titleEl = document.getElementById('decision-modal-title');
  const editIdEl = document.getElementById('edit-decision-id');
  const changeGroup = document.getElementById('change-summary-group');

  if (decisionToEdit) {
    titleEl.innerText = `Edit Decision #${decisionToEdit.id} (Version Bump to v${decisionToEdit.version + 1})`;
    editIdEl.value = decisionToEdit.id;
    document.getElementById('decision-title-input').value = decisionToEdit.title;
    document.getElementById('decision-category-input').value = decisionToEdit.category;
    document.getElementById('decision-status-input').value = decisionToEdit.status;
    document.getElementById('decision-problem-input').value = decisionToEdit.problem_statement;
    document.getElementById('decision-rationale-input').value = decisionToEdit.rationale || '';
    changeGroup.style.display = 'block';
  } else {
    titleEl.innerText = 'Create New Decision';
    editIdEl.value = '';
    document.getElementById('create-decision-form').reset();
    changeGroup.style.display = 'none';
  }

  modal.style.display = 'flex';
}

function closeCreateDecisionModal() {
  document.getElementById('create-decision-modal').style.display = 'none';
}

// Submit Create/Edit Decision
async function handleCreateDecisionSubmit(e) {
  e.preventDefault();
  if (!state.token) return;

  const editId = document.getElementById('edit-decision-id').value;
  const title = document.getElementById('decision-title-input').value;
  const category = document.getElementById('decision-category-input').value;
  const status = document.getElementById('decision-status-input').value;
  const problem_statement = document.getElementById('decision-problem-input').value;
  const rationale = document.getElementById('decision-rationale-input').value;
  const change_summary = document.getElementById('decision-change-summary-input').value;

  try {
    let url = `${API_BASE}/v1/decisions`;
    let method = 'POST';
    let body = { title, category, status, problem_statement, rationale };

    if (editId) {
      url = `${API_BASE}/v1/decisions/${editId}`;
      method = 'PUT';
      body.change_summary = change_summary || 'Updated decision metadata';
    }

    const res = await fetch(url, {
      method,
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${state.token}`
      },
      body: JSON.stringify(body)
    });

    const data = await res.json();
    if (!res.ok) throw new Error(data.detail || 'Failed to save decision');

    closeCreateDecisionModal();
    showToast(editId ? `Decision updated to Version ${data.version}` : 'Decision created successfully!');
    loadDecisions();

    if (editId && state.activeDecisionId == editId) {
      openDecisionDetailModal(editId);
    }
  } catch (err) {
    alert(`Error: ${err.message}`);
  }
}

// Open Decision Detail Modal Hub
async function openDecisionDetailModal(decisionId) {
  state.activeDecisionId = decisionId;
  const modal = document.getElementById('decision-detail-modal');
  modal.style.display = 'flex';

  try {
    const res = await fetch(`${API_BASE}/v1/decisions/${decisionId}`);
    if (!res.ok) throw new Error('Decision not found');
    const d = await res.json();

    document.getElementById('detail-title').innerText = d.title;
    document.getElementById('detail-category-badge').innerText = d.category;
    document.getElementById('detail-status-badge').innerText = d.status;
    document.getElementById('detail-version-badge').innerText = `v${d.version}`;
    document.getElementById('detail-meta').innerText = `Created by ${d.creator_name || 'System'} | ${new Date(d.created_at).toLocaleDateString()}`;
    document.getElementById('detail-problem-statement').innerText = d.problem_statement;
    document.getElementById('detail-rationale').innerText = d.rationale || 'No formal rationale documented yet.';

    window._currentDecision = d;
    switchDetailSubtab('overview');

  } catch (err) {
    alert(`Failed to load decision details: ${err.message}`);
    closeDecisionDetailModal();
  }
}

function closeDecisionDetailModal() {
  document.getElementById('decision-detail-modal').style.display = 'none';
  state.activeDecisionId = null;
}

// Switch Subtabs in Decision Detail View
function switchDetailSubtab(subtabName) {
  document.querySelectorAll('.detail-subtab-btn').forEach(btn => btn.classList.remove('active'));
  document.querySelectorAll('.detail-subtab-content').forEach(c => c.style.display = 'none');

  const activeContent = document.getElementById(`subtab-${subtabName}`);
  if (activeContent) activeContent.style.display = 'block';

  const dId = state.activeDecisionId;
  if (subtabName === 'alternatives') loadAlternativesMatrix(dId);
  if (subtabName === 'discussion') loadComments(dId);
  if (subtabName === 'files') loadAttachments(dId);
  if (subtabName === 'versions') loadVersionHistory(dId);
}

// 1. Alternatives Matrix
async function loadAlternativesMatrix(decisionId) {
  const grid = document.getElementById('alternatives-matrix-grid');
  const bannerText = document.getElementById('matrix-recommendation-text');
  grid.innerHTML = '<p style="color:var(--text-muted)">Evaluating alternatives matrix...</p>';

  try {
    const res = await fetch(`${API_BASE}/v1/decisions/${decisionId}/alternatives/comparison`);
    const data = await res.json();

    if (data.recommended_option) {
      bannerText.innerHTML = `Highest Rated Recommendation: <strong>${data.recommended_option}</strong> (${data.recommendation_reason})`;
    } else {
      bannerText.innerText = 'No alternative options recorded yet for side-by-side comparison.';
    }

    if (!data.alternatives || data.alternatives.length === 0) {
      grid.innerHTML = '<p style="color:var(--text-muted)">No alternatives recorded yet. Click "+ Add Alternative" above to compare options.</p>';
      return;
    }

    const riskColors = { 'Low': '#22c55e', 'Medium': '#fbbf24', 'High': '#ef4444' };

    grid.innerHTML = data.alternatives.map((alt, index) => `
      <div style="background:rgba(255,255,255,0.02); border:1px solid ${alt.title === data.recommended_option ? '#38bdf8' : 'var(--border-color)'}; border-radius:8px; padding:1rem; position:relative;">
        ${alt.title === data.recommended_option ? '<span style="position:absolute; top:-10px; right:10px; background:#38bdf8; color:#000; font-weight:700; font-size:0.7rem; padding:2px 8px; border-radius:10px;">★ RECOMMENDED</span>' : ''}
        <h4 style="margin-bottom:0.4rem; color:var(--text);">${alt.title}</h4>
        <p style="font-size:0.85rem; color:var(--text-muted); margin-bottom:0.75rem;">${alt.description || 'No description'}</p>

        <div style="font-size:0.8rem; line-height:1.5; margin-bottom:0.75rem;">
          <div style="color:#22c55e; margin-bottom:0.25rem;"><strong>Pros:</strong> ${alt.pros || 'N/A'}</div>
          <div style="color:#ef4444;"><strong>Cons:</strong> ${alt.cons || 'N/A'}</div>
        </div>

        <div style="display:flex; justify-content:space-between; align-items:center; pt:0.5rem; border-top:1px dashed var(--border-color); font-size:0.8rem;">
          <div>Cost: <strong>$${alt.estimated_cost}</strong></div>
          <div>Risk: <strong style="color:${riskColors[alt.risk_level] || '#fff'}">${alt.risk_level}</strong></div>
          <div>Feasibility: <strong>${alt.feasibility_score}/10</strong></div>
        </div>
      </div>
    `).join('');

  } catch (err) {
    grid.innerHTML = `<p style="color:var(--danger)">Error loading comparison matrix: ${err.message}</p>`;
  }
}

function toggleAddAlternativeForm() {
  const card = document.getElementById('add-alternative-card');
  card.style.display = card.style.display === 'none' ? 'block' : 'none';
}

async function handleAddAlternativeSubmit(e) {
  e.preventDefault();
  if (!state.token || !state.activeDecisionId) return;

  const title = document.getElementById('alt-title').value;
  const description = document.getElementById('alt-desc').value;
  const pros = document.getElementById('alt-pros').value;
  const cons = document.getElementById('alt-cons').value;
  const estimated_cost = parseFloat(document.getElementById('alt-cost').value) || 0.0;
  const risk_level = document.getElementById('alt-risk').value;
  const feasibility_score = parseInt(document.getElementById('alt-score').value) || 5;

  try {
    const res = await fetch(`${API_BASE}/v1/decisions/${state.activeDecisionId}/alternatives`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${state.token}`
      },
      body: JSON.stringify({ title, description, pros, cons, estimated_cost, risk_level, feasibility_score })
    });

    const data = await res.json();
    if (!res.ok) throw new Error(data.detail || 'Failed to add alternative');

    toggleAddAlternativeForm();
    document.getElementById('add-alternative-form').reset();
    showToast('Alternative option recorded!');
    loadAlternativesMatrix(state.activeDecisionId);

  } catch (err) {
    alert(`Error: ${err.message}`);
  }
}

// 2. Discussions Module
async function loadComments(decisionId) {
  const feed = document.getElementById('comments-feed');
  feed.innerHTML = '<p style="color:var(--text-muted)">Loading discussion threads...</p>';

  try {
    const res = await fetch(`${API_BASE}/v1/decisions/${decisionId}/comments`);
    const comments = await res.json();

    if (comments.length === 0) {
      feed.innerHTML = '<p style="color:var(--text-muted)">No comments posted yet. Be the first to start the discussion!</p>';
      return;
    }

    feed.innerHTML = comments.map(c => `
      <div style="background:rgba(255,255,255,0.02); border:1px solid var(--border-color); border-radius:8px; padding:0.85rem 1rem;">
        <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:0.4rem;">
          <div style="display:flex; gap:0.5rem; align-items:center;">
            <strong>${c.author_name || 'User'}</strong>
            <span class="role-pill role-${c.author_role || 'Employee'}" style="font-size:0.7rem; padding:1px 6px;">${c.author_role || 'User'}</span>
          </div>
          <span style="font-size:0.75rem; color:var(--text-muted);">${new Date(c.created_at).toLocaleString()}</span>
        </div>
        <p style="font-size:0.9rem; color:var(--text); line-height:1.5; white-space:pre-wrap; margin:0;">${c.content}</p>
      </div>
    `).join('');

  } catch (err) {
    feed.innerHTML = `<p style="color:var(--danger)">Error loading comments: ${err.message}</p>`;
  }
}

async function handlePostCommentSubmit(e) {
  e.preventDefault();
  if (!state.token || !state.activeDecisionId) return;

  const content = document.getElementById('comment-input').value;
  try {
    const res = await fetch(`${API_BASE}/v1/decisions/${state.activeDecisionId}/comments`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${state.token}`
      },
      body: JSON.stringify({ content })
    });

    const data = await res.json();
    if (!res.ok) throw new Error(data.detail || 'Failed to post comment');

    document.getElementById('comment-input').value = '';
    showToast('Comment posted');
    loadComments(state.activeDecisionId);

  } catch (err) {
    alert(`Error posting comment: ${err.message}`);
  }
}

// 3. File Attachments Engine
async function loadAttachments(decisionId) {
  const list = document.getElementById('attachments-list');
  list.innerHTML = '<p style="color:var(--text-muted)">Loading file attachments...</p>';

  try {
    const res = await fetch(`${API_BASE}/v1/decisions/${decisionId}/attachments`);
    const attachments = await res.json();

    if (attachments.length === 0) {
      list.innerHTML = '<p style="color:var(--text-muted)">No files uploaded yet for this decision.</p>';
      return;
    }

    list.innerHTML = attachments.map(att => `
      <div style="background:rgba(255,255,255,0.02); border:1px solid var(--border-color); border-radius:6px; padding:0.75rem 1rem; display:flex; justify-content:space-between; align-items:center;">
        <div>
          <strong>📄 ${att.filename}</strong>
          <span style="font-size:0.75rem; color:var(--text-muted); margin-left:0.5rem;">(${(att.file_size / 1024).toFixed(1)} KB | Uploaded by ${att.uploader_name || 'User'})</span>
        </div>
        <a href="${API_BASE}/v1/attachments/${att.id}/download" target="_blank" class="btn btn-secondary btn-sm" style="text-decoration:none;">⬇️ Download</a>
      </div>
    `).join('');

  } catch (err) {
    list.innerHTML = `<p style="color:var(--danger)">Error loading attachments: ${err.message}</p>`;
  }
}

async function handleUploadFileSubmit(e) {
  e.preventDefault();
  if (!state.token || !state.activeDecisionId) return;

  const fileInput = document.getElementById('attachment-file-input');
  if (!fileInput.files || fileInput.files.length === 0) return;

  const formData = new FormData();
  formData.append('file', fileInput.files[0]);

  try {
    const res = await fetch(`${API_BASE}/v1/decisions/${state.activeDecisionId}/upload`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${state.token}`
      },
      body: formData
    });

    const data = await res.json();
    if (!res.ok) throw new Error(data.detail || 'File upload failed');

    fileInput.value = '';
    showToast(`Uploaded file ${data.filename}`);
    loadAttachments(state.activeDecisionId);

  } catch (err) {
    alert(`File upload error: ${err.message}`);
  }
}

// 4. Version History Inspection Timeline
async function loadVersionHistory(decisionId) {
  const timeline = document.getElementById('version-history-timeline');
  timeline.innerHTML = '<p style="color:var(--text-muted)">Loading version snapshots...</p>';

  try {
    const res = await fetch(`${API_BASE}/v1/decisions/${decisionId}/versions`);
    const versions = await res.json();

    if (versions.length === 0) {
      timeline.innerHTML = '<p style="color:var(--text-muted)">No revision history snapshots found.</p>';
      return;
    }

    timeline.innerHTML = versions.map(v => `
      <div style="background:rgba(255,255,255,0.02); border-left:3px solid #38bdf8; border-radius:0 8px 8px 0; padding:0.85rem 1rem; border-top:1px solid var(--border-color); border-right:1px solid var(--border-color); border-bottom:1px solid var(--border-color);">
        <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:0.4rem;">
          <div>
            <span class="badge" style="background:#38bdf8; color:#000; font-weight:700; font-size:0.75rem; padding:2px 8px; border-radius:4px;">Version ${v.version}</span>
            <strong style="margin-left:0.5rem; font-size:0.95rem;">${v.title}</strong>
          </div>
          <span style="font-size:0.75rem; color:var(--text-muted);">${new Date(v.created_at).toLocaleString()} by ${v.created_by_name || 'System'}</span>
        </div>
        <p style="font-size:0.85rem; color:var(--text-muted); margin-bottom:0.4rem;"><strong>Change Summary:</strong> ${v.change_summary || 'N/A'}</p>
        <p style="font-size:0.85rem; color:var(--text); background:rgba(0,0,0,0.2); padding:0.5rem; border-radius:4px; margin:0;">${v.problem_statement}</p>
      </div>
    `).join('');

  } catch (err) {
    timeline.innerHTML = `<p style="color:var(--danger)">Error loading version history: ${err.message}</p>`;
  }
}


