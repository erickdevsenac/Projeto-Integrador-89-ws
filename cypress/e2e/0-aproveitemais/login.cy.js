describe('testa acesso da rota de /login', ()=> {
    it('Acesse rota e recebe 200', ()=> {
        cy.visit('http://localhost:9000/login')

        cy.get('.login-title').contains('Entrar')

        cy.get('input[name="email"]').type('usuario')

        cy.get('input[name="password"]').type('1A2B3C')

        
    })
})