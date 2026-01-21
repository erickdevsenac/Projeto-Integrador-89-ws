describe('testar se o caminho de videos funciona', ()=> {
    it('Testa se realmente da para fazer',()=> {
        cy.visit('/login')

        cy.get('.login-title').contains("Entrar")

        cy.get('input[name="email"]').type("vendedorprincipal@gmail.com")

        cy.get('input[name="password"]').type('Vendedor1')

        cy.contains("button", "Entrar").click()

        cy.get('.main-title').contains("Bem-Vindo ao Aproveite +")
        
        cy.contains('a', 'Videos').click()
    })

    })