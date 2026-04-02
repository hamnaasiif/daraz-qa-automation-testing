Feature: User Authentication and Guest Access
  As a user
  I want to access Daraz with or without login
  So that I can browse and shop

  @auth @smoke @guest
  Scenario: Guest user can browse Daraz without login
    Given I am on Daraz homepage
    Then I should see search functionality available
    And I should see product categories
    And homepage should load successfully

  @auth @login
  Scenario: User can access login page
    Given I am on Daraz homepage
    When I click on login button
    Then login modal should appear
    And I should see phone or email input field
    And I should see password input field

  @auth @login @data-driven
  Scenario Outline: Login attempt with different credentials
    Given I am on Daraz homepage
    When I click on login button
    And I enter "<email>" and "<password>"
    Then I should see "<expected_result>"

    Examples:
      | email                    | password       | expected_result  |
      | invalid@fake.com         | wrongpass123   | error_message    |
      | notregistered@test.com   | 12345678       | error_message    |
      | badformat                | pass           | error_message    |

  @auth @guest @cart
  Scenario: Guest user can view products and cart option
    Given I am on Daraz homepage
    When I search for "laptop"
    And I click on the first product
    Then I should see product details page
    And I should see add to cart button or login prompt