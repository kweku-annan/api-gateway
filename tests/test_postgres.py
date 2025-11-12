# import psycopg2
#
# # Connect to PostgreSQL server
# conn = psycopg2.connect(
#     host='localhost',
#     port=5432,
#     database='notification_db',
#     user="admin",
#     password="admin123"
# )
#
# cursor = conn.cursor()
#
# # Create a test table
# cursor.execute('''
#     CREATE TABLE IF NOT EXISTS test_table (
#         id SERIAL PRIMARY KEY,
#         message TEXT
#     )
# ''')
#
# # Insert data into the test table
# cursor.execute("INSERT INTO test_table (message) VALUES (%s)", ("Hello, PostgreSQL!",))
# conn.commit()
#
# # Retrieve data from the test table
# cursor.execute("SELECT * FROM test_table")
# rows = cursor.fetchall()
# print("Retrieved from PostgreSQL:", rows)
#
# cursor.close()
# conn.close()