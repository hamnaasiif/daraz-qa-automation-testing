Feature: Shopping Cart and Checkout
  As a customer
  I want to add products to cart and checkout
  So that I can complete my purchase

  Background:
    Given I am on Daraz homepage

  @cart @happy-path
  Scenario: Complete purchase flow - Search to Cart
    When I search for "mobile phone"
    And I click on the first product
    Then I should see product details page
    And product price should be displayed
    And I should see add to cart button

  @cart @inventory
  Scenario Outline: Product availability check
    When I search for "<product_name>"
    And I click on the first product
    Then I should verify "<availability_status>" status
    And I should see product "<product_name>" details

    Examples:
      | product_name | availability_status |
      | laptop       | in-stock           |
      | tablet       | in-stock           |
      | smartwatch   | in-stock           |

  @cart @unhappy-path
  Scenario: Out of stock product handling
    When I search for "rare-limited-edition"
    And product appears in results
    Then I should see either in stock or out of stock status
    And out of stock products should show proper message

  @cart @error-handling
  Scenario: Graceful handling of network issues
    Given I am viewing product details
    When network connectivity is degraded
    Then page should remain functional
    And I should see cached product information
    And error message should be user-friendly
