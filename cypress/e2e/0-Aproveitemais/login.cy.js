describe('testar acesso de rota de /login', ()=> {
    it('Acessa rota e recebe 200',()=> {
        cy.visit('http://localhost:9000/login')

        cy.get('.login-title').contains("Entrar")

        cy.get('input[name="email"]').type("usuario")

        cy.get('input[name="password"]').type('erica123')
        
        cy.get('.submit-btn').type("sumit")
        
    })
})