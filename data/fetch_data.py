import sqlite3
from tabulate import tabulate


# 1. Connect to the database (creates the file if it doesn't exist)
conn = sqlite3.connect("data/answers.db")

# 2. Create a cursor object to execute SQL commands
#cursor = conn.cursor()


query = """
SELECT q.question,
substr((SELECT content FROM answers WHERE question = q.question AND
model = 'gpt-4o-mini' ORDER BY id DESC LIMIT 1), 1, 200) AS mini_says,
substr((SELECT content FROM answers WHERE question = q.question AND
model = 'gpt-4o' ORDER BY id DESC LIMIT 1), 1, 200) AS full_says
FROM (SELECT DISTINCT question FROM answers WHERE model IN ('gpt-4omini', 'gpt-4o')) q
ORDER BY q.question;
"""
confidencequery="""SELECT model, AVG(confidence), AVG(cost_usd) FROM answers GROUP BY model"""

#confidencequery="""SELECT model, cost_usd,created_at FROM answers where model='gpt-4o-mini'"""

# 3. Execute the SQL query
rows =conn.execute(confidencequery).fetchall()
headers=['Model', 'Avg Confidence', 'Avg Cost']
print(tabulate(rows, headers=headers, tablefmt="grid"))




# 3. Execute the SQL query
# rows =conn.execute(query).fetchall()
# headers=['question', 'mini_says', 'full_says']
# print(tabulate(rows, headers=headers, tablefmt="grid"))


# headers = [desc[0] for desc in rows.description]

# print(columns)
# print(rows)


# 5. Iterate through and process the data
# for row in rows:
#     print(row)

# 6. Close the connection when done
conn.close()