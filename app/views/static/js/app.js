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

  // Máscara de telefone: (11) 91234-5678
  document.querySelectorAll("[data-mascara-telefone]").forEach(function (el) {
    el.addEventListener("input", function () {
      var d = el.value.replace(/\D/g, "").slice(0, 11);
      var r = d;
      if (d.length > 2) r = "(" + d.slice(0, 2) + ") " + d.slice(2);
      if (d.length > 6) r = "(" + d.slice(0, 2) + ") " + d.slice(2, d.length - 4) + "-" + d.slice(d.length - 4);
      el.value = r;
    });
  });

  // Sugestão de horários livres no formulário de agendamento
  var form = document.getElementById("form-agendamento");
  if (form) {
    var caixa = document.getElementById("horarios");
    var lista = document.getElementById("horarios-lista");
    var campos = ["id_profissional", "id_servico", "data"].map(function (n) { return form.elements[n]; });
    var hora = form.elements["hora"];

    function atualizar() {
      var prof = campos[0].value, serv = campos[1].value, data = campos[2].value;
      if (!prof || !serv || !data) { caixa.hidden = true; return; }
      var url = form.getAttribute("data-url-horarios") + "?profissional=" + prof + "&servico=" + serv + "&data=" + data;
      fetch(url, { credentials: "same-origin" })
        .then(function (r) { return r.json(); })
        .then(function (horarios) {
          lista.innerHTML = "";
          if (!horarios.length) {
            lista.innerHTML = '<span class="sutil">Nenhum horário livre neste dia para este profissional.</span>';
          }
          horarios.forEach(function (h) {
            var b = document.createElement("button");
            b.type = "button"; b.className = "horario" + (hora.value === h ? " selecionado" : ""); b.textContent = h;
            b.addEventListener("click", function () {
              hora.value = h;
              lista.querySelectorAll(".horario").forEach(function (x) { x.classList.remove("selecionado"); });
              b.classList.add("selecionado");
            });
            lista.appendChild(b);
          });
          caixa.hidden = false;
        })
        .catch(function () { caixa.hidden = true; });
    }
    campos.forEach(function (c) { c.addEventListener("change", atualizar); });
    atualizar();
  }
})();
