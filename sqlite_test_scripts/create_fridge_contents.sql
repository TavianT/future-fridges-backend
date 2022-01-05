INSERT INTO api_fridgecontent(quantity, introduction_date,expiration_date, item_id, last_inserted_by_id)
VALUES
(24, DATE('now'), DATE('now', '14 days'), 1, 2),
(1.5,DATE('now', '-2 days') ,DATE('now', '4 days'), 2, 3),
(2.25, DATE('now'),DATE('now', '6 days'), 5, 3),
(5, DATE('now', '-3 days'), DATE('now', '-2 days'), 4, 2);