Finding 1 — Malformed JSON. Response codes for each of the four bad inputs; whether any reached your application code.
    # Case 1 — empty body
        Received 422 unprocessable entity error
    # Case 2 — wrong field name (typo)
        Received 422 unprocessable entity error
    # Case 3 — wrong type (int instead of str)
        Received 422 unprocessable entity error
    # Case 4 — malformed JSON (missing closing brace)
        Received 422 unprocessable entity error

• Finding 2 — 5000-character question. Total wall time observed; whether the API hit a token limit; whether streaming worked.
    API did not hit token limit and Streaming worked. Following were the final timings
        real    0m33.799s
        user    0m0.013s
        sys     0m0.007s 

• Finding 3 — Disconnect mid-stream. What the server logged on --max-time 1;whether /health still responded after.
        uvicorn log#POST /ask HTTP/1.1 200 OK
        Client#curl: (28) Operation timed out after 1000 milliseconds with 0 bytes received

• Finding 4 — 50 parallel requests. Successes out of 50; p50 / p95 latency; effective req/s;whether SQLite captured all entries.
        Total wall time:   238.75s
        Successes:         50 / 50
        Effective req/s:   0.21

        Latency (successful requests):
        min:   5.91s
        p50:   41.98s
        p95:   77.23s
        max:   83.51s

        SQLite has appears to have captured all entries.
        sqlite3 results.db "SELECT COUNT(*) FROM answers WHERE created_at >
        datetime('now', '-5 minutes');"

• Known limits/follow
    Following query referes to created_at column in the answers table which does not exist. 
    Create table script also does not have the column.

    sqlite3 results.db "SELECT COUNT(*) FROM answers WHERE created_at >
    datetime('now', '-5 minutes');"
