describe("Testa acesso da rota de /login", () => {
    it("Acessa a rota e recebe 200", ()=> {
        cy.visit('http://localhost:9000/login')

        cy.get(".login-title").contains('Entrar')

        cy.get('input[type="email"]').type('tiago13@gmail.com')

        cy.get('input[type="password"]').type('102030Ti')

        cy.contains('button', 'Entrar').click()

        cy.url().should('include', '/')
    })
})