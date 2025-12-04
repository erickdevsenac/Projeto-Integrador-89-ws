// describe("Teste de cadastro", () => {
//     it('Acessa a rota de cadastro', () => {
//         cy.visit('http://localhost:9000/cadastro')

//         cy.get('select[name=tipo]').select('Cliente')

//         cy.get('input[name=email]').type('dsouzat18@gmail.com')

//         cy.get('input[name=senha]').type('102030Ti')

//         cy.get('input[name=confirmar_senha]').type('102030Ti')

//         cy.contains('button', 'Cadastrar').click()

//         cy.get('.alert-sucess').contains('ativação')




//     })
// }
// )

describe("testes dando erro", () => {
    it("Acessando a rota", () => {

        cy.visit('http://localhost:9000/cadastro')

        cy.get('select[name=tipo]').select('')

        cy.get('input[name=email]').type('dsouzat25@gmail.com')

        cy.get('input[name=senha]').type('102030Ti')

        cy.contains('button', 'Cadastrar').click()

        cy.get('.invalid-feedback').contains('Este campo é obrigatório.')
    })
})
