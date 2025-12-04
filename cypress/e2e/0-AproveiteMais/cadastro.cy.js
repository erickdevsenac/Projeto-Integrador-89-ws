describe("testando acesso da rota de /cadastro", () => {

    it("Acessa rota de cadastro e recebe 200", () => {
        cy.visit("http://localhost:9000/cadastro")

   
        cy.get('h2.card-title').contains("Crie sua Conta")

       
        cy.get('select[name="tipo"]').select("CLIENTE") 

        cy.get('input[name="email"]').type("novoUsuario3@gmail.com")

        cy.get('input[name="senha"]').type("Senha123")
        cy.get('input[name="confirmar_senha"]').type("Senha123")
        
       
        cy.contains("button", "Cadastrar").click()
        
       
        cy.url().should("include", "/login")
        cy.get(".alert").contains("Cadastro")
    })
})
