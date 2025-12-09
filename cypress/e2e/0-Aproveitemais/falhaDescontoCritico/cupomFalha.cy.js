describe("Teste de cadastro", () => {
    it('Acessa a rota de cadastro', () => {
        cy.visit('http://localhost:9000/login')

        cy.get('input[name=email').type('tiago13@gmail.com')

        cy.get('input[name=password').type('102030Ti')

        cy.contains('button', 'Entrar').click()

        cy.get('.dropdown-toggle').click()

        cy.get('a.dropdown-item[href="/vendedor/1/"]').click()

        cy.contains('a', 'Adicionar Produto').click()

        cy.get('input[name=nome]').type('Gengibre')

        cy.get('input[name=preco]').type('50')

        cy.get('input[name=quantidade_estoque]').type('5')

        cy.get('select[id=id_tipo_quantidade]').select(1)

        cy.get('input[name=codigo_produto]').type("102030405060708090100110")

        const dia = '24';
        const mes = '08';
        const ano = '2026';
        cy.get('#id_data_validade').type(`${ano}-${mes}-${dia}`);

        cy.contains('button', 'Cadastrar Produto').click()

        cy.contains('a', 'Gengibre').click()
        
        cy.contains('button', 'Adicionar ao Carrinho').click()

        cy.contains('a', 'Finalizar Compra').click()

        cy.get('input[name=codigo]').type('PERCENTUAL')

        cy.contains('button', 'Aplicar').click()

        




        
    })
}
)

// describe("testes dando erro", () => {
//     it("Acessando a rota", () => {

//         cy.visit('http://localhost:9000/cadastro')

//         cy.get('select[name=tipo]').select('')

//         cy.get('input[name=email]').type('dsouzat25@gmail.com')

//         cy.get('input[name=senha]').type('102030Ti')

//         cy.contains('button', 'Cadastrar').click()

//         cy.get('.invalid-feedback').contains('Este campo é obrigatório.')
//     })
// })

