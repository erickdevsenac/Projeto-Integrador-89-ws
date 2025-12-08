describe ("TESTAR O /cadastro",()=>{
    it("testar", ()=>{
        cy.visit("/cadastro")
        cy.get('.card-title').contains("Crie sua Conta")
        
        cy.get('#id_tipo').select(1)
        cy.get('input[name="email"] ').type("ERICA@GMAIL.COM")
        cy.get('input[name="senha"]').type('Erica1@')
        cy.get('input[name="senha"]').type('Erica1@')

    })
})