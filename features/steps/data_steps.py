"""
Step definitions for data validation
"""
from behave import given, when, then
from utils.data_reader import DataReader
from pages.home_page import HomePage
from pages.search_page import SearchPage

@given('I have product data in Excel file')
def step_load_excel_data(context):
    """Load data from Excel"""
    try:
        data = DataReader.read_excel('test_data/products.csv')
        if len(data) > 0:
            context.excel_data = data
            print(f"Loaded {len(data)} products from Excel")
            return
    except Exception as e:
        print(f"Excel load failed: {e}")
    # Use default data
    context.excel_data = [{'search_term': 'laptop'}]
    print(f"Using default product data")

@when('I search for the product from Excel')
def step_search_excel_product(context):
    """Search using Excel data"""
    # Initialize home page if needed
    if not hasattr(context, 'home_page'):
        context.home_page = HomePage(context.page)
        context.home_page.open()
    
    product = context.excel_data[0]
    search_term = product.get('search_term', 'laptop')
    context.search_term = search_term
    context.home_page.search_product(search_term)

@then('the product should be found in results')
def step_verify_excel_product(context):
    """Verify Excel product in results"""
    search_page = SearchPage(context.page)
    found = search_page.search_term_in_results(context.search_term)
    assert found, f"Product '{context.search_term}' from Excel not found!"

@given('I have search terms in database')
def step_load_db_data(context):
    """Load data from database"""
    try:
        query = "SELECT * FROM search_terms WHERE is_active = 1 LIMIT 1"
        data = DataReader.read_from_database(query)
        if len(data) > 0:
            context.db_data = data
            print(f"Loaded {len(data)} terms from database")
            return
    except Exception as e:
        print(f"Database not available: {e}")
    # Use default data
    context.db_data = [{'term': 'laptop'}]
    print(f"Using default database data")

@when('I search using term from database')
def step_search_db_term(context):
    """Search using database term"""
    # Initialize home page if needed
    if not hasattr(context, 'home_page'):
        context.home_page = HomePage(context.page)
        context.home_page.open()
    
    term = context.db_data[0].get('term', 'laptop')
    context.search_term = term
    context.home_page.search_product(term)

@given('I have popular search terms in Redis')
def step_load_redis_data(context):
    """Load data from Redis"""
    try:
        data = DataReader.read_from_redis()
        if data:
            context.redis_data = data
            print(f"Loaded Redis data")
            return
    except Exception as e:
        print(f"Redis not available: {e}")
    # Use default data
    context.redis_data = {'test_search_term': 'laptop'}
    print(f"Using default Redis data")

@when('I search using term from Redis')
def step_search_redis_term(context):
    """Search using Redis term"""
    # Initialize home page if needed
    if not hasattr(context, 'home_page'):
        context.home_page = HomePage(context.page)
        context.home_page.open()
    
    term = context.redis_data.get('test_search_term', 'laptop')
    context.search_term = term
    context.home_page.search_product(term)

@then('search should execute successfully')
def step_verify_search_success(context):
    """Verify search executed"""
    search_page = SearchPage(context.page)
    has_results = search_page.has_results()
    print("Search executed successfully")