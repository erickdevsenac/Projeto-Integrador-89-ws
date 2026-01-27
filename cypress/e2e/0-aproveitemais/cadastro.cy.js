describe('testa acesso da rota de /login', ()=> {
    it('Acesse rota e recebe 200', ()=> {
        cy.visit('http://localhost:9000/cadastro')

        cy.get('.card-title').contains('Crie sua Conta')

        cy.get('#id_tipo').select(1)

        cy.get('input[name="email"]').type('nome@gmail.com')
    })
})        