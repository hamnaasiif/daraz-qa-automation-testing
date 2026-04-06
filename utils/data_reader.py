"""
Data Reader - Read from Excel, Database, Redis
"""
import pandas as pd
import sqlite3
import json
import os

class DataReader:
    """Read test data from various sources"""
    
    @staticmethod
    def read_excel(file_path: str, sheet_name=0) -> list:
        """
        Read data from Excel file
        
        Args:
            file_path: Path to Excel file
            sheet_name: Sheet name or index
            
        Returns:
            List of dictionaries
        """
        try:
            # Try Excel first
            df = pd.read_excel(file_path, sheet_name=sheet_name)
            data = df.to_dict('records')
            print(f"Read {len(data)} rows from Excel")
            return data
        except:
            # Fallback to CSV
            try:
                df = pd.read_csv(file_path)
                data = df.to_dict('records')
                print(f"Read {len(data)} rows from CSV")
                return data
            except Exception as e:
                print(f"Error reading file: {e}")
                return []
    
    @staticmethod
    def read_from_database(query: str, db_path='db/test_data.db') -> list:
        """
        Read data from SQLite database
        
        Args:
            query: SQL query
            db_path: Database file path
            
        Returns:
            List of dictionaries
        """
        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            cursor.execute(query)
            
            # Get column names
            columns = [description[0] for description in cursor.description]
            
            # Fetch results
            rows = cursor.fetchall()
            
            # Convert to list of dicts
            data = [dict(zip(columns, row)) for row in rows]
            
            conn.close()
            print(f"Read {len(data)} rows from database")
            return data
            
        except Exception as e:
            print(f"Database error: {e}")
            return []
    
    @staticmethod
    def read_from_redis(key: str = None) -> dict:
        """
        Read data from Redis using RedisClient (falls back to JSON automatically).

        Args:
            key: Optional specific Redis key to retrieve.
                 If None, returns all available test-data keys.

        Returns:
            Dictionary of data
        """
        from utils.redis_client import get_redis_client

        try:
            rc = get_redis_client()
            if key:
                value = rc.get(key)
                print(f"Read key '{key}' from Redis")
                return {key: value} if value is not None else {}
            else:
                data = rc.get_all()
                print(f"Read {len(data)} keys from Redis")
                return data if data else {"test_search_term": "laptop"}
        except Exception as e:
            print(f"Redis read error: {e}")
            return {"test_search_term": "laptop"}