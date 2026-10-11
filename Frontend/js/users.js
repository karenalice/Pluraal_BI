// User Management and Link Management Controller

let allAvailableLinks = [];
let allUsersList = [];

async function carregarTodosLinks() {
  try {
    allAvailableLinks = await API.get("/links");
  } catch (err) {
    console.error("Erro ao carregar links:", err);
  }
}

async function carregarUsuarios() {
  const tbody = document.getElementById("usersTableBody");
  if (!tbody) return;

  tbody.innerHTML = `<tr><td colspan="6" class="text-center" style="padding: 2rem;">Carregando usuários...</td></tr>`;

  try {
    allUsersList = await API.get("/users");
    renderizarTabelaUsuarios(allUsersList);
  } catch (err) {
    tbody.innerHTML = `<tr><td colspan="6" class="text-center text-danger" style="padding: 2rem;">Erro ao carregar usuários: ${err.message}</td></tr>`;
  }
}

function renderizarTabelaUsuarios(usuarios) {
  const tbody = document.getElementById("usersTableBody");
  if (!tbody) return;

  if (usuarios.length === 0) {
    tbody.innerHTML = `<tr><td colspan="6" class="text-center text-muted" style="padding: 2rem;">Nenhum usuário cadastrado.</td></tr>`;
    return;
  }

  tbody.innerHTML = "";

  const activeLinkIds = new Set(allAvailableLinks.filter(link => link.ativo).map(link => String(link.id_link)));

  usuarios.forEach(u => {
    const tr = document.createElement("tr");
    tr.className = "bi-user-row";

    const assignedLinks = u.links_bi || [];
    const assignedIds = new Set(assignedLinks.map(link => String(link.id_link)));
    const hasAllUnits = u.hierarquia === "Master" ||
      (activeLinkIds.size > 0 && [...activeLinkIds].every(id => assignedIds.has(id)));
    const unitBadge = link => `<span class="bi-badge bi-badge-link">${escaparHTML(link.nome)}</span>`;
    let unitsMarkup = '<span class="bi-empty-value">Nenhuma unidade atribuída</span>';

    if (hasAllUnits) {
      unitsMarkup = '<span class="bi-all-units">Acesso a todas as unidades</span>';
    } else if (assignedLinks.length) {
      const visibleUnits = assignedLinks.slice(0, 4).map(unitBadge).join("");
      const remainingUnits = assignedLinks.slice(4);
      unitsMarkup = `<div class="bi-units-list">${visibleUnits}${remainingUnits.length ? `
        <details class="bi-units-details">
          <summary>+${remainingUnits.length} unidades</summary>
          <div class="bi-units-list bi-units-list-expanded">${remainingUnits.map(unitBadge).join("")}</div>
        </details>` : ""}</div>`;
    }

    tr.innerHTML = `
      <td>
        <div class="bi-user-identity">
          <strong>${escaparHTML(u.nome_completo_usuario || u.email)}</strong>
          <span>${escaparHTML(u.email)}</span>
        </div>
      </td>
      <td>
        <span class="bi-badge bi-badge-role">${escaparHTML(u.hierarquia)}</span>
      </td>
      <td>
        <div class="bi-permissions-list">
          ${u.pode_criar_usuario ? '<span class="bi-badge bi-badge-role" title="Pode gerenciar usuários">Criar usuários</span>' : ''}
          ${u.pode_criar_link ? '<span class="bi-badge bi-badge-role" title="Pode gerenciar links de Power BI">Gerenciar links</span>' : ''}
          ${!u.pode_criar_usuario && !u.pode_criar_link ? '<span class="bi-empty-value">Somente consulta</span>' : ''}
        </div>
      </td>
      <td>
        ${unitsMarkup}
      </td>
      <td>
        <span class="bi-badge ${u.ativo ? 'bi-badge-success' : 'bi-badge-danger'}">
          ${u.ativo ? 'Ativo' : 'Inativo'}
        </span>
      </td>
      <td>
        <div class="bi-row-actions">
          <button class="btn btn-secondary btn-sm btn-edit-user" data-id="${u.id_usuario}">Editar</button>
          <button class="btn btn-secondary btn-sm btn-reset-pwd" data-id="${u.id_usuario}">Nova Senha</button>
        </div>
      </td>
    `;

    tr.querySelector(".btn-edit-user").addEventListener("click", () => abrirModalUsuario(u));
    tr.querySelector(".btn-reset-pwd").addEventListener("click", () => redefinirSenhaUsuario(u.id_usuario, u.nome_completo_usuario));

    tbody.appendChild(tr);
  });
}

function abrirModalUsuario(usuario = null) {
  const modal = document.getElementById("userModal");
  const modalTitle = document.getElementById("userModalTitle");
  const form = document.getElementById("userForm");
  const userAlert = document.getElementById("userModalAlert");
  const linksContainer = document.getElementById("userModalLinksCheckboxes");

  userAlert.classList.add("hidden");
  userAlert.textContent = "";

  const currentUser = API.getUser();
  const isMaster = currentUser && currentUser.hierarquia === "Master";

  // Checkboxes permissions visibility
  const permSection = document.getElementById("userPermissionsSection");
  const linkPermGroup = document.getElementById("podeCriarLinkGroup");
  const userPermGroup = document.getElementById("podeCriarUsuarioGroup");
  const roleSelect = document.getElementById("userRole");

  if (isMaster) {
    permSection.classList.remove("hidden");
  } else {
    permSection.classList.add("hidden");
  }

  // Populate Power BI links checkboxes
  linksContainer.innerHTML = "";
  const userAssignedIds = usuario ? (usuario.links_bi || []).map(l => l.id_link) : [];

  allAvailableLinks.forEach(link => {
    const label = document.createElement("label");
    label.style.display = "flex";
    label.style.alignItems = "center";
    label.style.gap = "8px";
    label.style.padding = "6px 10px";
    label.style.background = "rgba(255,255,255,0.03)";
    label.style.borderRadius = "6px";
    label.style.cursor = "pointer";
    label.style.fontSize = "0.85rem";

    const isChecked = userAssignedIds.includes(link.id_link) ? "checked" : "";
    label.innerHTML = `
      <input type="checkbox" name="user_links" value="${link.id_link}" ${isChecked}>
      <span style="color: #fff; font-weight: 500;">${escaparHTML(link.nome)}</span>
    `;
    linksContainer.appendChild(label);
  });

  // Handle role change to toggle "pode_criar_link"
  roleSelect.onchange = () => {
    const val = roleSelect.value;
    // "o unico que pode receber autorizacao para criar link e o administrador"
    if (isMaster && (val === "Administrador" || val === "Master")) {
      linkPermGroup.classList.remove("hidden");
    } else {
      linkPermGroup.classList.add("hidden");
      document.getElementById("podeCriarLinkCheck").checked = false;
    }
  };

  if (usuario) {
    modalTitle.textContent = "Editar Usuário";
    document.getElementById("userIdInput").value = usuario.id_usuario;
    document.getElementById("userNameInput").value = usuario.nome_completo_usuario;
    document.getElementById("userEmailInput").value = usuario.email;
    document.getElementById("userRole").value = usuario.hierarquia;
    document.getElementById("userStatusCheck").checked = usuario.ativo;
    document.getElementById("podeCriarUsuarioCheck").checked = !!usuario.pode_criar_usuario;
    document.getElementById("podeCriarLinkCheck").checked = !!usuario.pode_criar_link;
    document.getElementById("userExpirationInput").value = usuario.data_expiracao_login || "";
  } else {
    modalTitle.textContent = "Novo Usuário";
    form.reset();
    document.getElementById("userIdInput").value = "";
    document.getElementById("userStatusCheck").checked = true;
  }

  roleSelect.onchange();
  modal.classList.remove("hidden");
}

function fecharModalUsuario() {
  document.getElementById("userModal").classList.add("hidden");
}

async function salvarUsuario(e) {
  e.preventDefault();
  const alertEl = document.getElementById("userModalAlert");
  alertEl.classList.add("hidden");

  const id = document.getElementById("userIdInput").value;
  const nome_completo_usuario = document.getElementById("userNameInput").value.trim();
  const email = document.getElementById("userEmailInput").value.trim();
  const hierarquia = document.getElementById("userRole").value;
  const ativo = document.getElementById("userStatusCheck").checked;
  const pode_criar_usuario = document.getElementById("podeCriarUsuarioCheck").checked;
  const pode_criar_link = document.getElementById("podeCriarLinkCheck").checked;
  const data_expiracao_login = document.getElementById("userExpirationInput").value || null;

  // Selected links
  const links_ids = [];
  document.querySelectorAll("input[name='user_links']:checked").forEach(cb => {
    links_ids.push(parseInt(cb.value));
  });

  const payload = {
    nome_completo_usuario,
    email,
    hierarquia,
    ativo,
    pode_criar_usuario,
    pode_criar_link,
    data_expiracao_login,
    links_ids
  };

  try {
    if (id) {
      await API.put(`/users/${id}`, payload);
      alert("Usuário atualizado com sucesso!");
    } else {
      const res = await API.post("/users", payload);
      alert(`Usuário criado com sucesso!\n\nSenha temporária inicial: ${res.user.senha_temporaria}\n\nCopie e envie ao usuário.`);
    }
    fecharModalUsuario();
    carregarUsuarios();
  } catch (err) {
    alertEl.textContent = err.message || "Erro ao salvar usuário.";
    alertEl.classList.remove("hidden");
  }
}

async function redefinirSenhaUsuario(userId, nome) {
  if (!confirm(`Deseja gerar uma nova senha temporária para ${nome}?`)) return;

  try {
    const res = await API.post(`/users/${userId}/reset-password`);
    alert(`Nova senha temporária para ${nome}:\n\n${res.senha_temporaria}\n\nO usuário deverá alterá-la no próximo acesso.`);
  } catch (err) {
    alert(err.message || "Erro ao redefinir senha.");
  }
}

// Power BI Link Creation Modal
function abrirModalLink() {
  const modal = document.getElementById("linkModal");
  const form = document.getElementById("linkForm");
  const alertEl = document.getElementById("linkModalAlert");
  form.reset();
  alertEl.classList.add("hidden");
  modal.classList.remove("hidden");
}

function fecharModalLink() {
  document.getElementById("linkModal").classList.add("hidden");
}

async function salvarLink(e) {
  e.preventDefault();
  const alertEl = document.getElementById("linkModalAlert");
  alertEl.classList.add("hidden");

  const nome = document.getElementById("linkNomeInput").value.trim();
  const link = document.getElementById("linkUrlInput").value.trim();
  const descricao = document.getElementById("linkDescInput").value.trim();

  if (!nome || !link) {
    alertEl.textContent = "Nome e link do Power BI são obrigatórios.";
    alertEl.classList.remove("hidden");
    return;
  }

  try {
    await API.post("/links", { nome, link, descricao });
    alert("Dashboard cadastrado com sucesso!");
    fecharModalLink();
    // Refresh links
    await carregarTodosLinks();
    const myLinks = await API.get("/links/my-links");
    currentDashboards = myLinks;
    renderizarDashboards(currentDashboards);
  } catch (err) {
    alertEl.textContent = err.message || "Erro ao cadastrar link.";
    alertEl.classList.remove("hidden");
  }
}

document.addEventListener("DOMContentLoaded", () => {
  const userForm = document.getElementById("userForm");
  if (userForm) userForm.addEventListener("submit", salvarUsuario);

  const linkForm = document.getElementById("linkForm");
  if (linkForm) linkForm.addEventListener("submit", salvarLink);

  const btnCloseUserModal = document.getElementById("btnCloseUserModal");
  if (btnCloseUserModal) btnCloseUserModal.addEventListener("click", fecharModalUsuario);

  const btnCloseLinkModal = document.getElementById("btnCloseLinkModal");
  if (btnCloseLinkModal) btnCloseLinkModal.addEventListener("click", fecharModalLink);
});
