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
  // Validação idade
  const idadeNum = Number(payload.idade || 0);
  if (!Number.isInteger(idadeNum) || idadeNum < 18) {
    throw new Error('Idade deve ser um número inteiro maior ou igual a 18');
  }
  payload.idade = idadeNum;
  // Validar telefone (11 dígitos)
  const telefone = payload.telefone.replace(/\D/g, '');
  if (telefone.length !== 11) {
    throw new Error('Telefone deve ter exatamente 11 dígitos');
  }
  payload.telefone = Number(telefone);
  payload.correntista = form.elements['correntista'].checked;
  // Converter saldo formatado (R$ 1.234,56) para número
  const saldoStr = payload.saldo_cc || '';
  const saldoNumerico = saldoStr.replace(/[^\d,]/g, '').replace(',', '.');
  payload.saldo_cc = saldoNumerico ? Number(saldoNumerico) : null;
  // Score é calculado automaticamente no backend (saldo_cc * 0.1)
  return payload;
}

function formatCurrency(value) {
  // Remove tudo exceto dígitos
  let num = value.replace(/\D/g, '');
  if (!num) return '';
  // Converte para centavos e formata
  num = (Number(num) / 100).toFixed(2);
  // Formata com separadores brasileiros
  num = num.replace('.', ',');
  num = num.replace(/(\d)(\d{3})(,\d{2})$/, '$1.$2$3');
  num = num.replace(/(\d)(\d{3}\.)/, '$1.$2');
  return 'R$ ' + num;
}

function renderClients(rows) {
  const tbody = document.querySelector('#clients-tbody');
  tbody.innerHTML = '';
  if (rows.length === 0) {
    const tr = document.createElement('tr');
    tr.innerHTML = '<td colspan="7" style="text-align:center;color:#999;">Nenhum cliente cadastrado</td>';
    tbody.appendChild(tr);
    return;
  }
  for (const c of rows) {
    const tr = document.createElement('tr');
    const saldoNum = c.saldo_cc != null ? Number(c.saldo_cc) : null;
    const scoreCalc = saldoNum != null ? Math.floor(saldoNum * 0.1) : null;
    const saldoFormatado = saldoNum != null ? `R$ ${saldoNum.toLocaleString('pt-BR', { minimumFractionDigits: 2, maximumFractionDigits: 2 }).replace('.', ',')}` : '-';
    tr.innerHTML = `
      <td>${c.id}</td>
      <td>${c.nome}</td>
      <td>${c.telefone}</td>
      <td>${c.email || '-'}</td>
      <td>${c.idade ?? '-'}</td>
      <td>${c.correntista ? 'Sim' : 'Não'}</td>
      <td>${scoreCalc ?? '-'}</td>
      <td>${saldoFormatado}</td>
      <td class="actions">
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
    const res = await api.createClient(payload);
    document.querySelector('#api-response').textContent = JSON.stringify(res, null, 2);
    form.reset();
    await refreshClients();
  } catch (err) {
    console.error(err);
    document.querySelector('#api-response').textContent = `ERRO: ${err.message}`;
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
  
  // Formatar saldo como moeda
  const saldoInput = document.getElementById('saldo_cc');
  saldoInput.addEventListener('input', (e) => {
    e.target.value = formatCurrency(e.target.value);
  });
  
  refreshClients();
}

window.addEventListener('DOMContentLoaded', init);
