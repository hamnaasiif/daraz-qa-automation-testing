Feature: Product Search Functionality
  As a customer
  I want to search for products on Daraz
  So that I can find items I want to buy

  Background:
    Given I am on Daraz homepage

  @smoke @search
  Scenario: Search for a product successfully
    When I search for "laptop"
    Then I should see search results
    And search results should contain "laptop"

  @search @data-driven
  Scenario Outline: Search with multiple keywords
    When I search for "<search_term>"
    Then I should see search results
    And search results should contain "<search_term>"

    Examples:
      | search_term |
      | laptop      |
      | mobile      |
      | headphones  |

  @negative @search
  Scenario: Search with invalid term shows no results
    When I search for "xyzinvalidproduct99999"
    Then I should see no results message