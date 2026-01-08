const api = {
  listClients: async () => {
    const r = await fetch('/clients');
    if (!r.ok) throw new Error('Falha ao listar clientes');
    return r.json();
  },
  createClient: async (payload) => {
    const r = await fetch('/clients', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    });
    if (!r.ok) {
      const text = await r.text();
      throw new Error(`Falha ao criar cliente: ${text}`);
    }
    return r.json();
  },
  deleteClient: async (id) => {
    const r = await fetch(`/clients/${id}`, { method: 'DELETE' });
    if (!r.ok) throw new Error('Falha ao excluir cliente');
  },
  score: async (id) => {
    const r = await fetch(`/clients/${id}/score`);
    if (!r.ok) throw new Error('Falha ao obter score');
    return r.json();
  },
};

function formToPayload(form) {
  const data = new FormData(form);
  const payload = Object.fromEntries(data.entries());
  // Normaliza tipos
  payload.telefone = payload.telefone ? Number(payload.telefone) : 0;
  payload.correntista = form.elements['correntista'].checked;
  payload.score_credito = payload.score_credito ? Number(payload.score_credito) : null;
  payload.saldo_cc = payload.saldo_cc ? Number(payload.saldo_cc) : null;
  return payload;
}

function renderClients(rows) {
  const tbody = document.querySelector('#clients-table tbody');
  tbody.innerHTML = '';
  for (const c of rows) {
    const tr = document.createElement('tr');
    tr.innerHTML = `
      <td>${c.id}</td>
      <td>${c.nome}</td>
      <td>${c.telefone}</td>
      <td>${c.correntista ? 'Sim' : 'Não'}</td>
      <td>${c.score_credito ?? '-'}</td>
      <td>${c.saldo_cc ?? '-'}</td>
      <td class="actions">
        <button data-action="score" data-id="${c.id}">Score</button>
        <button data-action="delete" data-id="${c.id}" class="danger">Excluir</button>
      </td>
    `;
    tbody.appendChild(tr);
  }
}

async function refreshClients() {
  try {
    const rows = await api.listClients();
    renderClients(rows);
  } catch (err) {
    console.error(err);
    alert(err.message);
  }
}

async function onSubmit(e) {
  e.preventDefault();
  const form = e.currentTarget;
  const payload = formToPayload(form);
  try {
    await api.createClient(payload);
    form.reset();
    await refreshClients();
  } catch (err) {
    console.error(err);
    alert(err.message);
  }
}

async function onTableClick(e) {
  const btn = e.target.closest('button');
  if (!btn) return;
  const id = btn.dataset.id;
  const action = btn.dataset.action;
  try {
    if (action === 'delete') {
      if (confirm('Excluir este cliente?')) {
        await api.deleteClient(id);
        await refreshClients();
      }
    } else if (action === 'score') {
      const s = await api.score(id);
      alert(`Cliente: ${s.nome}\nSaldo CC: ${s.saldo_cc ?? '-'}\nScore calculado: ${s.score_calculado ?? '-'}`);
    }
  } catch (err) {
    console.error(err);
    alert(err.message);
  }
}

function init() {
  document.getElementById('client-form').addEventListener('submit', onSubmit);
  document.getElementById('refresh').addEventListener('click', refreshClients);
  document.querySelector('#clients-table').addEventListener('click', onTableClick);
  refreshClients();
}

window.addEventListener('DOMContentLoaded', init);
