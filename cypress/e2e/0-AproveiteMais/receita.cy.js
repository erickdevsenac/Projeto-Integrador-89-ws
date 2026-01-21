describe("Login e criação de receita", () => {

  const email = "usuario1213@gmail.com"
  const senha = "Senha123"
  const nomeReceita = "Receita Cypress Login"

  it("Faz login e cadastra uma receita", () => {

    // =========================
    // LOGIN
    // =========================
    cy.visit("http://localhost:9000/login")
    cy.url().should("include", "/login")

    cy.get('input[name="email"]').should("be.visible").type(email)
    cy.get('input[name="password"]').should("be.visible").type(senha)

    cy.contains("button", "Entrar").should("be.visible").click()

    // =========================
    // ACESSAR RECEITAS
    // =========================
    cy.contains("a", "Receitas").should("be.visible").click()
    cy.url().should("include", "/receitas")

    // =========================
    // CRIAR RECEITA
    // =========================
    cy.contains("Cadastrar uma receita").should("be.visible").click()
    cy.url().should("include", "/receita/criar")

    cy.get('input[name="nome"]').type(nomeReceita)
    cy.get('textarea[name="descricao"]').type("Receita criada via Cypress")
    cy.get('input[name="tempo_preparo"]').type("30")
    cy.get('input[name="rendimento"]').type("4 porções")

    cy.get('select[name="categoria"]').select(0)

    cy.contains("button", "Salvar").should("be.visible").click()

    // =========================
    // VERIFICAR RECEITA
    // =========================
    cy.url().should("include", "/receitas")
    cy.contains(nomeReceita).should("be.visible")
    cy.contains("Ver Receita Completa").click()
    cy.get("h1").should("contain.text", nomeReceita)
  })
})
