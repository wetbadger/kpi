

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

    //enter the shadow DOM
    cy.get('input[placeholder="Enter title of project here"]') //TODO: change to .get(input['data-cy="title"]')
      //.shadow() //?does not find the shadow root
      //.find('div') //?does not find div
      .type('Test')

    cy.get('textarea[placeholder="Enter short description here"]')
      .type('This form was created by a bot.')

    const selections = ['Other', 'United States']
    cy.get('div.kobo-select__value-container.css-1hwfws3') //TODO: add data attribute to dropdown selectors
      .should('have.length', 2)
      .each(($el, i) => {
        cy.wrap($el)
          .click()
        cy.contains(selections[i])
          .click()
    })

    cy.get('button[type="submit"]')
      .contains('Create project')
      .should('exist')
      .click()

    // Assert -- make an assertion
    cy.contains("Error:", {timeout: 2000}).should('not.exist')
    cy.url().should('include', '/edit')
  })
})
