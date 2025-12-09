describe('testar se produtos com menos de 3 dias de validade conseguem desconto de mais de 25%', ()=> {
    const fakeDate = new Date(2025, 12, 11);
    it('Testa se realmente da para fazer ',()=> {
        cy.visit('/login')

        cy.get('.login-title').contains("Entrar")

        cy.get('input[name="email"]').type("vendedorprincipal@gmail.com")

        cy.get('input[name="password"]').type('Vendedor1')

        cy.contains("button", "Entrar").click()

        cy.get('.main-title').contains("Bem-Vindo ao Aproveite +")
        
        cy.get('.dropdown-toggle').click()
        
        cy.get('a.dropdown-item[href="/vendedor/82/"]').click()

        cy.contains('a', 'Adicionar Produto').click()
        
        cy.get('input[name="nome"]').type("Pão")

        cy.get('select[id = "id_categoria"]').select(1)

        cy.get('input[name="preco"]').type(10)

        cy.get('input[name="quantidade_estoque"]').type(10)
        
        cy.get('select[id = "id_tipo_quantidade"]').select(1)
        
        cy.get('input[name="codigo_produto"]').type(1012323452381)

        cy.get('input[id="id_data_validade"]').type("2025-12-11")

        cy.contains('button', 'Cadastrar Produto').click()

        cy.contains("a", "Pão").click()

        cy.contains("button", "Adicionar ao Carrinho").click()

        cy.contains("a", "Finalizar Compra").click()

        cy.get('input[name="codigo"]').type("Avaliação+25")

        cy.contains("button", "Aplicar").click()

        cy.get('.alert').contains("Cupom 'Avaliação+25' aplicado com sucesso!")

    })
})