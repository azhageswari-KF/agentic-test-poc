Feature: Booking form functionality on Dream Journey travel site

  Background:
    * driver target_url

  @integration @guest @web
  Scenario: Verify successful booking form submission with all required and optional fields displays 'Success' confirmation
    Given driver target_url
    And input('input[name=name]', 'Test Traveler')
    And input('input[name=number]', '9876543210')
    And input('input[name=place]', 'Place 1')
    And input('input[name=people]', '2')
    And input('input[name=address]', '12 Test Street, Chennai')
    When click('button[type=submit]')
    Then waitFor('text=Success')

  @component @guest @web
  Scenario: Verify clicking 'Book Now' button scrolls the page to the booking section
    Given driver target_url
    When click('{a}Book Now')
    Then waitFor('input[name=name]')

  @component @guest @web @negative
  Scenario: Verify submitting the booking form with empty required fields (name, number, place, address) does not display 'Success'
    Given driver target_url
    When click('button[type=submit]')
    Then match text('text=Success') == '#notpresent'

  @regression @guest @mobile
  Scenario: Verify booking form UI layout and submission functionality on mobile browsers
    Given configure driver = { type: 'chrome', emulateDevice: 'iPhone X' }
    And driver target_url
    When click('{a}Book Now')
    And waitFor('input[name=name]')
    And input('input[name=name]', 'Mobile Traveler')
    And input('input[name=number]', '9876543210')
    And input('input[name=place]', 'Mobile Place')
    And input('input[name=people]', '1')
    And input('input[name=address]', '45 Mobile Road')
    And click('button[type=submit]')
    Then waitFor('text=Success')