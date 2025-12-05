describe('Testa acesso da rota de /login', () => {
    it('Acessa rota e recebe 200', ()=> {
        cy.visit('http://localhost:9000/login')

        cy.get('.login-title').contains('Entrar')

        cy.get('input[name="email"]').type('vendedor@email.com')
        cy.get('input[name="password"]').type('1A2b3c')

        cy.contains('button', 'Entrar').click()

        cy.url().should('include', '/')
    })
})