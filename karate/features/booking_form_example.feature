Feature: Booking form on Dream Journey travel site
  # Seed pattern for the Creator agent to extend. Selectors below are
  # illustrative -- confirm the real ones against the live DOM (browser
  # devtools) before relying on this in CI; the sample page markup wasn't
  # inspected at the CSS-selector level for this POC.

  Background:
    * driver target_url

  @component @guest @web
  Scenario: Guest submits a fully completed booking form
    Given driver target_url
    And input('input[name=name]', 'Test Traveler')
    And input('input[name=number]', '9876543210')
    And input('input[name=place]', 'Place 1')
    And input('input[name=people]', '2')
    And input('input[name=address]', '12 Test Street, Chennai')
    When click('button[type=submit]')
    Then waitFor('text=Success')

  @component @guest @web @negative
  Scenario: Guest cannot submit the booking form with required fields empty
    Given driver target_url
    When click('button[type=submit]')
    Then match text('text=Success') == '#notpresent'
