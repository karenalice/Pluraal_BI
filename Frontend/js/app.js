// Main Application Orchestrator

async function initApp() {
  const token = API.getToken();
  if (!token) {
    mostrarTelaLogin();
    return;
  }

  try {
    const user = await API.get("/auth/me");
    API.setUser(user);

    if (user.trocar_senha_no_primeiro_acesso) {
      document.getElementById("authView").classList.add("hidden");
      document.getElementById("passwordChangeBarrier").classList.remove("hidden");
    } else {
      window.initAppAfterLogin(user);
    }
  } catch (err) {
    console.warn("Sessão inválida:", err);
    API.clearSession();
    mostrarTelaLogin();
  }
}

function mostrarTelaLogin() {
  document.getElementById("authView").classList.remove("hidden");
  document.getElementById("appContainer").classList.add("hidden");
  document.getElementById("passwordChangeBarrier").classList.add("hidden");
  document.getElementById("biView").classList.add("hidden");
}

window.initAppAfterLogin = async function(user) {
  // Hide Auth screens and show App Container
  document.getElementById("authView").classList.add("hidden");
  document.getElementById("passwordChangeBarrier").classList.add("hidden");
  document.getElementById("appContainer").classList.remove("hidden");

  // Configure User Profile in Header
  document.getElementById("navUserName").textContent = user.nome_completo_usuario || user.email;
  document.getElementById("navUserRole").textContent = user.hierarquia || "Acesso";
  const initials = (user.nome_completo_usuario || "U")
    .split(" ")
    .map(p => p[0])
    .slice(0, 2)
    .join("")
    .toUpperCase();
  document.getElementById("navUserAvatar").textContent = initials;

  // Management controls based on user role
  const isMaster = user.hierarquia === "Master";
  const canManageUsers = isMaster || user.pode_criar_usuario;
  const canCreateLinks = isMaster || user.pode_criar_link;

  const btnUsersNav = document.getElementById("btnUsersNav");
  const btnNewLink = document.getElementById("btnNewLink");

  if (canManageUsers) {
    btnUsersNav.classList.remove("hidden");
  } else {
    btnUsersNav.classList.add("hidden");
  }

  if (canCreateLinks) {
    btnNewLink.classList.remove("hidden");
  } else {
    btnNewLink.classList.add("hidden");
  }

  // Pre-load all links if manager
  if (canManageUsers || canCreateLinks) {
    await carregarTodosLinks();
  }

  // Fetch this user's assigned links
  try {
    const links = await API.get("/links/my-links");
    currentDashboards = links || [];

    // CRITICAL USER REQUIREMENT:
    // "se o usuario so tiver 1 bi apenas abra o bi não precisa ter home, se tiver mais de mostrar um home com as opções de links"
    if (currentDashboards.length === 1 && !isMaster && !canManageUsers) {
      // Direct open! No home needed!
      document.getElementById("hubView").classList.add("hidden");
      document.getElementById("usersView").classList.add("hidden");
      abrirDashboard(currentDashboards[0]);
    } else {
      // Show Home Hub with cards and search
      document.getElementById("hubView").classList.remove("hidden");
      document.getElementById("usersView").classList.add("hidden");
      document.getElementById("biView").classList.add("hidden");
      renderizarDashboards(currentDashboards);
    }
  } catch (err) {
    console.error("Erro ao carregar dashboards:", err);
  }
};

// Navigation Tab Switches
document.addEventListener("DOMContentLoaded", () => {
  const btnDashboardsNav = document.getElementById("btnDashboardsNav");
  const btnUsersNav = document.getElementById("btnUsersNav");
  const btnNewLink = document.getElementById("btnNewLink");
  const btnNewUser = document.getElementById("btnNewUser");
  const btnLogout = document.getElementById("btnLogout");
  const btnViewerLogout = document.getElementById("btnViewerLogout");

  if (btnDashboardsNav) {
    btnDashboardsNav.addEventListener("click", () => {
      btnDashboardsNav.classList.add("active");
      btnUsersNav.classList.remove("active");
      document.getElementById("hubView").classList.remove("hidden");
      document.getElementById("usersView").classList.add("hidden");
      document.getElementById("biView").classList.add("hidden");
    });
  }

  if (btnUsersNav) {
    btnUsersNav.addEventListener("click", () => {
      btnUsersNav.classList.add("active");
      btnDashboardsNav.classList.remove("active");
      document.getElementById("usersView").classList.remove("hidden");
      document.getElementById("hubView").classList.add("hidden");
      document.getElementById("biView").classList.add("hidden");
      carregarUsuarios();
    });
  }

  if (btnNewLink) {
    btnNewLink.addEventListener("click", abrirModalLink);
  }

  if (btnNewUser) {
    btnNewUser.addEventListener("click", () => abrirModalUsuario(null));
  }

  const handleLogout = async () => {
    try {
      await API.post("/auth/logout");
    } catch {}
    API.clearSession();
    window.location.reload();
  };

  if (btnLogout) btnLogout.addEventListener("click", handleLogout);
  if (btnViewerLogout) btnViewerLogout.addEventListener("click", handleLogout);

  // Initial application startup
  initApp();
});
