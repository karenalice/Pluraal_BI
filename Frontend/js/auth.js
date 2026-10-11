// Auth Controller

document.addEventListener("DOMContentLoaded", () => {
  // Password visibility toggles
  document.querySelectorAll(".password-toggle-btn").forEach(btn => {
    btn.addEventListener("click", () => {
      const targetId = btn.getAttribute("data-target");
      const input = document.getElementById(targetId);
      if (input) {
        if (input.type === "password") {
          input.type = "text";
          btn.style.color = "var(--color-primary, #4f46e5)";
        } else {
          input.type = "password";
          btn.style.color = "";
        }
      }
    });
  });

  // Login form handler
  const loginForm = document.getElementById("loginForm");
  const loginAlert = document.getElementById("loginAlert");
  const loginSubmitBtn = document.getElementById("loginSubmitBtn");

  if (loginForm) {
    loginForm.addEventListener("submit", async (e) => {
      e.preventDefault();
      loginAlert.classList.add("hidden");
      loginAlert.textContent = "";

      const email = document.getElementById("loginEmail").value.trim();
      const password = document.getElementById("loginPassword").value;

      if (!email || !password) {
        loginAlert.textContent = "Por favor, preencha o e-mail e a senha.";
        loginAlert.classList.remove("hidden");
        return;
      }

      loginSubmitBtn.disabled = true;
      loginSubmitBtn.innerHTML = "<span>Entrando...</span>";

      try {
        const res = await API.post("/auth/login", { email, senha: password });
        API.setToken(res.token);
        API.setUser(res.usuario);

        // Check if mandatory first access password change is needed
        if (res.usuario.trocar_senha_no_primeiro_acesso) {
          document.getElementById("authView").classList.add("hidden");
          document.getElementById("passwordChangeBarrier").classList.remove("hidden");
        } else {
          // Initialize app
          window.initAppAfterLogin(res.usuario);
        }
      } catch (err) {
        loginAlert.textContent = err.message || "Erro ao realizar login.";
        loginAlert.classList.remove("hidden");
      } finally {
        loginSubmitBtn.disabled = false;
        loginSubmitBtn.innerHTML = "<span>Entrar no Sistema</span>";
      }
    });
  }

  // Mandatory Password Change Barrier handler
  const barrierForm = document.getElementById("mandatoryPasswordChangeForm");
  const barrierAlert = document.getElementById("barrierAlert");
  const barrierSubmitBtn = document.getElementById("barrierSubmitBtn");

  if (barrierForm) {
    barrierForm.addEventListener("submit", async (e) => {
      e.preventDefault();
      barrierAlert.classList.add("hidden");
      barrierAlert.textContent = "";

      const senha_atual = document.getElementById("barrierCurrentPassword").value;
      const nova_senha = document.getElementById("barrierNewPassword").value;
      const confirmacao_senha = document.getElementById("barrierConfirmPassword").value;

      if (!senha_atual || !nova_senha || !confirmacao_senha) {
        barrierAlert.textContent = "Preencha todos os campos obrigatórios.";
        barrierAlert.classList.remove("hidden");
        return;
      }

      if (nova_senha !== confirmacao_senha) {
        barrierAlert.textContent = "A nova senha e a confirmação não coincidem.";
        barrierAlert.classList.remove("hidden");
        return;
      }

      barrierSubmitBtn.disabled = true;
      barrierSubmitBtn.innerHTML = "<span>Salvando Nova Senha...</span>";

      try {
        const res = await API.post("/auth/change-password", {
          senha_atual,
          nova_senha,
          confirmacao_senha
        });

        API.setToken(res.token);
        API.setUser(res.usuario);

        document.getElementById("passwordChangeBarrier").classList.add("hidden");
        window.initAppAfterLogin(res.usuario);
      } catch (err) {
        barrierAlert.textContent = err.message || "Erro ao alterar senha.";
        barrierAlert.classList.remove("hidden");
      } finally {
        barrierSubmitBtn.disabled = false;
        barrierSubmitBtn.innerHTML = "<span>Salvar Senha e Acessar Plataforma</span>";
      }
    });
  }
});
