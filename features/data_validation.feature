Feature: Data Validation from Multiple Sources
  As a tester
  I want to validate product data from different sources
  So that I can ensure data consistency

  @data @excel
  Scenario: Validate product data from Excel
    Given I have product data in Excel file
    When I search for the product from Excel
    Then the product should be found in results

  @data @database
  Scenario: Validate search terms from Database
    Given I have search terms in database
    When I search using term from database
    Then I should see search results

  @data @redis
  Scenario: Validate popular searches from Redis
    Given I have popular search terms in Redis
    When I search using term from Redis
    Then search should execute successfully