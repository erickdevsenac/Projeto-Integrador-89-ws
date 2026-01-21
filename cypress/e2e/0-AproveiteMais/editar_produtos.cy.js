describe('testar se o caminho de dicas funciona', ()=> {
    it('Testa se realmente da para fazer',()=> {
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
            
            cy.get('input[name="codigo_produto"]').type(10123234523912121121)

            cy.get('input[id="id_data_validade"]').type("2025-12-11")

            cy.contains('button', 'Cadastrar Produto').click()

            cy.get('.dropdown-toggle').click()
            
            cy.get('a.dropdown-item[href="/vendedor/82/"]').click()

            cy.contains('Editar').click()
        })
    })
