describe('testar se o caminho de dicas funciona', ()=> {
    it('Testa se realmente da para fazer',()=> {
        cy.visit('/login')

        cy.get('.login-title').contains("Entrar")

        cy.get('input[name="email"]').type("usuario1213@gmail.com")

        cy.get('input[name="password"]').type('Senha123')

        cy.contains("button", "Entrar").click()

        cy.get('.main-title').contains("Bem-Vindo ao Aproveite +")
        
        cy.contains('a', 'Dicas').click()
    })

    })