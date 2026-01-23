describe("Perfil do Usuário", () => {
  const email = "usuario1213@gmail.com";
  const senha = "Senha123";

  beforeEach(() => {

    cy.visit("http://localhost:9000/login");
    cy.get('input[name="email"]').type(email);
    cy.get('input[name="password"]').type(senha);
    cy.contains("button", "Entrar").click();

    cy.visit("http://localhost:9000/perfil");
  });

  it("Deve abrir modo de edição e preencher telefone e CNPJ", () => {
   
    cy.get("#edit-profile-btn").should("be.visible").click();

    cy.get("#edit-mode form").should("be.visible");

    cy.get('#id_telefone:visible').clear().type("(11) 91234-5678");
    cy.get('#id_cep:visible').clear().type("12345-678");


    cy.get("#edit-mode button[type='submit']").click();

    cy.get("#view-mode").should("be.visible");
  });
});
