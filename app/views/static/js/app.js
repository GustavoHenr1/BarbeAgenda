// BarberAgenda — interações da interface (JavaScript puro, sem bibliotecas)
(function () {
  "use strict";

  // Confirmação antes de ações destrutivas (excluir / cancelar)
  document.addEventListener("submit", function (ev) {
    var msg = ev.target.getAttribute("data-confirmar");
    if (msg && !window.confirm(msg)) ev.preventDefault();
  });

  // Fechar mensagens
  document.addEventListener("click", function (ev) {
    if (ev.target.classList.contains("alerta-fechar")) ev.target.closest(".alerta").remove();
    if (ev.target.hasAttribute("data-toggle-menu")) document.getElementById("sidebar").classList.toggle("aberta");
  });

  // Mensagens de sucesso somem sozinhas após 5 s
  document.querySelectorAll(".alerta-sucesso").forEach(function (el) {
    setTimeout(function () { el.style.transition = "opacity .4s"; el.style.opacity = "0"; setTimeout(function () { el.remove(); }, 400); }, 5000);
  });

  // Filtros que enviam o formulário ao mudar
  document.querySelectorAll("[data-auto-submit]").forEach(function (el) {
    el.addEventListener("change", function () { el.form.submit(); });
  });

  // Máscara de telefone: (11) 1234-5678 (fixo) ou (11) 91234-5678 (celular).
  // Aceita número colado com +55 e monta a máscara de forma progressiva.
  function mascaraTelefone(valor) {
    var d = valor.replace(/\D/g, "");
    if (valor.trim().charAt(0) === "+") {          // digitando o código do país: +55
      if (d.length <= 2) return "+" + d;
      if (d.indexOf("55") === 0) d = d.slice(2);
      else return "+" + d.slice(0, 13);              // outro país: não aplica a máscara brasileira
    } else if (d.length > 11 && d.indexOf("55") === 0) {
      d = d.slice(2);                                // colou 55 + DDD + número
    }
    d = d.slice(0, 11);
    if (d.length === 0) return "";
    if (d.length <= 2) return "(" + d;
    var ddd = d.slice(0, 2), resto = d.slice(2);
    if (resto.length <= 4) return "(" + ddd + ") " + resto;
    var corte = d.length === 11 ? 5 : 4;
    return "(" + ddd + ") " + resto.slice(0, corte) + "-" + resto.slice(corte);
  }
  document.querySelectorAll("[data-mascara-telefone]").forEach(function (el) {
    el.setAttribute("maxlength", "20");
    el.setAttribute("pattern", "\\(\\d{2}\\) \\d{4,5}-\\d{4}");
    el.setAttribute("title", "Use DDD + número, ex.: (11) 91234-5678");
    el.addEventListener("input", function () { el.value = mascaraTelefone(el.value); });
    if (el.value) el.value = mascaraTelefone(el.value);
  });

  // Sugestão de horários livres no formulário de agendamento.
  // O horário digitado só é aceito se estiver na lista de horários livres.
  var form = document.getElementById("form-agendamento");
  if (form) {
    var caixa = document.getElementById("horarios");
    var lista = document.getElementById("horarios-lista");
    var aviso = document.getElementById("aviso-horario");
    var campos = ["id_profissional", "id_servico", "data"].map(function (n) { return form.elements[n]; });
    var hora = form.elements["hora"];
    // na edição, o horário atual do próprio agendamento continua válido
    var horaOriginal = form.getAttribute("data-ignorar") ? hora.value : "";
    var livres = null;

    function conferirHora() {
      var msg = "";
      if (hora.value && livres !== null && livres.indexOf(hora.value) === -1 && hora.value !== horaOriginal) {
        msg = "Este horário não está disponível. Escolha um dos horários livres abaixo.";
      }
      hora.setCustomValidity(msg);
      aviso.textContent = msg;
      aviso.hidden = !msg;
      lista.querySelectorAll(".horario").forEach(function (b) { b.classList.toggle("selecionado", b.textContent === hora.value); });
    }

    function atualizar() {
      var prof = campos[0].value, serv = campos[1].value, data = campos[2].value;
      if (!prof || !serv || !data) { caixa.hidden = true; livres = null; conferirHora(); return; }
      var url = form.getAttribute("data-url-horarios") + "?profissional=" + prof + "&servico=" + serv +
                "&data=" + data + "&ignorar=" + (form.getAttribute("data-ignorar") || "");
      fetch(url, { credentials: "same-origin" })
        .then(function (r) { return r.json(); })
        .then(function (horarios) {
          livres = horarios;
          lista.innerHTML = "";
          if (!horarios.length) {
            lista.innerHTML = '<span class="sutil">Nenhum horário livre neste dia para este profissional.</span>';
          }
          horarios.forEach(function (h) {
            var b = document.createElement("button");
            b.type = "button"; b.className = "horario"; b.textContent = h;
            b.addEventListener("click", function () { hora.value = h; conferirHora(); });
            lista.appendChild(b);
          });
          caixa.hidden = false;
          conferirHora();
        })
        .catch(function () { caixa.hidden = true; livres = null; });
    }
    campos.forEach(function (c) { c.addEventListener("change", function () { horaOriginal = ""; atualizar(); }); });
    hora.addEventListener("input", conferirHora);
    hora.addEventListener("change", conferirHora);
    atualizar();
  }
})();
