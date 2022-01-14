

describe('Create Form', function () {

  before(() => {
    cy.fixture('accounts').then((accounts) => {
      return accounts.form_creation
    }).then(($acct) => {
      cy.login($acct)
    })
  })

  it('Creates a Form', function () {

    cy.contains('NEW')
      .should('exist')
      .click()

    cy.contains('Build from scratch')
      .should('exist')
      .click()

    cy.get('[data-cy="title"]')
      .type('Test')

    cy.get('[data-cy="description"]')
      .type('This form was created by a bot.')

    cy.get('.cy-sector')
      .should('exist')
      .click()
    cy.contains('Other')
      .click()

    cy.get('.cy-country')
      .should('exist')
      .click()
    cy.contains('United States')
      .click()


    cy.get('button[type="submit"]')
      .contains('Create project')
      .should('exist')
      .click()

    // Assert -- should not see an error
    //        -- should now be on the edit page
    cy.contains("Error:", {timeout: 2000}).should('not.exist')
    cy.url().should('include', '/edit')
  })
})
