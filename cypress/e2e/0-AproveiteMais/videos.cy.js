describe("Página de Vídeos", () => {
  beforeEach(() => {
    cy.visit("http://localhost:9000/videos") // ajuste a URL
  })

  it("Deve carregar a página e mostrar a primeira categoria (Pães)", () => {
    cy.get(".categories").should("be.visible")
    cy.get(".category-btn.active").contains("Pães")
    cy.get("#bread").should("be.visible")
    cy.get("#bread .video").should("have.length.greaterThan", 0)
  })

  it("Deve alternar categorias corretamente", () => {
    // Bolos
    cy.contains(".category-btn", "Bolos").click().should("have.class", "active")
    cy.get("#cake").should("be.visible")
    cy.get("#bread").should("not.be.visible")

    // Sobremesas
    cy.contains(".category-btn", "Sobremesas").click().should("have.class", "active")
    cy.get("#dessert").should("be.visible")
    cy.get("#cake").should("not.be.visible")

    // Salgados
    cy.contains(".category-btn", "Salgados").click().should("have.class", "active")
    cy.get("#savory").should("be.visible")
    cy.get("#dessert").should("not.be.visible")
  })

  it("Cada vídeo deve ter iframe do YouTube", () => {
    cy.get(".video-group").each(($group) => {
      cy.wrap($group).find(".video").each(($video) => {
        cy.wrap($video)
          .find("iframe")
          .should("have.attr", "src")
          .and("include", "youtube.com/embed")
      })
    })
  })
})
