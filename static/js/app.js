const API_BASE = '/api';

// State management
let state = {
  token: localStorage.getItem('token') || null,
  user: JSON.parse(localStorage.getItem('user')) || null,
  roles: ['Employee', 'Reviewer', 'Manager', 'Administrator'],
  activeTab: 'wireframe-tab'
};

// Initialize App
document.addEventListener('DOMContentLoaded', () => {
  setupEventListeners();
  checkAuth();
  loadWireframeSpecs();
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

      if (tabId === 'users-tab') loadUsers();
      if (tabId === 'audit-tab') loadAuditLogs();
      if (tabId === 'dashboard-tab') loadDashboardStats();
    });
  });

  // Auth Modal Buttons
  document.getElementById('open-login-btn')?.addEventListener('click', () => showAuthModal('login'));
  document.getElementById('open-register-btn')?.addEventListener('click', () => showAuthModal('register'));
  document.getElementById('close-modal-btn')?.addEventListener('click', hideAuthModal);
  document.getElementById('logout-btn')?.addEventListener('click', handleLogout);

  // Forms
  document.getElementById('auth-form')?.addEventListener('submit', handleAuthSubmit);
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
