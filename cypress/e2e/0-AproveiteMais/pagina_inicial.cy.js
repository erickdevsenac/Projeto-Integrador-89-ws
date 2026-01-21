describe('Home - Aproveite +', () => {

  beforeEach(() => {
    cy.visit('http://127.0.0.1:9000/')
  })

it('Carrega o título principal', () => {
  cy.get('h1.main-title')
    .should('be.visible')
    .and('contain.text', 'Bem-Vindo ao Aproveite +')
})

  it('Exibe a seção "O que é Aproveite +"', () => {
    cy.contains('O que é Aproveite +?').should('be.visible')
    cy.contains('plataforma inovadora').should('exist')
  })

  it('Exibe os benefícios', () => {
    cy.contains('Reduza o Desperdício').should('be.visible')
    cy.contains('Apoie a Comunidade').should('be.visible')
    cy.contains('Impacto Ambiental').should('be.visible')
  })

  it('Exibe a seção de pacotes surpresa', () => {
    cy.get('#pacotes-surpresa').should('exist')
  })

  it('Se existir pacote, ele deve ter botão "Ver Detalhes"', () => {
    cy.get('body').then(($body) => {
      if ($body.find('.card').length > 0) {
        cy.get('.card').first().contains('Ver Detalhes').should('be.visible')
      } else {
        cy.contains('Nenhum pacote surpresa disponível').should('be.visible')
      }
    })
  })

  it('Botão "Comprar" redireciona corretamente', () => {
    cy.contains('Comprar').click()
    cy.url().should('include', '/produtos')
  })

})
