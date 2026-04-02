Feature: Product Browsing
  As a customer
  I want to browse and view product details
  So that I can make informed purchase decisions

  Background:
    Given I am on Daraz homepage

  @smoke @product
  Scenario: View product details
    When I search for "laptop"
    And I click on the first product
    Then I should see product details page
    And product name should be displayed
    And product price should be displayed

  @product @happy-path
  Scenario: Complete product browsing flow
    When I search for "smartphone"
    And I click on the first product
    Then I should see product details page
    And I take a screenshot of the product