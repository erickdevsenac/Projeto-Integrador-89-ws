describe('Funcionalidade de Cadastro de Usuário no Aproveite+', () => {
    
    const EMAIL_ALEATORIO = `teste-${Date.now()}@exemplo.com`;
    const SENHA_FORTE = 'Senha123!'; 
    
    const CADASTRO_PATH = '/cadastro/'; 

    it('Caminho Feliz: Deve criar uma nova conta com sucesso e exibir mensagem de sucesso e envio para email', () => {
        
        // ARRANGE (Preparar o cenário)
        cy.visit(CADASTRO_PATH); 
        
        // ACT (Agir)
        cy.get('#id_tipo').select(1); 

        cy.get('#id_email').type(EMAIL_ALEATORIO); 

        cy.get('#id_senha').type(SENHA_FORTE);
        cy.get('#id_confirmar_senha').type(SENHA_FORTE);
        
        cy.get('.btn-success').contains('Cadastrar').click(); 
        
        // ASSERT (Verificar)
        cy.url().should('include', '/telalogin');
        
        cy.get('.alert-success').should('be.visible').and('contain', 'Conta criada com sucesso');
    });


    it('Caminho Infeliz: Deve impedir o cadastro com senhas não correspondentes', () => {
        
        // ARRANGE
        cy.visit(CADASTRO_PATH); 
        cy.get('#id_tipo').select(1);
        
        // ACT (Ação de Falha)
        cy.get('#id_senha').type('Senha123!');
        cy.get('#id_confirmar_senha').type('SenhaDIFERENTE!'); 

        cy.get('.btn-success').contains('Cadastrar').click(); 
        
        // ASSERT (Verificação da Falha)
        cy.url().should('include', CADASTRO_PATH);
        
        cy.get('.invalid-feedback.d-block').should('be.visible').and('contain', 'As senhas não conferem');
        
        cy.get('#id_email').should('have.value', ''); 
    });
});