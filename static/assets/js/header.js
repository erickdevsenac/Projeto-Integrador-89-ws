document.addEventListener("DOMContentLoaded", function () {
  const searchForm = document.querySelector(".search-form");
  const toggleBtn = document.querySelector(".search-toggle");
  const searchInput = document.querySelector(".search-input");

  toggleBtn.addEventListener("click", () => {
    // Alterna a classe active para mostrar/esconder o campo
    searchForm.classList.toggle("active");

    if (searchForm.classList.contains("active")) {
      searchInput.focus();
    } else {
      searchInput.value = "";
    }
  });

  // Opcional: esconde campo ao clicar fora
  document.addEventListener("click", (e) => {
    if (
      !searchForm.contains(e.target) &&
      searchForm.classList.contains("active")
    ) {
      searchForm.classList.remove("active");
      searchInput.value = "";
    }
  });
});
